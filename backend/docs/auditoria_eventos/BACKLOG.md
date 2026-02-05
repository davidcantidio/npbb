# Auditoria Eventos - Backlog

## Resumo executivo (10 linhas)
- Modulo de eventos e o eixo central do backend: CRUD, dicionarios, import/export CSV e submodulos (formulario, questionario, gamificacao, ativacao).
- A camada de rotas e densa e monolitica, o que aumenta risco de regressao e dificulta manutencao.
- A visibilidade por agencia existe, mas o restante dos perfis ve todos os eventos; pode ser requisito, mas e risco de exposicao se nao for intencional.
- Importacao CSV de eventos processa arquivo inteiro em memoria e faz matching por linha com consultas repetidas.
- Filtros usados no listing/export (diretoria/status/tipo/subtipo/datas) nao tem indices declarados; risco de scan em crescimento de dados.
- Data health depende de config em `docs/` com fallback silencioso; pode divergir entre ambientes.
- Status do evento e inferido via nomes hard-coded; se base nao estiver seedada, cria evento com erro 500.
- Tests cobrem boa parte do CRUD, mas ha lacunas de contrato para alguns endpoints secundarios.
- Ha duplicacao de regras de visibilidade entre routers relacionados (ativacao/gamificacao/eventos).
- Nao foi encontrado uso de PII em logs de eventos (logs ja sanitizados no import).

## Backlog priorizado

### [P1] Visibilidade de eventos por matriz de permissões (NPBB / BB / Agência)

* **Impacto:** alto (exposição indevida de eventos entre diretorias/agências).
* **Probabilidade:** média (hoje “default = vê tudo” para tipos não-AGENCIA).
* **Esforço:** M.
* **Evidência:** `app/routers/eventos.py:114-124` (`_apply_visibility` filtra apenas `UsuarioTipo.AGENCIA`; demais tipos não têm restrição e acabam vendo tudo).
* **Matriz de permissões (regra de negócio definida):**

  * **NPBB:** vê tudo.
  * **BB (@bb.com.br):** vê **apenas** eventos da **diretoria** do usuário.
  * **AGENCIA:** vê **apenas** eventos atribuídos à sua **agência**.
* **Recomendação (implementação):**

  1. **Centralizar regra** em um único lugar (ex: `app/services/eventos_visibility.py` ou `app/utils/permissions.py`), com função pura tipo:

     * `apply_event_visibility(query, usuario) -> query`
  2. **Determinar “role” do usuário** de forma determinística:

     * `is_npbb_user(usuario)` (ex: domínio não-bb OU flag/tipo específico NPBB no model)
     * `is_bb_user(usuario)` (email `@bb.com.br` + matrícula) e **diretoria_id** (ou campo equivalente) obrigatório
     * `is_agencia_user(usuario)` (UsuarioTipo.AGENCIA + agencia_id obrigatório)
  3. **Aplicar o filtro em TODOS os endpoints** do módulo eventos (listagem, detalhar por id, dashboards relacionados a evento, etc.), não só no list:

     * List: filtrar no SELECT
     * Detail: ao buscar por id, garantir que o evento também respeita a visibilidade (senão retornar **404** para não vazar existência; 403 só se a política do produto pedir explícito).
  4. **Garantir integridade do modelo** (se faltar campo):

     * Usuário BB sem `diretoria_id` → tratar como configuração inválida: negar acesso (403) e log interno (sem PII).
     * Agência sem `agencia_id` → idem.
  5. **Auditar “evento atribuível”**: confirmar em model qual coluna indica vínculo:

     * ex: `Evento.agencia_id`, `Evento.diretoria_id` (ou tabela de associação). Se não existir, criar item P1 dependente: “modelar vínculo evento↔diretoria/agência”.
* **Critério de aceite:**

  * Matriz documentada em `docs/auditoria_eventos/` (ou docs do módulo).
  * Testes cobrindo:

    * NPBB lista e detalha qualquer evento.
    * BB vê só eventos da própria diretoria (lista e detalhe).
    * Agência vê só eventos atribuídos à sua agência (lista e detalhe).
    * Usuário tentando acessar evento fora do escopo → **404** (ou 403, se decidido) consistente.
* **Dependências/risco:**

  * Exige que existam (ou sejam criados) campos confiáveis:

    * `usuario.diretoria_id` (BB), `usuario.agencia_id` (Agência), e equivalentes em `Evento`.
  * Decisão final: **404 vs 403** para acesso negado (evitar enumeração normalmente favorece 404).
  * Se a classificação “NPBB” não for explícita no model, precisa definir o critério (tipo/perfil/flag), senão vira gambiarra por domínio.


Sim, pode trazer ganho **bem real** (segurança + estabilidade + performance). Do jeito que está, é “me mande um CSV gigante e eu derrubo teu worker”.

Aqui vai o detalhamento do item já no formato de backlog, com *por que vale* e como fazer direito:

### [P1] Importação CSV de eventos carrega o arquivo inteiro em memória

* **Ganha algo?** Sim:

  * **Evita DoS acidental ou malicioso** (arquivo grande = RAM explode).
  * **Reduz latência**: começa a processar enquanto lê (streaming), sem esperar carregar tudo.
  * **Melhora previsibilidade**: limite claro de tamanho + limite de linhas.
  * **Abre espaço pra UX melhor**: reportar erros por linha sem travar o servidor.

* **Impacto:** médio/alto (instabilidade/queda do serviço em input grande).

* **Probabilidade:** média (import é lugar clássico de “alguém jogou um CSV de 2GB sem querer”).

* **Esforço:** M.

* **Evidência:** `app/routers/eventos.py:758-772`

  * `file.file.read()` carrega tudo.
  * `rows = list(csv.reader(...))` duplica a pancada.

* **Recomendação (implementação):**

  1. **Validação de tamanho antes de processar**

     * Preferir checar `Content-Length` quando disponível.
     * Se não disponível (upload chunked), aplicar **contador de bytes** enquanto lê.
     * Definir `MAX_CSV_BYTES` (config/env) e rejeitar acima do limite com 413/400.
  2. **Streaming de CSV**

     * Não usar `read()` nem `list(...)`.
     * Iterar linha a linha usando um wrapper de texto:

       * `io.TextIOWrapper(file.file, encoding="utf-8", newline="")`
       * `csv.DictReader(...)` (melhor pra mapear colunas com nome).
     * Processar em loop:

       * validar header
       * para cada linha: validar, normalizar, acumular erros
  3. **Limites defensivos adicionais**

     * `MAX_ROWS` (ex: 100k) para evitar “CSV infinito”.
     * `MAX_ERRORS` (ex: 500) para parar cedo se o arquivo é lixo.
     * opcional: limite de tempo por import (se for sync).
  4. **Batch insert / transação**

     * Se hoje faz insert por linha, é lento.
     * Inserir em lotes (ex: 500/1000) pra reduzir overhead.
     * Estratégia de falha:

       * ou “tudo ou nada” (transação)
       * ou “melhor esforço” com relatório de erros (mais comum em import)
     * Registrar isso na doc do endpoint.
  5. **Erros e logging**

     * Retornar erros por linha **sem PII** (se houver dados sensíveis).
     * Logar apenas contadores + linha atual + tipo de erro.
  6. **Compatibilidade**

     * Manter o contrato do endpoint (payload/response) igual, só mudar o motor.
     * Se precisar mudar, versionar ou documentar.

* **Critério de aceite:**

  * Import rejeita arquivo acima de `MAX_CSV_BYTES` com erro claro.
  * Processa CSV **sem** `read()` e **sem** `list(csv.reader(...))`.
  * Memória não cresce proporcional ao tamanho do arquivo (verificado por inspeção e/ou teste).
  * Testes cobrindo:

    1. arquivo pequeno válido -> sucesso
    2. arquivo > limite -> rejeitado
    3. muitas linhas -> respeita `MAX_ROWS`
    4. CSV inválido -> erros por linha (limitados por `MAX_ERRORS`)

* **Dependências/risco:**

  * Definir limite máximo (produto/ops). **Sugestão pragmática**:

    * `MAX_CSV_BYTES`: 5–20 MB (começa em 10 MB) e ajusta depois.
    * `MAX_ROWS`: 50k–200k dependendo do hardware.
  * Se o endpoint roda síncrono no request, arquivos grandes ainda vão demorar; se isso for comum, melhor mover pra **job assíncrono** (P2/P1 dependendo do uso).




Sim, **vale muito** — e geralmente dá ganho “barato” quando o volume cresce. Lista/export sem índice vira triturador de CPU + I/O.

Abaixo vai o detalhamento (já com um plano de migração que não derruba produção) e critérios mais objetivos.

---

### [P1] Filtros críticos de eventos sem índices dedicados

* **Ganha algo?** Sim:

  * **Melhora tempo de listagem/export** quando tabela cresce (principalmente filtros + ordenação/paginação).
  * **Reduz lock/impacto** em banco (menos full scan = menos I/O).
  * **Evita regressão silenciosa**: hoje funciona “rápido” só porque o volume ainda não bateu.

* **Impacto:** médio/alto (degradação de performance em lista/export, timeouts e custos de DB).

* **Probabilidade:** média (depende do volume; export costuma doer primeiro).

* **Esforço:** M (migrações + validação).

* **Evidência:**

  * Filtros usados: `app/routers/eventos.py:174-203` (diretoria_id + datas).
  * Modelo com índices apenas em cidade/estado: `app/models/models.py:211-213`.

* **Recomendação (implementação técnica):**

  1. **Inventariar queries reais**

     * Identificar exatamente:

       * quais colunas entram no `WHERE` mais frequente (diretoria_id, status_id, tipo_id, subtipo_id, datas)
       * qual a ordenação padrão (ex: `ORDER BY data_inicio DESC` ou `created_at DESC`)
       * se há paginação com `OFFSET/LIMIT` (impacta índice útil)
     * Se houver query de export diferente (sem paginação), considerar índices específicos.
  2. **Adicionar índices “bons o bastante” (mínimo inicial)**

     * Índices simples (quase sempre úteis):

       * `evento(diretoria_id)`
       * `evento(status_id)`
       * `evento(tipo_id)`
       * `evento(subtipo_id)`
       * índice em coluna(s) de data filtradas (ex: `data_inicio`, `data_fim`, `created_at` — usar as que realmente aparecem no `WHERE`)
     * Se os filtros aparecem combinados com data (muito comum), considere **índices compostos**:

       * Exemplo comum: `WHERE diretoria_id=? AND data_inicio BETWEEN ? AND ?`

         * índice composto: `(diretoria_id, data_inicio)`
       * Se também filtra por status:

         * `(diretoria_id, status_id, data_inicio)`
     * Regra prática: **não crie 10 compostos de uma vez**. Comece pelo composto mais frequente e pelos simples.
  3. **Nomear índices com convenção**

     * Evitar nomes aleatórios de Alembic.
     * Ex: `ix_evento_diretoria_id`, `ix_evento_diretoria_data_inicio`.
     * (Se o projeto ainda não tem naming_convention, isso pode ser item acoplado ao P1/P2 de migrações.)
  4. **Migração segura**

     * Se Postgres:

       * preferir `CREATE INDEX CONCURRENTLY` para não travar escrita (mas cuidado: Alembic precisa de `op.execute` e `transaction_per_migration = False`/autocommit).
     * Se não der para concurrent:

       * planejar janela de manutenção ou aplicar em horário de baixo uso.
  5. **Verificar impacto**

     * Rodar `EXPLAIN (ANALYZE, BUFFERS)` antes/depois para a query de listagem e a query de export.
     * Se não puder rodar ANALYZE, pelo menos `EXPLAIN` para ver se sai de `Seq Scan` para `Index Scan/Bitmap Index Scan`.
  6. **Observação de “índice só por coluna” vs composto**

     * Se o planner usar `BitmapAnd` combinando índices simples, pode ser suficiente.
     * Se ainda ficar pesado, aí sim entrar com composto.

* **Critério de aceite (mais objetivo):**

  1. Migração cria os índices definidos (com nomes claros).
  2. Para a query principal de listagem (com diretoria + intervalo de datas):

     * `EXPLAIN` não mostra `Seq Scan` na tabela de eventos (ou reduz drasticamente rows examined).
  3. Para export:

     * redução de custo estimado e/ou tempo (quando medível).
  4. Testes/migrations ok:

     * `alembic upgrade head` funciona.
     * downgrade (se suportado) remove índices.

* **Dependências/risco:**

  * **Banco e carga**: criar índice em tabela grande pode demorar e consumir I/O.
  * Precisar confirmar:

    * qual SGBD (provavelmente Postgres pelo psycopg2)
    * volume estimado (linhas em eventos)
  * Se a tabela for enorme, o “CONCURRENTLY” vira quase obrigatório.

* **Sugestão de pacote inicial (se você quiser fechar escopo sem discussão):**

  * Índices simples: diretoria_id, status_id, tipo_id, subtipo_id
  * Índice composto: (diretoria_id, data_inicio) OU (diretoria_id, created_at) — escolher baseado no filtro/ordenação real do router.


Dá pra ganhar, sim — principalmente quando o import cresce. Hoje você está pagando **N linhas × (buscar candidatos + fazer score em Python)**. Isso escala mal e ainda cria “surpresas” de performance.

Aqui vai o detalhamento do item, com um caminho de implementação que não muda a regra de negócio “na raça”.

---

### [P2] Matching de eventos no import CSV faz scoring em Python por linha

* **Ganha algo?**

  * **Menos tempo por linha** (reduz I/O e CPU no app).
  * **Menos memória** (não precisa trazer “todos candidatos”).
  * **Mais previsível** (o banco faz o ranking e devolve 1).
  * **Menos bugs “edge”** (centraliza critério no SQL, facilita testar).

* **Impacto:** médio (tempo alto em import com muitos eventos).

* **Probabilidade:** média (piora conforme volume de eventos/imports).

* **Esforço:** M (query + testes + possível ajuste de índices).

* **Evidência:**

  * `app/routers/eventos.py:517-558` busca candidatos e calcula overlap em Python.
  * `app/routers/eventos.py:824-835` usa isso por linha no import.

---

## Recomendações (com plano incremental e seguro)

### 1) Fix imediato (barato) sem SQL fancy: reduzir candidato + cache

Antes de mexer em SQL:

* **Cache em memória por import**: se a mesma chave de matching se repete (ex: (diretoria_id, cidade, data)), cacheia o resultado e evita recomputar.
* **Pré-filtrar mais agressivo no SQL**: traga candidatos já “próximos”:

  * por `diretoria_id`
  * por intervalo de datas (ex: ±7 dias)
  * por cidade/estado se existirem
  * por tipo/subtipo se existirem
* **Limitar candidatos**: `LIMIT 50/100` com uma ordenação simples (data mais próxima, status ativo, etc.) antes de fazer o scoring Python.
  Isso sozinho às vezes corta 10x do custo.

> Se isso não bastar, aí sim parte pra “ranking no banco”.

### 2) Mover ranking pro SQL (alvo do item)

A ideia é: **o banco calcula o score e devolve só 1 linha**.

**Como fazer depende do que é “overlap”:**

* Se overlap é de **intervalo de datas** (ex: `data_inicio`/`data_fim`):

  * Postgres tem operadores e funções boas:

    * `GREATEST(0, LEAST(a_fim,b_fim) - GREATEST(a_ini,b_ini))` para duração de sobreposição
    * ou usar `tsrange/daterange` + operador `&&` e `upper/lower`
* Se overlap inclui **campos textuais** (nome do evento, local), dá pra:

  * começar simples: score por igualdade/prefixo/ILIKE
  * opcional futuro: trigram (`pg_trgm`) ou full text — mas isso já é P2/P1 dependendo do caso.

**Exemplo de estratégia de score (sem mudar regra de negócio):**

* `score = overlap_dias * 100`
* * bônus se cidade/estado bater
* * bônus se tipo/subtipo bater
* * penalidade por distância de datas (se for parte da regra)
    E ordenar:
* `ORDER BY score DESC, data_inicio DESC, id ASC LIMIT 1`

### 3) Índices para sustentar a query

Se você filtra por `diretoria_id` e datas:

* índice composto ajuda: `(diretoria_id, data_inicio)` (ou data_fim dependendo do filtro)
* e os simples já citados: `status_id`, `tipo_id`, etc.

### 4) Garantir “mesma regra” (não quebrar negócio)

* **Congelar a regra atual** em testes:

  1. Monte um conjunto de eventos candidatos + input de linha CSV.
  2. Rode o matcher atual (Python) e registre o evento escolhido.
  3. Rode o matcher novo (SQL) e verifique que escolhe o mesmo.
* Se der diferença, documente e decida:

  * ou ajustar score SQL para ficar equivalente
  * ou aceitar mudança se for melhoria (mas isso é decisão do produto/negócio).

---

## Critério de aceite (mais robusto)

1. O matching por linha faz **uma query que retorna 1 evento** (`LIMIT 1`) — sem puxar lista grande.
2. Em um dataset grande (ex: milhares de eventos + milhares de linhas):

   * tempo total de import cai (registre tempo antes/depois).
3. Testes:

   * “equivalência” com a regra antiga em pelo menos N casos (ex: 10 cenários cobrindo edge cases).
4. Logs:

   * não logar payload sensível; logar só métricas (tempo, número de linhas, hits/misses no cache).

---

## Dependências/risco

* Precisa confirmar DB (parece Postgres). Se for SQLite, alguns recursos de range/intervalo não existem.
* Se overlap é mais complexo (ex: lista de sessões, tags), talvez precise tabela normalizada ou pré-computo.
* Migrar para trigram/FTS é trabalho extra (não obrigatório pra primeira versão).

---


Boa. Isso **pode sim trazer ganho** — não em “performance”, mas em **confiabilidade** e **reprodutibilidade** (e isso economiza horas de caça a bug “só acontece em prod”).

Aqui vai o detalhamento do item (com um caminho prático e sem drama):

---

### [P2] Config de saúde de dados do evento vive em `docs/` com fallback silencioso

* **Ganha algo?** Sim:

  * **Consistência entre ambientes**: dev/stage/prod deixam de “rodar cada um com uma config”.
  * **Menos divergência silenciosa**: hoje pode estar usando `DEFAULT_CONFIG` sem ninguém perceber.
  * **Deploy mais previsível**: config vira artefato de runtime (ou env) e entra no pacote.
  * **Observabilidade**: warning/erro quando cair em fallback reduz tempo de debug.

* **Impacto:** médio (métricas/alertas podem divergir sem sinal).

* **Probabilidade:** média (docs/ não costuma ir completo em deploy, ou path muda).

* **Esforço:** P/M.

* **Evidência:** `app/services/data_health.py:62-66`

  * carrega `docs/eventos_saude_dados_config.json`
  * fallback para `DEFAULT_CONFIG` sem barulho.

* **Recomendação (implementação):**

  1. **Mover para local de runtime** (dentro do pacote do app)

     * Ex: `app/config/eventos_saude_dados_config.json`
     * Alternativa: `app/resources/` ou `app/data/` (o nome tanto faz, desde que seja “runtime” e versionado).
  2. **Tornar o caminho configurável por env**

     * `EVENT_DATA_HEALTH_CONFIG_PATH` (opcional)
     * Se setado: carrega esse path (bom para override em prod).
     * Se não: carrega o default do pacote (`app/config/...`).
  3. **Fallback com alerta explícito**

     * Se o arquivo não for encontrado / inválido:

       * logar `WARNING` com motivo + caminho tentado
       * incluir “usando DEFAULT_CONFIG”
     * (se isso for crítico em prod, pode virar `ERROR` e falhar startup — mas isso é decisão; por enquanto warning cumpre.)
  4. **Validar schema da config**

     * Validar com Pydantic (ou validação manual) para impedir config “quase certa”.
     * Se inválida: warning + fallback (ou fail fast conforme ambiente).
  5. **Garantir inclusão no deploy**

     * Se o deploy empacota Python (wheel/docker):

       * confirmar que o arquivo JSON é incluído (MANIFEST.in / package_data / Docker COPY).
     * Se roda direto do repo no container, só precisa garantir que o arquivo está no caminho e não fica em docs/.
  6. **Documentar**

     * Em doc de ops/dev: “onde fica a config e como sobrescrever”.

* **Critério de aceite (objetivo):**

  1. A config padrão é carregada de `app/config/eventos_saude_dados_config.json` (ou equivalente).
  2. Se o arquivo não existir ou estiver inválido:

     * aparece log `WARNING` claro (“fallback para DEFAULT_CONFIG” + motivo).
  3. Existe suporte a override por env (`EVENT_DATA_HEALTH_CONFIG_PATH`).
  4. Testes:

     * “carrega config do caminho padrão”
     * “carrega config via env”
     * “arquivo ausente -> warning + fallback”
     * “arquivo inválido -> warning + fallback”

* **Dependências/risco:**

  * Ajuste no deploy para incluir JSON no pacote/container.
  * Decidir se em produção fallback deve ser permitido (warning) ou proibido (fail fast).
    Sugestão pragmática: warning por padrão + opção `STRICT_HEALTH_CONFIG=1` para falhar em prod.

---


Dá ganho sim — e não é “perfuminho”: router gigante vira **fábrica de regressão** e trava qualquer vibe coding (ninguém entende onde mexer, todo mundo tem medo). Mas é trabalho grande, então o jeito certo é **refatorar em fatias**, sem quebrar contrato.

Aqui vai o detalhamento com um plano executável (e critérios de aceite que não são subjetivos):

---

### [P2] Router de eventos muito grande e com múltiplas responsabilidades

* **Ganha algo?** Sim:

  * **Manutenção mais barata**: mudanças localizadas, menos conflito de merge.
  * **Menos regressão**: cada módulo com testes e boundaries claros.
  * **Onboarding/vibe coding**: “quer mexer no import? abre eventos_import.py e acabou”.
  * **Facilita segurança/permissões**: aplicar dependências por área (ex: import/export mais restrito).
  * **Abre espaço para performance**: services isolados ficam fáceis de otimizar sem encostar em CRUD.

* **Impacto:** médio (manutenção lenta, risco de regressão).

* **Probabilidade:** alta (arquivo 1–2k linhas sempre vira bola de neve).

* **Esforço:** G.

* **Evidência:** `app/routers/eventos.py` mistura CRUD + import/export + dicionários + form-config + questionário + gamificação + ativação (`751-2056` etc).

---

## Recomendação (refactor “seguro” em etapas)

### 1) Definir o alvo: arquitetura mínima e nomes

Criar pacote: `app/routers/eventos/` e transformar em submódulos:

* `app/routers/eventos/__init__.py` (monta o router principal e inclui subrouters)
* `app/routers/eventos/crud.py` (GET/POST/PUT/DELETE básicos)
* `app/routers/eventos/import.py` (import CSV/XLSX, matching, validações, limites)
* `app/routers/eventos/export.py` (export CSV/relatórios)
* `app/routers/eventos/dicionarios.py` (listas/combos/status/tipos)
* `app/routers/eventos/forms.py` (form-config / questionário)
* `app/routers/eventos/gamificacao.py` (regras gamificação)
* `app/routers/eventos/ativacao.py` (ativação/estado operacional)

**Regra:** manter o mesmo prefixo e paths públicos (ex: `/eventos/...`) para não quebrar frontend/consumidores.

### 2) Congelar contrato antes de mexer

Antes de mover código:

* gerar lista de endpoints reais:

  * `rg -n "@router\\.(get|post|put|delete|patch)\\(" app/routers/eventos.py`
* registrar (método + path + tags + status codes) num arquivo:

  * `docs/auditoria_eventos/ENDPOINTS_EVENTOS.md`
* Se houver OpenAPI tags, manter as mesmas.

### 3) Extrair “sem mudança de lógica”

Ordem de extração (do mais isolado pro mais crítico):

1. **dicionarios** (baixo risco)
2. **forms/questionario** (médio risco)
3. **gamificacao** (médio risco)
4. **export** (médio/alto, mas isolável)
5. **import** (alto risco)
6. **crud** (alto risco, central)

Cada extração:

* Move handlers (funções) para o novo arquivo.
* Mantém as dependências e response models iguais.
* O arquivo antigo passa a só incluir subrouters (ou vai diminuindo gradualmente).

### 4) Criar services para lógica de domínio (a parte que realmente reduz bagunça)

Depois de “mover” (organização), vem o “ganho real”:

* Lógica pesada que hoje está no router vai para `app/services/eventos/...`:

  * `matching.py`
  * `importer.py`
  * `exporter.py`
  * `visibility.py` (matriz NPBB/BB/Agência)
  * `forms.py`
* Router vira cola fina (parse input → chama service → retorna response).

### 5) Testes como cinto de segurança

* Antes de refatorar: garantir pelo menos testes de smoke:

  * “lista eventos”
  * “cria/atualiza evento”
  * “import endpoint responde”
  * “export endpoint responde”
* Depois de cada extração: rodar testes + assegurar que OpenAPI não mudou path.

### 6) Critérios objetivos de “arquivo menor”

Para não virar discussão:

* `eventos.py` final deve ter no máximo:

  * criação do router principal + includes + coisas comuns (≤ ~150-250 linhas).
* Cada subrouter idealmente ≤ ~400 linhas (sem services dentro).

---

## Critério de aceite (bem definido)

1. **Sem breaking changes**:

   * Mesmos paths e métodos expostos (comparar lista antes/depois).
2. **Arquivos menores e com responsabilidade única**:

   * `app/routers/eventos.py` vira “orquestrador” (inclui subrouters).
   * Submódulos separados conforme responsabilidades.
3. **Services criados** para pelo menos import e visibility (os mais sensíveis).
4. **Testes passam** e incluem:

   * smoke por subrouter (mínimo).
5. **Documentação atualizada**:

   * `docs/auditoria_eventos/ENDPOINTS_EVENTOS.md` atualizado
   * mapa de módulos.

---

## Dependências/risco

* Refactor grande sem testes é roleta russa.
* Pode haver imports circulares se hoje o router “faz tudo”. Precisa organizar dependências:

  * routers -> services -> models/db/utils
  * evitar services importarem routers.

---


Boa pegada — isso é aquele bug “funciona na minha máquina porque eu rodei seed uma vez em 2023”.

### [P2] Inferência de status usa nomes hard-coded; erro 500 se status não estiver seedado

* **Ganha algo?** Sim:

  * **Menos 500 besta** em dev/stage (e até prod depois de restore).
  * **Onboarding melhor**: erro diz exatamente o que falta e como resolver.
  * **Observabilidade**: fica óbvio quando o ambiente está sem pré-requisito.
  * **Separa bug de infra de bug de regra**.

* **Impacto:** médio (falha de criação em ambientes sem seed; quebra fluxo).

* **Probabilidade:** média (ambientes novos/CI/stage frequentemente sobem sem seed completo).

* **Esforço:** P.

* **Evidência:**

  * `app/routers/eventos.py:942-975`: constantes `STATUS_*` + `_get_status_id_by_nome` (explode e vira 500).
  * `app/routers/eventos.py:1071-1076`: usado na criação.

---

## Recomendação (do mais seguro pro mais “maduro”)

### 1) Trocar “500” por erro de precondição (400/409) com instrução clara

Quando faltar status:

* retornar **400 Bad Request** (ou **409 Conflict**) com mensagem tipo:

  * `"STATUS_NOT_CONFIGURED: status '<nome>' não encontrado. Rode seed: python -m ... ou alembic + seed ..."`
* Isso resolve o sintoma sem mascarar.

**Regra prática**:

* 500 = bug do servidor
* seed faltando = **ambiente mal configurado** → 400/409 + instrução

### 2) Validar no startup (fail-fast opcional)

No startup do app:

* checar se os status mínimos existem (os que o código assume).
* Se faltarem:

  * **warning** + “app sobe mas rotas falham” (modo dev)
  * ou **raise** e não sobe (modo prod), controlado por env:

    * `STRICT_SEED_CHECK=1`

Isso evita pegar na rota só quando alguém tenta criar.

### 3) Tirar hard-code de “nome” se possível (melhoria P2/P3)

* Melhor que depender de `nome` é depender de **código/enum** (ex: `status.code = "ATIVO"`).
* Se o modelo não tem code, considerar adicionar (mas isso é migração e pode virar P1/P2 dependendo do impacto).
* Se não der, pelo menos:

  * centralizar nomes numa única config e documentar.

---

## Critério de aceite (objetivo)

1. Em ambiente sem seed:

   * criar evento retorna **400/409** com payload claro e instruções (nada de 500).
2. Existe checagem no startup:

   * loga warning ou falha conforme `STRICT_SEED_CHECK`.
3. Existe documentação:

   * `docs/SETUP.md` ou `docs/TROUBLESHOOTING.md` explica seed obrigatório e comando.
4. Testes:

   * teste “sem status seedado” → resposta amigável
   * teste “com status” → cria normal

---

## Dependências/risco

* Depende do processo real de seed/migração:

  * onde fica o seed? script? fixture? migration?
* Precisa garantir que a instrução no erro aponta um comando que existe no repo (senão vira meme).

Se você quiser, mando uma versão “prompt pro Codex executar” já com: localizar seed atual, criar `seed_required_statuses`, implementar checagem no startup e ajustar a rota pra 400/409 + testes.


Dá ganho sim — não vai deixar o sistema “10x mais rápido”, mas evita o tipo de bug chato: **um router atualiza a regra, o outro fica velho e vaza dado**. E é barato.

### [P3] Regras de visibilidade duplicadas em routers relacionados

* **Ganha algo?**

  * **Menos divergência**: uma regra só, todo mundo obedece.
  * **Mudança mais rápida**: alterou a matriz uma vez, acabou.
  * **Reduz risco de vazamento**: duplicação em permissão é pedir pra dar ruim.

* **Impacto:** baixo/médio (duplicação + risco de comportamento diferente).

* **Probabilidade:** alta (duplicação costuma “apodrecer” com o tempo).

* **Esforço:** P.

* **Evidência:**

  * `app/routers/ativacao.py:31-45`
  * `app/routers/gamificacao.py:17-33`
  * (mesma lógica copiada)

---

## Recomendação (faça do jeito certo, não “copia e cola melhorado”)

### 1) Extrair helper único

Criar módulo: `app/utils/visibility.py` (ou `app/services/visibility.py` se for regra de negócio).

API sugerida (mínima e clara):

* `def apply_event_visibility(query, usuario) -> query:`

  * aplica a matriz (NPBB vê tudo; BB por diretoria; Agência por agência).
* `def can_access_event(usuario, evento) -> bool:`

  * útil para endpoints “detail” (e evita enumeração retornando 404).

> Evite helper “genérico demais”. Permissão precisa ser óbvia.

### 2) Substituir nos routers

* Em `ativacao.py` e `gamificacao.py`:

  * remover lógica duplicada
  * chamar o helper
* Se cada router hoje faz “list” e “detail”, usar:

  * list: `apply_event_visibility(select(...), usuario)`
  * detail: buscar com filtro de visibilidade e se não achar → 404

### 3) Testes

* Se já existem testes desses endpoints, eles devem continuar passando.
* Se não existem, pelo menos adicionar 2 testes smoke (baratos) para garantir que ambos routers aplicam a mesma regra:

  * usuário agência não acessa evento de outra agência
  * usuário bb não acessa evento de outra diretoria
  * NPBB acessa ambos

---

## Critério de aceite

* Não existe mais lógica duplicada nos dois routers citados.
* Ambos importam e usam **o mesmo** helper.
* Testes passam.
* (Bônus bom) existe pelo menos 1 teste que prova que os dois endpoints respeitam a mesma matriz.

