# Diagnóstico crítico do fluxo de importação de leads

Esta análise foi feita a partir do shell React de `/leads/importar`, dos serviços front-end, dos serviços e modelos de backend, da documentação interna e dos testes automatizados do repositório. Eu não consegui executar a instância local `http://localhost:5173/leads/importar` neste ambiente de pesquisa; por isso, os pontos de UX dinâmica e comportamento em runtime foram inferidos do código e dos testes, e eu sinalizo explicitamente onde ainda seria importante validar com observação de uso real, logs e métricas. fileciteturn32file0L1-L1 fileciteturn33file0L1-L1 fileciteturn42file0L1-L1 fileciteturn43file0L1-L1

## Visão geral do fluxo atual

Hoje o endpoint `/leads/importar` não representa um único fluxo; ele funciona como um “shell canônico” que concentra dois caminhos distintos: **Bronze + mapeamento + pipeline** e **ETL CSV/XLSX com preview + commit**. No mesmo shell também existe um modo Bronze simples e um modo Bronze batch. O estado é distribuído entre `importFlow`, `bronzeMode`, `activeStep` e query params como `step`, `batch_id`, `context` e `mapping_mode`, o que torna a navegação muito flexível, mas também bastante carregada de estado implícito. fileciteturn32file0L1-L1 fileciteturn33file0L1-L1

No caminho Bronze, o usuário informa metadados como plataforma, data, evento, origem do lote e, se for o caso, ativação. Só depois disso o arquivo é efetivamente enviado para a camada Bronze via `createLeadBatch`; em seguida o sistema busca um preview do lote já criado por `batch_id`; depois o operador vai para mapeamento; depois para pipeline Gold. No modo batch, cada arquivo vira um `LeadBatch` independente e o workspace serve para acompanhar várias linhas ao mesmo tempo. fileciteturn32file0L1-L1 fileciteturn33file0L1-L1 fileciteturn34file0L1-L1 fileciteturn35file0L1-L1

No caminho ETL, o fluxo é mais seguro do ponto de vista de qualidade de dados: o usuário escolhe o evento, envia o arquivo, recebe um preview com `session_token`, contagem de válidas/inválidas e `dq_report`, resolve problemas de cabeçalho ou coluna CPF se necessário, e só então confirma o commit. O commit tem bloqueio por warnings, suporte a retry em caso de `partial_failure` e reaproveitamento idempotente para sessões já concluídas com status `committed`. fileciteturn42file0L1-L1 fileciteturn21file0L1-L1 fileciteturn22file0L1-L1 fileciteturn23file0L1-L1

Há decisões boas no desenho atual: o sistema recupera metadados de importações anteriores pelo hash do arquivo no Bronze; impede importação de ativação quando o evento ainda não está vinculado a uma agência; permite criação rápida de evento e ativação; mostra progresso do pipeline Gold com polling, detecção de stall e retomada; e no ETL já existe uma separação clara entre preview e persistência. Isso fornece uma base sólida para evoluir, mas a maturidade é desigual entre os dois caminhos. fileciteturn32file0L1-L1 fileciteturn33file0L1-L1 fileciteturn28file0L1-L1 fileciteturn29file0L1-L1 fileciteturn31file0L1-L1

## Principais problemas encontrados

### Shell único com complexidade cognitiva alta

**Descrição.** O mesmo shell mistura quatro modelos mentais diferentes: Bronze simples, Bronze batch, ETL preview/commit e navegação por query string entre upload, mapeamento e pipeline. A pessoa operadora precisa entender não só “o que fazer”, mas também em qual submodo está, qual step está sendo renderizado e se o contexto atual é um lote isolado ou um workspace batch. Isso aumenta a curva de aprendizado e a chance de executar o fluxo certo no modo errado. fileciteturn32file0L1-L1 fileciteturn33file0L1-L1

**Onde ocorre no fluxo.** Logo na entrada do shell, na troca entre “Bronze + mapeamento” e “ETL CSV/XLSX”, na mudança entre upload simples e batch, e também na retomada por URL com `step`, `batch_id`, `context` e `mapping_mode`. Os testes mostram vários comportamentos de reidratação de contexto, fallback e navegação indireta, o que confirma a sofisticação — e a fragilidade — dessa orquestração. fileciteturn32file0L1-L1 fileciteturn43file0L1-L1

**Impacto.** No negócio, isso aumenta custo de treinamento e suporte. Na operação, aumenta o risco de usuários abrirem o fluxo errado, abandonarem o processo ou assumirem que “upload” já significa “importação concluída”. Em UX, reduz previsibilidade.  

**Severidade.** Alta.  

**Probabilidade de ocorrência.** Alta.  

**Sugestão de melhoria.** Separar a entrada em dois caminhos explícitos: “Importação Bronze” e “Importação ETL”. Dentro de Bronze, tratar batch como um subproduto claro, com página própria ou, no mínimo, onboarding contextual e copies diferentes. Também vale reduzir a dependência de query string como mecanismo principal de orquestração visual e mover parte do estado para um modelo de sessão explícita de importação. fileciteturn32file0L1-L1 fileciteturn33file0L1-L1

### Bronze persiste antes de validar de verdade

**Descrição.** No Bronze, o botão primário é “Enviar para Bronze”. O sistema cria o `LeadBatch` e só então carrega um preview do lote por `batch_id`. Em outras palavras: o upload e a persistência precedem a validação operacional do conteúdo. Já o ETL faz o inverso — preview antes de commit. Isso cria dois padrões mentais opostos no mesmo shell e deixa o caminho Bronze mais arriscado para importações erradas. fileciteturn32file0L1-L1 fileciteturn33file0L1-L1 fileciteturn42file0L1-L1

**Onde ocorre no fluxo.** Em `handleSubmitStep1`, quando o shell Bronze chama `createLeadBatch` antes de `getLeadBatchPreview`. fileciteturn32file0L1-L1

**Impacto.** No negócio, aumenta retrabalho e ruído operacional, porque lotes potencialmente errados já entram no sistema. Na operação, “cancelar” depois do upload não desfaz o artefato criado. Em UX, o usuário só descobre a estrutura do arquivo depois de já ter gravado um lote.  

**Severidade.** Alta.  

**Probabilidade de ocorrência.** Alta.  

**Sugestão de melhoria.** Introduzir um “pré-preview” antes de criar o `LeadBatch` — ao menos com detecção de cabeçalho, amostra de linhas, colunas e validações básicas. Idealmente, o Bronze deveria convergir para uma arquitetura semelhante ao ETL: `preview -> confirmação -> criação do artefato persistente`. Se isso for inviável no curto prazo, pelo menos renomear a ação para algo como “Carregar arquivo para revisão” e explicitar que o lote será criado imediatamente. fileciteturn32file0L1-L1 fileciteturn42file0L1-L1

### Autofill por hash ajuda, mas está opaco e pode induzir erro

**Descrição.** O Bronze calcula SHA-256 do arquivo no navegador, tenta recuperar metadados de uma importação anterior do “mesmo ficheiro” e, se o usuário ainda não marcou certos campos como alterados, preenche automaticamente plataforma, data, evento, origem e até ativação. Isso é poderoso, mas a interface mostra apenas um alerta genérico; não existe um diff visível nem uma confirmação explícita do que foi reaplicado. Além disso, o cálculo do hash lê o arquivo inteiro em memória no browser. fileciteturn32file0L1-L1 fileciteturn36file0L1-L1

**Onde ocorre no fluxo.** Na seleção do arquivo Bronze, em `handleSelectFile`, `computeFileSha256Hex`, `getLeadImportMetadataHint` e `applyBronzeImportHint`. Os testes confirmam que o hint pode preencher inclusive origem do lote e ativação. fileciteturn32file0L1-L1 fileciteturn36file0L1-L1 fileciteturn43file0L1-L1

**Impacto.** No negócio, um autofill silencioso pode associar uma importação ao evento ou à ativação errada, contaminando métricas e atribuição operacional. Em performance, arquivos grandes são lidos totalmente pelo browser apenas para calcular hash. Em UX, o sistema “parece adivinhar”, mas sem transparência suficiente para gerar confiança.  

**Severidade.** Alta.  

**Probabilidade de ocorrência.** Média.  

**Sugestão de melhoria.** Transformar o hint em uma sugestão revisável, não em preenchimento silencioso. Exibir um bloco “Metadados sugeridos” com comparação entre valor atual e valor recuperado, pedindo confirmação explícita. Em paralelo, mover o hashing para o backend ou para um fluxo streaming/resumable quando o volume crescer. fileciteturn32file0L1-L1 fileciteturn36file0L1-L1

### Preview ETL é informativo, mas pouco operacional

**Descrição.** O ETL já lida bem com casos como cabeçalho não detectado, CPF ausente, múltiplas abas, header tardio e warnings por duplicidade. Porém, o preview mostrado ao usuário é quase todo resumido em alerts: contagem de linhas, lista de checks e, em `partial_failure`, a enumeração das linhas com falha. Falta uma camada operacional intermediária: preview tabular das linhas rejeitadas, exportação dos erros, drilldown por regra de qualidade e instruções mais prescritivas sobre como corrigir o arquivo. fileciteturn33file0L1-L1 fileciteturn26file0L1-L1 fileciteturn31file0L1-L1

**Onde ocorre no fluxo.** No `EtlPreviewStep`, que mostra `dq_report` como uma pilha de alerts; e no backend, onde `_RejectedRowsCheck` e `_DuplicateRowsCheck` geram amostras, mas a UI não explora esse material de forma mais rica. fileciteturn33file0L1-L1 fileciteturn26file0L1-L1

**Impacto.** No negócio, reduz a taxa de correção em primeira tentativa. Na operação, aumenta o vai-e-volta entre exportar arquivo, corrigir manualmente e reimportar. Em UX, o sistema “avisa”, mas não “ajuda a resolver”.  

**Severidade.** Média.  

**Probabilidade de ocorrência.** Alta.  

**Sugestão de melhoria.** Adicionar uma grade de erros no preview ETL com filtro por regra, linha física, coluna e sugestão de correção. Disponibilizar download de CSV com linhas rejeitadas + motivo. Para warnings de duplicidade, mostrar claramente qual linha vence e por quê. fileciteturn26file0L1-L1 fileciteturn33file0L1-L1

### Batch Bronze escala a fricção operacional junto com o volume

**Descrição.** No batch, cada arquivo selecionado vira um `LeadBatch` independente. O workspace exibe contadores, cada linha tem seus próprios metadados e ações, e o mapeamento é aplicado depois a todos os lotes elegíveis. Isso resolve casos multiarquivo, mas explode o número de artefatos operacionais, cria uma dependência pesada do workspace e exige que o time entenda a diferença entre “linha do grid”, “lote criado”, “mapeamento unificado” e “pipeline por batch_id”. fileciteturn34file0L1-L1 fileciteturn35file0L1-L1

**Onde ocorre no fluxo.** No modo “Upload batch”, em que a copy afirma explicitamente que cada linha gera um `LeadBatch` independente. Os testes também mostram toda a navegação de workspace, fallback para mapeamento single e retomada do próximo pipeline pendente. fileciteturn34file0L1-L1 fileciteturn43file0L1-L1

**Impacto.** No negócio, aumenta custo operacional conforme o volume cresce. Na operação, dificulta auditoria e acompanhamento de uma importação “como um todo”. Em UX, o grid é poderoso, mas pesado para quem só quer “subir dez arquivos parecidos”.  

**Severidade.** Média-alta.  

**Probabilidade de ocorrência.** Média-alta.  

**Sugestão de melhoria.** Criar uma entidade pai, algo como `ImportSession` ou `UploadGroup`, que agrupe n arquivos, centralize metadados compartilhados, consolide status e auditoria, e trate `LeadBatch` como unidade técnica interna, não como unidade principal de experiência. fileciteturn34file0L1-L1 fileciteturn38file0L1-L1

### Arquitetura de armazenamento e parsing tende a doer com arquivo grande

**Descrição.** Há vários sinais de pressão de memória e I/O. O front-end calcula hash lendo o arquivo inteiro em `arrayBuffer`. O servidor lê o upload inteiro em bytes para preview ETL. O modelo Bronze persiste o arquivo bruto em `LargeBinary` na tabela `lead_batches`. E a sessão de preview ETL persiste `approved_rows_json`, `rejected_rows_json` e `dq_report_json` como texto no banco. O próprio front-end estica timeouts para 120 segundos em operações de arquivo/lote, o que é mais um sintoma de acoplamento a chamadas síncronas e pesadas. fileciteturn36file0L1-L1 fileciteturn25file0L1-L1 fileciteturn38file0L1-L1 fileciteturn41file0L1-L1

**Onde ocorre no fluxo.** Upload Bronze, preview ETL e persistência de snapshot ETL. O repositório de preview ainda reaproveita snapshots por idempotência, mas não há evidência aqui de TTL, compactação ou limpeza desses blobs lógicos. fileciteturn23file0L1-L1 fileciteturn41file0L1-L1

**Impacto.** No negócio, o fluxo pode degradar justamente quando a operação mais precisa dele: importações maiores, mais frequentes ou concorrentes. Na operação, aumenta tempo de resposta, consumo de banco, backup e custo de manutenção. Em UX, resulta em spinners longos, timeouts e sensação de instabilidade.  

**Severidade.** Alta.  

**Probabilidade de ocorrência.** Alta para crescimento de volume; média no volume atual.  

**Sugestão de melhoria.** Migrar arquivos brutos para object storage; manter no banco apenas metadados e referências. Para ETL, armazenar snapshots resumidos e materializar linhas detalhadas em storage temporário com TTL. Separar preview, validação e persistência em jobs assíncronos com fila, progressos incrementais e possibilidade de retomada. fileciteturn36file0L1-L1 fileciteturn38file0L1-L1 fileciteturn41file0L1-L1

### Sessão ETL sem dono explícito e sem política visível de expiração

**Descrição.** A tabela `lead_import_etl_preview_session` guarda `session_token`, `idempotency_key`, `evento_id`, filename, status, rows aprovadas/rejeitadas, report e timestamps, mas não guarda usuário responsável. Além disso, o idempotency key do preview é derivado de evento, fingerprint do arquivo, strict e contexto de cabeçalho; o repositório reaproveita snapshots existentes por esse identificador global. Isso sugere uma lacuna de governança: a sessão ETL não tem um “owner” explícito, nem uma política visível de limpeza/expiração no modelo. fileciteturn21file0L1-L1 fileciteturn23file0L1-L1 fileciteturn41file0L1-L1

**Onde ocorre no fluxo.** Na criação e persistência do preview ETL e no reaproveitamento por idempotência. O commit também trabalha apenas com `session_token` e `evento_id`, sem vínculo explícito com o usuário que gerou o preview. fileciteturn21file0L1-L1 fileciteturn22file0L1-L1

**Impacto.** Em segurança e governança, isso dificulta responder com precisão “quem gerou esse preview?”, “quem o confirmou?” e “qual sessão pertence a qual operador?”. Também abre um risco potencial de reaproveitamento cruzado de sessão em cenários multiusuário, principalmente se tokens de sessão vazarem ou forem reemitidos por idempotência global.  

**Severidade.** Alta.  

**Probabilidade de ocorrência.** Média.  

**Sugestão de melhoria.** Incluir `created_by`, `committed_by`, `workspace_id/import_session_id`, `expires_at` e `last_accessed_at` nas sessões ETL. Restringir lookup/cache idempotente por usuário ou por tenant/escopo operacional. Criar job de cleanup e trilha de auditoria formal. fileciteturn23file0L1-L1 fileciteturn41file0L1-L1

### Política de dedupe e merge é segura para preservação, mas arriscada para atualização

**Descrição.** A regra de dedupe considera `email + cpf + evento + sessão`, duplicidades internas no mesmo lote mantêm a última ocorrência, e o merge com registros existentes é não destrutivo: o sistema só preenche campos vazios e não substitui valores já existentes. Isso reduz risco de sobrescrever dados bons, mas cria outro problema: um arquivo novo com dados mais corretos pode ser parcialmente ignorado sem deixar isso claro para o operador. fileciteturn24file0L1-L1 fileciteturn26file0L1-L1 fileciteturn42file0L1-L1

**Onde ocorre no fluxo.** No commit ETL e no import legado/Bronze, porque a política foi documentada como alinhada ao Gold e as rotinas de persistência usam `merge_lead_payload_fill_missing`, lookup contextual e dedupe key. fileciteturn24file0L1-L1 fileciteturn27file0L1-L1 fileciteturn42file0L1-L1

**Impacto.** No negócio, pode manter dados antigos ou incompletos sem sinalizar claramente o conflito. Na operação, dificulta explicar por que uma importação “deu certo” mas não atualizou certos campos. Em UX, o usuário lê “updated”, mas não entende o que realmente mudou.  

**Severidade.** Média-alta.  

**Probabilidade de ocorrência.** Alta em bases já existentes.  

**Sugestão de melhoria.** Mostrar no resultado uma visão de “campos ignorados por política de merge” e permitir, em fluxos controlados, modos alternativos de atualização: `fill_missing`, `prefer_import`, `prefer_existing`, sempre com confirmação e auditoria. fileciteturn24file0L1-L1 fileciteturn22file0L1-L1

### Boa resiliência pontual, mas baixa resumibilidade de ponta a ponta

**Descrição.** O produto já tem ilhas de resiliência: retry por linha no batch Bronze, retomada de pipeline Gold estagnado, retry de `partial_failure` no ETL e reaproveitamento idempotente de commit bem-sucedido. Mas isso ainda não vira uma experiência realmente contínua de “sessão de importação”: não há evidência de persistência do rascunho do batch antes do envio, de recuperação do estado do ETL antes do commit após refresh do navegador ou de uma visão única de histórico operacional por operação. fileciteturn28file0L1-L1 fileciteturn31file0L1-L1 fileciteturn33file0L1-L1 fileciteturn43file0L1-L1

**Onde ocorre no fluxo.** Especialmente no batch Bronze e no ETL preview/commit.  

**Impacto.** Em operação, o usuário depende demais da continuidade da sessão do navegador. Em UX, isso aumenta ansiedade em processos longos. Em negócio, dificulta escalar o fluxo para operadores que trabalham com interrupções, pausas e retomadas.  

**Severidade.** Média.  

**Probabilidade de ocorrência.** Média.  

**Sugestão de melhoria.** Modelar uma sessão de importação persistente, com estados explícitos, drafts salvos, retomada por usuário e timeline de passos concluídos. Isso aproxima o produto de um padrão de “wizard operacional”, não de uma tela multiuso. fileciteturn32file0L1-L1 fileciteturn41file0L1-L1

### Segurança de arquivo tem base razoável, mas ainda não está em defesa em profundidade

**Descrição.** O repositório mostra validações reais de tipo e conteúdo, inclusive rejeição de `.txt`, `.xlsx` inválido e ZIP disfarçado de XLSX nos testes. Isso é bom. Mas eu não encontrei evidência, no material inspecionado, de antivírus, sandbox, CDR, quarentena separada ou storage isolado para uploads; além disso, o modelo Bronze guarda o binário no próprio banco. Em comparação com as recomendações da entity["organization","OWASP","app security foundation"], o fluxo parece cobrir allowlist de extensão e limite de upload, mas ainda não mostra uma estratégia mais profunda de contenção de arquivo potencialmente malicioso. fileciteturn29file0L1-L1 fileciteturn38file0L1-L1 citeturn0view3

**Onde ocorre no fluxo.** Upload Bronze e preview ETL.  

**Impacto.** Em segurança, aumenta o risco residual de parser abuse, payload malformado ou uso indevido de storage. Em governança, concentrar binário no banco também amplia o raio de impacto de backup, replicação e incidentes.  

**Severidade.** Média.  

**Probabilidade de ocorrência.** Média.  

**Sugestão de melhoria.** Adotar defesa em profundidade para upload: storage externo, checagem de assinatura do arquivo, isolamento/quarentena, observabilidade de rejeições por motivo e, se o risco operacional justificar, varredura antimalware. Isso segue o padrão recomendado pela OWASP para upload seguro. citeturn0view3

## Oportunidades de melhoria

### Quick wins

O ganho mais imediato está em clareza, confirmação e feedback. Eu priorizaria: separar visualmente os modos Bronze e ETL logo na entrada; trocar a copy do Bronze para deixar explícito que o lote é criado antes da revisão; transformar o hint por hash em sugestão confirmável; exibir resumo claro do que foi autofillado; adicionar preview de erros mais acionável no ETL; e tornar o resultado de merge/upsert mais explicativo, dizendo não só quantos registros foram atualizados, mas também quantos campos foram preservados por política. Tudo isso cabe em backlog de UX/produto sem reescrever a arquitetura. fileciteturn32file0L1-L1 fileciteturn33file0L1-L1 fileciteturn24file0L1-L1

Também há quick wins de operação: exportar CSV com linhas rejeitadas no ETL; mostrar no Bronze um “pré-check” de cabeçalho e colunas antes do upload real; destacar quando `max_scan_rows` pode ser útil; e exibir, no batch, uma noção mais clara de progresso agregado do workspace, não apenas contadores estáticos por status. fileciteturn25file0L1-L1 fileciteturn33file0L1-L1 fileciteturn34file0L1-L1

### Melhorias de médio prazo

No médio prazo, eu consolidaria a governança. Isso significa: colocar `owner` e expiração nas sessões ETL; criar uma trilha de auditoria formal para preview, commit, retry e retomada; adicionar uma entidade pai para batchs múltiplos; e melhorar a rastreabilidade de “quem importou, quando, com quais parâmetros e qual foi o resultado final por arquivo e por sessão”. Hoje parte disso existe de forma fragmentada em `LeadBatch`, em logs e em `LeadImportEtlPreviewSession`, mas não como uma auditoria operacional unificada. fileciteturn21file0L1-L1 fileciteturn22file0L1-L1 fileciteturn38file0L1-L1 fileciteturn41file0L1-L1

Também vale reorganizar a experiência do batch. Em vez de um grid puramente técnico, o produto deveria permitir metadados compartilhados por seleção em massa, agrupamento por evento/origem, e um mecanismo de “aplicar para todos” com exceções por linha. Isso reduz esforço manual e melhora throughput operacional sem abrir mão do controle fino. fileciteturn34file0L1-L1 fileciteturn35file0L1-L1

### Melhorias estruturais e arquiteturais

As mudanças mais importantes são arquiteturais. A principal é sair de um desenho predominantemente síncrono e baseado em payloads/JSON grandes no banco para um desenho de ingestão assíncrona: upload para storage, criação de sessão, parsing/preview em fila, commit em job idempotente, progresso incremental e armazenamento temporário com TTL para artefatos intermediários. Isso reduz timeouts, desacopla UX de I/O pesado e melhora escalabilidade. fileciteturn36file0L1-L1 fileciteturn38file0L1-L1 fileciteturn41file0L1-L1

A segunda mudança estrutural é unificar semanticamente Bronze e ETL sob um mesmo modelo de “sessão de importação”, mantendo caminhos diferentes de validação, mas com contrato operacional consistente: `draft -> preview -> confirm -> process -> audit`. Hoje o sistema já sugere essa direção, mas metade da experiência ainda é “wizard transacional” e metade é “shell técnico”. Fechar essa lacuna deixaria o produto muito mais robusto e mais fácil de operar. fileciteturn32file0L1-L1 fileciteturn42file0L1-L1

## Riscos críticos

O risco mais perigoso hoje é **importar ou associar dados corretos ao contexto errado**, especialmente em Bronze, onde o lote é criado antes de uma revisão real do conteúdo e onde o hint por hash pode reaplicar metadados anteriores com pouca fricção visível. Se evento, origem do lote ou ativação forem herdados indevidamente, o problema deixa de ser apenas técnico e vira erro analítico e operacional em cascata. fileciteturn32file0L1-L1 fileciteturn36file0L1-L1

O segundo risco crítico é **degradação de performance e custo operacional com volume**, porque o desenho atual concentra binário bruto, snapshots ETL e payloads JSON no banco, além de depender de leitura integral de arquivo tanto no navegador quanto no backend. Isso tende a piorar justamente quando a operação precisar subir mais arquivos ou arquivos maiores. fileciteturn36file0L1-L1 fileciteturn38file0L1-L1 fileciteturn41file0L1-L1

O terceiro risco é **governança insuficiente no ETL**, porque a sessão de preview não carrega explicitamente o usuário dono nem uma política de expiração evidente no modelo. Isso fragiliza auditoria e pode gerar ambiguidades sérias em cenários multiusuário ou de retry operacional. fileciteturn23file0L1-L1 fileciteturn41file0L1-L1

O quarto risco é **falsa sensação de atualização**, causada pela política de merge não destrutivo. O fluxo pode retornar sucesso operacional enquanto preserva dados antigos sem deixar isso transparente para quem importou, o que gera divergência silenciosa entre expectativa do operador e estado real da base. fileciteturn24file0L1-L1 fileciteturn42file0L1-L1

O quinto risco é **fragmentação operacional do batch**, porque uma importação multiarquivo se transforma em vários `LeadBatch` independentes, espalhando o controle entre grid, query params, mapeamento unificado, pipeline individual e retomadas pontuais. Isso ainda funciona em escala pequena, mas tende a ficar caro de operar e difícil de auditar conforme o uso crescer. fileciteturn34file0L1-L1 fileciteturn35file0L1-L1

## Priorização final

A ordem recomendada de implementação é esta:

1. **Introduzir revisão antes da persistência no Bronze.** Esse é o maior redutor de erro humano no curto prazo, porque aproxima o Bronze do padrão mais seguro que o próprio ETL já usa. fileciteturn32file0L1-L1 fileciteturn42file0L1-L1

2. **Tornar o hint por hash explícito e confirmável.** Alto impacto, esforço relativamente baixo e redução direta do risco de contexto errado. fileciteturn32file0L1-L1 fileciteturn36file0L1-L1

3. **Adicionar auditoria e ownership às sessões ETL.** É prioridade alta porque fecha a maior lacuna de governança e segurança do fluxo preview/commit. fileciteturn23file0L1-L1 fileciteturn41file0L1-L1

4. **Enriquecer o ETL com drilldown operacional de erros.** Isso eleva muito a taxa de correção em primeira tentativa e reduz custo operacional de suporte. fileciteturn26file0L1-L1 fileciteturn33file0L1-L1

5. **Criar entidade pai para batch multiarquivo.** Esse é o passo mais importante para manter o modo batch sustentável. fileciteturn34file0L1-L1 fileciteturn38file0L1-L1

6. **Migrar binários e snapshots pesados para storage temporário/externo.** Alto impacto técnico e operacional, especialmente para escala e custo. fileciteturn38file0L1-L1 fileciteturn41file0L1-L1

7. **Passar parsing/preview/commit pesado para fila assíncrona com progresso incremental.** Essa é a grande mudança arquitetural que prepara o fluxo para arquivos maiores e menor acoplamento a timeouts. fileciteturn36file0L1-L1

8. **Reorganizar a navegação do shell em jornadas separadas por intenção.** Depois de estabilizar risco e governança, vale simplificar profundamente a experiência. fileciteturn32file0L1-L1 fileciteturn33file0L1-L1

9. **Tornar a política de merge visível e configurável em cenários controlados.** Importante para qualidade e confiança na base, mas fica depois de corrigir fricções mais críticas. fileciteturn24file0L1-L1 fileciteturn42file0L1-L1

10. **Adicionar defesa em profundidade de upload.** É relevante, mas eu colocaria depois das lacunas estruturais de fluxo, storage e auditoria, a menos que os arquivos venham de fontes externas de maior risco. fileciteturn38file0L1-L1 citeturn0view3

Os pontos que eu validaria em seguida, antes de transformar tudo em backlog fechado, são: comportamento real da tela em `localhost`, tempos reais de upload/preview/commit em arquivos de diferentes tamanhos, cardinalidade e crescimento das tabelas `lead_batches` e `lead_import_etl_preview_session`, cobertura de logs correlacionáveis por usuário/operação, e regras reais de autorização nos endpoints de lote, preview e commit. Esses itens não invalidam o diagnóstico; eles refinam prioridade, sizing e desenho de implementação. fileciteturn38file0L1-L1 fileciteturn41file0L1-L1