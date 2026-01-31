# Pagina de Ativos (Cotas de ingressos)

## 1. Nome da Tela
**Ativos (Cotas de ingressos cortesia)**

Tela para exibir, acompanhar e ajustar a distribuicao de ingressos (cotas) por Diretoria e Evento.

Status no novo sistema:
- Frontend: implementado (listagem, filtros, atribuicao, exportacao).
- Backend: implementado (GET /ativos, POST /ativos/{evento_id}/{diretoria_id}/atribuir, GET /ativos/export/csv).

---

## 2. Referencia Visual
Print do sistema original:
`docs/tela-inicial/menu/Ativos/ativos.png`

---

## 3. Estrutura (proposta)
### 3.1 Cabecalho da pagina
- Titulo: **Ativos**
- Acoes principais: **Atualizar**, **+ Novo**

### 3.2 Painel lateral (filtros)
- Filtros: Evento, Diretoria, Data
- Acoes: **Aplicar** / **Limpar** / **Exportar CSV**

### 3.3 Lista de cards
Cada card representa uma combinacao **evento + diretoria**, exibindo:
- Evento
- Diretoria
- Disponibilidade (ex.: `23 / 45`)
- Indicador visual (barra de progresso ou percentual)
- Acoes: icone **Editar** e icone **Excluir** (canto superior do card)
- Icone **Excluir** (desabilitado quando `usados > 0`)

Wireframe textual do card (ordem):
1. **Evento** (titulo)
2. **Diretoria** (subtitulo)
3. **Resumo**: Usados / Total + Disponiveis
4. **Indicador**: barra + percentual
5. **Acoes**: icones editar/excluir no canto superior

### 3.3.1 Indicador de uso (decisao)
- Formato: **barra de progresso + percentual** no card.
- Percentual: `usados / total` (0% quando `total = 0`).
- Limites: clamp entre **0% e 100%**.
- Tamanho: barra com **8px** de altura.
- Cores: **< 50% (success)**, **50–79% (warning)**, **>= 80% (error)**.

### 3.4 Estados da tela
- **Carregando**: exibir skeletons/placeholder de cards.
- **Vazio**: mensagem “Nenhum ativo encontrado” + acao “Limpar filtros”.
- **Erro**: mensagem “Erro ao carregar ativos” + acao “Tentar novamente”.
- **Sucesso**: grid de cards (paginacao via API, sem controles na UI).

---

## 4. Comportamento (observado/esperado)
- Ao carregar, lista todos os cards (um por evento + diretoria com cota cadastrada).
- Botao **Atualizar** recarrega os dados.
- Botao **+ Novo** abre um modal para criar a cota (evento + diretoria + quantidade).
- Icone **Editar** abre um modal para atualizar a quantidade total disponivel.
- **Excluir** remove a cota (apenas quando `usados = 0`).
- Ao salvar, o card reflete imediatamente o novo total.

---

## 4.1 Fluxo: Atribuir ingressos (passo a passo)
1. Usuario clica no icone **Editar** no card.
2. Modal abre mostrando **Evento**, **Diretoria**, **Total atual** e **Usados**.
3. Usuario informa nova **Quantidade total** (campo numerico).
4. Validacoes locais:
   - `quantidade < 0` -> mensagem "Quantidade nao pode ser negativa".
   - `quantidade < usados` -> mensagem "Quantidade nao pode ser menor que o total usado".
5. Usuario clica em **Salvar**.
6. UI envia `POST /ativos/{evento_id}/{diretoria_id}/atribuir`.
7. Sucesso: modal fecha, card atualiza valores e exibe toast "Cota atualizada com sucesso".
8. Erro: manter modal aberto e exibir mensagem retornada pela API.

Mensagens esperadas (API):
- 400 `COTA_NEGATIVE` -> "Quantidade nao pode ser negativa".
- 409 `COTA_BELOW_USED` -> "Quantidade nao pode ser menor que o total usado".
- 404 `EVENTO_NOT_FOUND` / `DIRETORIA_NOT_FOUND` -> "Evento/Diretoria nao encontrado".

---

## 4.1.1 Wireframe do modal de atribuicao
Estrutura (ordem):
1. **Titulo**: "Atribuir ingressos"
2. **Contexto**: Evento e Diretoria (texto curto)
3. **Resumo**: Total atual + Usados (ex.: "Usados: 2 de 10")
4. **Campo numerico**: "Nova quantidade total" (min=0)
5. **Mensagem de validacao** (inline)
6. **Acoes**: "Cancelar" (secundario) e "Salvar" (primario)

Campos exibidos:
- Evento
- Diretoria
- Total atual
- Usados

---

## 4.1.2 Estrategia de update otimista (UI)
- Regra: ao clicar em **Salvar**, a UI pode atualizar o card imediatamente com o novo `total`.
- Guardar **valor anterior** (total/usados/disponiveis) para rollback se a API falhar.
- Se erro: restaurar valores anteriores e exibir mensagem de erro.

---

## 4.1.3 Concorrencia simples (UI)
- **Bloqueio**: desabilitar o botao "Salvar" enquanto uma requisicao esta em andamento.
- **Garantia**: impedir multiplas submissões simultaneas para o mesmo card.
- **UI**: manter um unico estado de "salvando" por vez.

---

## 4.1.4 Fluxo: Excluir ativo
1. Usuario clica no icone **Excluir** no card.
2. UI abre modal de confirmacao com evento/diretoria e alerta de irreversibilidade.
3. Se `usados > 0`, o botao **Excluir** fica desabilitado e a UI informa o bloqueio.
4. Confirmacao chama `DELETE /ativos/{cota_id}`.
5. Sucesso: card removido e toast "Ativo excluido com sucesso".
6. Erro: exibir mensagem retornada pela API.

Mensagens esperadas (API):
- 404 `COTA_NOT_FOUND` -> "Cota nao encontrada".
- 409 `COTA_HAS_USED` -> "Nao e possivel excluir uma cota com solicitacoes emitidos".

---
## 4.2 Fluxo: Exportacao CSV
Ponto de entrada:
- Botao **Exportar CSV** no painel lateral (secao **Acoes**).

Passo a passo:
1. Usuario ajusta filtros (evento, diretoria, data).
2. Usuario clica em **Exportar CSV**.
3. UI chama `GET /ativos/export/csv` com os filtros atuais.
4. Sucesso: navegador inicia download do arquivo `ativos.csv` (ou nome retornado pela API).
5. Erro: exibir mensagem "Nao foi possivel exportar o CSV" e acao "Tentar novamente".

Estados e feedback:
- Botao em **loading** durante a requisicao.
- Botao **desabilitado** enquanto exporta para evitar duplicidade.

---

## 4.3 Painel lateral: filtros e acoes
Filtros obrigatorios (MVP):
- Evento (selecao/auto-complete)
- Diretoria (selecao/auto-complete)
- Data do evento (intervalo ou data unica)

Filtros opcionais (pos-MVP):
- Status do evento
- Agencia

Comportamento:
- **Aplicar**: atualiza a listagem e volta para a pagina 1.
- **Limpar**: remove filtros, reseta pagina para 1 e recarrega a listagem.
- **Persistencia**: filtros ficam na URL (querystring) para manter estado ao navegar.

---

## 5. Regras de negocio (confirmadas)
- Cada diretoria possui **uma unica** cota (quantidade total) por evento (unicidade `evento + diretoria`).
- Se nao existir cota para a combinacao **evento + diretoria**, a listagem nao exibe card; o endpoint de atribuicao **cria** a cota ao salvar.
- Cota **nao pode** existir sem evento e diretoria validos (FK obrigatoria).
- **Ingressos usados = solicitacoes de ingresso** (cada solicitacao consome 1 ingresso da cota).
  - Origem do dado: entidade `SolicitacaoIngresso` (tabela `solicitacao_ingresso`) vinculada a `CotaCortesia` via `cota_id`.
  - Solicitacoes canceladas **nao** entram na contagem de usados.
  - `usados` e calculado **em tempo real** na listagem/exportacao (nao persistido na cota).
- Nao permitir:
  - atribuir valor negativo
  - definir total menor que o numero ja usado
  - excluir cota com solicitacoes emitidas
- Exportacao CSV: pagina deve permitir exportar cotas/consumo.
- Cada card deve permitir acessar a lista de solicitacoes daquela cota; cancelar solicitacao devolve 1 ingresso.

### Erros e validacoes (atribuir)
- `quantidade < 0` -> HTTP 400 `COTA_NEGATIVE` ("Quantidade nao pode ser negativa").
- `quantidade < usados` -> HTTP 409 `COTA_BELOW_USED` ("Quantidade nao pode ser menor que o total usado").
- `evento_id` inexistente -> HTTP 404 `EVENTO_NOT_FOUND` ("Evento nao encontrado").
- `diretoria_id` inexistente -> HTTP 404 `DIRETORIA_NOT_FOUND` ("Diretoria nao encontrada").

Tabela de erros (padrao):
| Code | Message | Status |
|---|---|---|
| `COTA_NEGATIVE` | Quantidade nao pode ser negativa | 400 |
| `COTA_BELOW_USED` | Quantidade nao pode ser menor que o total usado | 409 |
| `COTA_HAS_USED` | Nao e possivel excluir uma cota com solicitacoes emitidas | 409 |
| `COTA_NOT_FOUND` | Cota nao encontrada | 404 |
| `EVENTO_NOT_FOUND` | Evento nao encontrado | 404 |
| `DIRETORIA_NOT_FOUND` | Diretoria nao encontrada | 404 |
| `FORBIDDEN` | Usuario agencia sem agencia_id | 403 |
| `CSV_LIMIT_EXCEEDED` | Limite de exportacao excedido | 400 |

---

## 6. Endpoints (implementados)
- `GET /ativos` -> lista evento, diretoria, usados, disponiveis
- `POST /ativos/{evento_id}/{diretoria_id}/atribuir` -> ajusta quantidade total
- `GET /ativos/export/csv` -> exporta a listagem filtrada em CSV
- `DELETE /ativos/{cota_id}` -> exclui a cota (apenas se usados = 0)
- `GET /ativos/{evento_id}/{diretoria_id}` -> detalhes/historico (**nao implementado**)

---

## 6.0.1 Contrato de atribuicao (POST /ativos/{evento_id}/{diretoria_id}/atribuir)
Payload:
```json
{
  "quantidade": 10
}
```

Comportamento:
- **Create-on-demand**: se nao existir cota para `evento_id + diretoria_id`, o endpoint **cria** a cota e retorna o estado atualizado.

Seguranca/visibilidade:
- `tipo_usuario=AGENCIA` so pode ver/alterar cotas de eventos da propria `agencia_id`.
- Se usuario agencia nao tiver `agencia_id`, retornar HTTP 403 `FORBIDDEN`.
- Se evento nao pertence a agencia, retornar HTTP 404 (`EVENTO_NOT_FOUND`).

Response (estado atualizado):
```json
{
  "id": 12,
  "evento_id": 10,
  "evento_nome": "Reveillon",
  "diretoria_id": 3,
  "diretoria_nome": "dimac",
  "total": 10,
  "usados": 2,
  "disponiveis": 8,
  "percentual_usado": 0.2
}
```

---

## 6.1 DTO de resposta (GET /ativos)
Campos de contexto:
- `id` (cota)
- `evento_id`, `evento_nome`
- `data_inicio`, `data_fim`
- `diretoria_id`, `diretoria_nome`

Campos de negocio (minimos):
- `total` (quantidade da cota)
- `usados`
- `disponiveis`
- `percentual_usado`

Nomenclatura alinhada (API/UI):
- API: `total`, `usados`, `disponiveis`, `percentual_usado`
- UI: Total, Usados, Disponiveis, Percentual

Regras de calculo:
- `usados = count(solicitacao_ingresso)` por cota, **excluindo** `CANCELADO`.
- `disponiveis = total - usados` (minimo 0).
- `percentual_usado = usados / total` (quando `total > 0`; caso contrario `0`).

---

## 6.2 Ordenacao (GET /ativos)
Observacao: **order_by nao implementado** no backend atual. Mantem a ordem padrao por `cota_cortesia.id desc`.

Ordenacoes planejadas:
- `usados_desc` -> ordem por usados (maior para menor).
- `disponiveis_asc` -> ordem por disponiveis (menor para maior).
- `evento_nome_asc` -> ordem por nome do evento (A-Z).

Mapeamento para colunas:
- `usados_desc` -> `count(solicitacao_ingresso)` por cota.
- `disponiveis_asc` -> `cota_cortesia.quantidade - count(solicitacao_ingresso)`.
- `evento_nome_asc` -> `evento.nome`.

Parametro da API (planejado):
- `order_by` (string).
- Valores previstos: `usados_desc`, `disponiveis_asc`, `evento_nome_asc`.

Exemplos (quando implementado):
- `GET /ativos?order_by=usados_desc`
- `GET /ativos?order_by=disponiveis_asc&evento_id=10`
- `GET /ativos?order_by=evento_nome_asc&diretoria_id=3`

---

## 6.3 Ordenacao por campos calculados (usados/disponiveis)
Estrategia:
- Usar **subquery/agregacao** para `usados = count(solicitacao_ingresso)` por `cota_id`.
- Join da subquery na listagem para permitir `ORDER BY usados` e `ORDER BY (quantidade - usados)`.

Performance:
- Index em `solicitacao_ingresso.cota_id` e filtro por status ajudam no `COUNT`.
- Paginação deve ocorrer **apos** a ordenacao agregada para evitar inconsistencias.

---

## 6.5 Contrato de exportacao (GET /ativos/export/csv)
Endpoint:
- `GET /ativos/export/csv`

Filtros (mesmos do GET /ativos):
- `evento_id`, `diretoria_id`, `data`

Exemplo:
- `GET /ativos/export/csv?evento_id=10&diretoria_id=3&data=2026-01-01`

---

## 6.6 Layout do CSV (ativos)
Colunas (ordem):
1. Evento
2. Diretoria
3. Data inicio
4. Data fim
5. Total
6. Usados
7. Disponiveis
8. Percentual

Cabecalhos finais (ordem):
- Evento, Diretoria, Data inicio, Data fim, Total, Usados, Disponiveis, Percentual

Formatacao:
- Datas: `YYYY-MM-DD`
- Percentual: `0.00` (ex.: `0.45` para 45%)
- Numeros inteiros (Total/Usados/Disponiveis): sem separador de milhar

---

## 6.6.1 Exemplo de CSV (ativos)
```csv
Evento,Diretoria,Data inicio,Data fim,Total,Usados,Disponiveis,Percentual
Reveillon,dimac,2026-12-31,2027-01-01,10,2,8,0.20
```

Exemplo de chamada:
- `GET /ativos/export/csv?evento_id=10&diretoria_id=3&data=2026-12-31`

---

## 6.7 Performance e limites (CSV)
- Limite maximo: **10.000 registros** por exportacao.
- Comportamento: se o total filtrado exceder o limite, retornar erro **400** `CSV_LIMIT_EXCEEDED`.
- Objetivo: evitar exportacoes pesadas que possam degradar a API.

---

## 7. MVP (escopo minimo)
Entra no MVP:
- Listagem de ativos (evento + diretoria) com total/usados/disponiveis.
- Atribuir/ajustar cota (validacoes aplicadas).
- Filtros basicos (evento, diretoria, data).
- Exportacao CSV da listagem filtrada.

Fora do MVP:
- Historico/auditoria detalhada (linha do tempo completa) — complexidade adicional.
- Notificacoes (email, alertas) — dependencia de infra/servicos externos.
- Importacao em massa de cotas — maior risco de dados inconsistentes.
- Dashboards/analises avancadas — fora do foco do fluxo principal.
- Controle de acesso granular por diretoria/evento — exige regras/perfis adicionais.

---

## 8. Objetivos do MVP (criterios de sucesso)
Capacidades minimas (acoes do usuario / resultado):
1. **Listar ativos** com evento, diretoria, total, usados e disponiveis.
2. **Filtrar a listagem** por evento, diretoria e data.
3. **Atribuir/ajustar cota** com validacoes (nao negativo e nao menor que usados).
4. **Visualizar indicador de uso** (percentual e/ou barra) por card.
5. **Exportar CSV** com os mesmos filtros aplicados.
6. **Receber feedback claro** de sucesso/erro ao salvar ajustes.

Criterios de sucesso mensuraveis:
- Fluxo principal completo (listar -> filtrar -> ajustar -> exportar) **sem bloqueios**.
- Erros de validacao retornam codigo/mensagem padronizados.
- Listagem respeita paginação e exibe total corretamente.
- Exportacao gera arquivo consistente com a listagem filtrada.

---

## 8.1 Matriz MVP x Fora de escopo
| Inclui no MVP | Fora de escopo |
|---|---|
| Listagem de ativos (evento + diretoria) | Historico/auditoria detalhada |
| Filtros basicos (evento, diretoria, data) | Notificacoes (email, alertas) |
| Atribuir/ajustar cota com validacoes | Importacao em massa de cotas |
| Indicador de uso (percentual/barra) | Dashboards/analises avancadas |
| Exportacao CSV filtrada | Controle de acesso granular por diretoria/evento |

---

## 8.2 Revisao rapida do fluxo principal (sanidade)
Checklist do fluxo (listar -> ajustar -> validar -> exportar):
- [x] **Listar** ativos com total/usados/disponiveis (GET /ativos).
- [x] **Ajustar cota** via modal (POST /ativos/{evento_id}/{diretoria_id}/atribuir).
- [x] **Validar** regras (nao negativo, nao menor que usados) com erros padronizados.
- [x] **Exportar CSV** com filtros aplicados (GET /ativos/export/csv).

Lacunas/ajustes sugeridos:
- Definir **status validos de solicitacao_ingresso** que contam como "usados" (SOLICITADO; excluir CANCELADO).
- Confirmar se o fluxo permite **criar cota ao ajustar** quando inexistente (documentado como sim; precisa refletir no backend).

---

## 9. Glossario (pt-BR)
- **Ativo**: cota de ingressos vinculada a uma combinacao **evento + diretoria**.
- **Cota**: quantidade total de ingressos disponiveis para um **Ativo**.
- **Usado**: quantidade de solicitacoes ativas (status SOLICITADO) na tabela `solicitacao_ingresso`.
- **Disponivel**: `cota (total) - usado`.
- **solicitacao de ingresso**: registro na tabela `solicitacao_ingresso` criado por um solicitante.

Nomenclatura API/UI (pt-BR):
- API: `total`, `usados`, `disponiveis`, `percentual_usado`.
- UI: Total, Usados, Disponiveis, Percentual.

---

## 10. Entidade Ativo/Cota (modelo)
Entidade principal: **CotaCortesia** (tabela `cota_cortesia`).

Campos obrigatorios (MVP):
- `id`: identificador da cota.
- `evento_id`: FK para `evento`.
- `diretoria_id`: FK para `diretoria`.
- `quantidade` (total): quantidade total de ingressos da cota.

Campos derivados (na resposta):
- `usados`: total de solicitacoes ativas para a cota (contagem em `solicitacao_ingresso`).
- `disponiveis`: `quantidade - usados`.
- `percentual_usado`: `usados / quantidade` (quando `quantidade > 0`).

Relacionamentos:
- **Evento 1:N CotaCortesia**
- **Diretoria 1:N CotaCortesia**
- **CotaCortesia 1:N SolicitacaoIngresso**

Unicidade:
- Uma unica cota por combinacao **evento_id + diretoria_id** (chave unica).

---

## 10.1 Relacao Ativo ↔ Evento
- Cardinalidade: **1 Evento -> N Cotas (Ativos)**.
- Integridade: cota **nao pode existir** sem `evento_id` valido (FK obrigatoria).
- Regra de exclusao: **nao permitir** excluir evento com cotas vinculadas (bloquear ou exigir limpeza previa).

---

## 10.1.1 Relacao Ativo ↔ Diretoria
- Cardinalidade: **1 Diretoria -> N Cotas (Ativos)**.
- Integridade: cota **nao pode existir** sem `diretoria_id` valido (FK obrigatoria).
- Regra de exclusao: **nao permitir** excluir diretoria com cotas vinculadas (bloquear ou exigir limpeza previa).

---

## 10.2 Entidade SolicitacaoIngresso (origem do "usado")
- Fonte: entidade **SolicitacaoIngresso** (tabela `solicitacao_ingresso`), ligada a `CotaCortesia` por `cota_id`.
- Relacao com evento/diretoria: SolicitacaoIngresso -> CotaCortesia -> Evento/Diretoria.
- Regra de contagem: `usados = count(solicitacao_ingresso)` por cota, **excluindo** solicitacoes com status CANCELADO.

---

## 10.3 Diagrama logico (texto)
- **Evento 1:N CotaCortesia (Ativo)**
- **Diretoria 1:N CotaCortesia (Ativo)**
- **CotaCortesia 1:N SolicitacaoIngresso**
- **SolicitacaoIngresso N:1 Usuario (solicitante)**

---

## 10.4 Indices para listagem e filtros
Indices recomendados:
- `cota_cortesia` **UNIQUE (evento_id, diretoria_id)**: garante unicidade e acelera joins/lookup por evento.
- `cota_cortesia` **INDEX (diretoria_id)**: acelera filtro por diretoria (consulta isolada).
- `solicitacao_ingresso` **INDEX (cota_id)**: acelera contagem de `usados` por cota.
- `evento` **INDEX funcional** em `coalesce(data_inicio_prevista, data_inicio_realizada)` e
  `coalesce(data_fim_prevista, data_fim_realizada)` para filtro por data do evento.

Justificativas (por consulta):
- Listagem por **evento** usa o indice composto (evento_id, diretoria_id).
- Filtro por **diretoria** usa o indice dedicado em `diretoria_id`.
- Calculo de **usados** usa `solicitacao_ingresso.cota_id` (count por cota).
- Filtro por **data** usa as datas do evento (indice funcional evita full scan).

---

## 10.5 Unicidade de Ativo (evento_id + diretoria_id)
- Constraint unica: `UNIQUE (evento_id, diretoria_id)` na tabela `cota_cortesia`.
- Comportamento em conflito: **erro** (HTTP 409 `COTA_DUPLICATE`) ao tentar criar uma segunda cota para a mesma combinacao.
- Upsert **nao** sera utilizado no MVP (alteracao deve ocorrer via endpoint de atribuicao).

---

## 10.6 Constraints de integridade referencial (FK)
- `cota_cortesia.evento_id -> evento.id` (**ON DELETE RESTRICT**, **ON UPDATE RESTRICT**).
- `cota_cortesia.diretoria_id -> diretoria.id` (**ON DELETE RESTRICT**, **ON UPDATE RESTRICT**).

Decisao para dados orfaos:
- **Nao permitir** dados orfaos; exclusao de evento/diretoria deve falhar se houver cotas vinculadas.

---

## 10.7 Checklist de validacao de dados (DB)
Constraints check:
- `cota_cortesia.quantidade >= 0`
- `solicitacao_ingresso.status` dentro de um conjunto permitido (ex.: `SOLICITADO`, `CANCELADO`)

Observacoes de tipos:
- `quantidade`: inteiro nao negativo (int).
- `usados`/`disponiveis`: derivados (nao persistidos).

---

## 10.8 Migracao inicial (cota_cortesia)
Esqueleto da tabela (campos + tipos):
- `id` (PK, int, auto incremento)
- `evento_id` (FK -> `evento.id`, int, obrigatorio)
- `diretoria_id` (FK -> `diretoria.id`, int, obrigatorio)
- `quantidade` (int, obrigatorio, >= 0)

Constraints basicas:
- `UNIQUE (evento_id, diretoria_id)`
- `CHECK (quantidade >= 0)`
- FKs com **ON DELETE/UPDATE RESTRICT**

---

## 10.9 Planejamento de FKs (Evento/Diretoria)
FKs:
- `cota_cortesia.evento_id -> evento.id` (ON DELETE/UPDATE **RESTRICT**)
- `cota_cortesia.diretoria_id -> diretoria.id` (ON DELETE/UPDATE **RESTRICT**)

Justificativa:
- **Restrict** evita orfaos e garante integridade do dominio (cotas dependem de evento/diretoria validos).
- Exclusoes devem ser conscientes (limpar cotas antes de excluir evento/diretoria).

---

## 10.10 Seed minimo (dev)
Quantidade minima sugerida:
- **Eventos**: 2
- **Diretorias**: 2
- **Cotas (cota_cortesia)**: 3 (ao menos 2 combinacoes distintas evento+diretoria)
- **solicitacoes**: 2 (para simular `usados > 0`)

Cenarios de teste:
- Cota com `quantidade` > 0 e **usados > 0** (ex.: 10 total, 2 solicitacoes).
- Cota **zerada** (quantidade = 0, usados = 0).
- Cota **sem solicitacoes** (quantidade > 0, usados = 0).

---

## 10.11 Sequencia de execucao (migrations/seeds)
Ordem recomendada:
1. **Migracoes** do schema (tabelas base + `cota_cortesia` + `solicitacao_ingresso`).
2. **Seeds base**: eventos, diretorias (e convidados/funcionarios, se necessario).
3. **Seeds de cotas**: inserir `cota_cortesia` para combinacoes validas.
4. **Seeds de solicitacoes**: inserir `solicitacao_ingresso` associado a `cota_cortesia`.

Dependencias explicitas:
- `evento` e `diretoria` **antes** de `cota_cortesia`.
- `cota_cortesia` **antes** de `solicitacao_ingresso`.

---

## 10.12 Checklist de rollback (minimo)
Estrategia minima:
- Executar **downgrade** da migracao que criou `cota_cortesia` (removendo tabela e constraints).
- Remover seeds inseridos (cotas/solicitacoes) antes do downgrade, se necessario.

Observacoes de risco:
- Downgrade pode falhar se houver dependencias (ex.: solicitacoes ligados).
- Garantir backup/ambiente de dev antes de rollback.

---

## 10.13 Auditoria minima (campos)
Campos sugeridos:
- `alterado_por` (usuario id ou email)
- `alterado_em` (timestamp UTC)
- `valor_anterior` (quantidade antes da mudanca)
- `valor_novo` (quantidade apos a mudanca)

Origem dos dados:
- `alterado_por` vem de `current_user.id` (ou `current_user.email` para auditoria humana).
- `alterado_em` gerado no backend (UTC) no momento do update/insert.

---

## 10.14 Onde armazenar auditoria (MVP)
Decisao:
- Armazenar **na propria tabela `cota_cortesia`** (campos simples de auditoria).

Impacto:
- **Queries**: sem joins adicionais (mais simples e performatico).
- **UI**: exibicao opcional do "ultimo ajuste" (data/usuario) sem precisar historico.

---

## 10.15 Exposicao de auditoria no DTO (MVP)
Decisao:
- **Nao incluir** campos de auditoria na listagem (`GET /ativos`) no MVP.

Quando necessario:
- Em um endpoint de detalhe, expor `alterado_por`, `alterado_em`, `valor_anterior`, `valor_novo`.

---

## 11. Backlog (status)
### Backend
- [x] Modelos/tabelas de cotas/solicitacoes (se ainda nao existirem)
- [x] Endpoints de leitura/ajuste
- [x] Validacoes (nao reduzir abaixo do usado)

### Frontend
- [x] Pagina `<AtivosPage />` com grid de cards
- [x] Modal de atribuicao de ingressos
- [x] Filtros + exportacao CSV









