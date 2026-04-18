# Handoff Técnico: Batch Bronze Incremental para Multi-Upload de Leads

Data: 2026-04-17

## 1. Resumo executivo

### Objetivo da entrega

Implementar o recorte incremental do plano de multi-upload no fluxo Bronze de `/leads/importar`, sem introduzir `ImportSession`, sem consolidar o fluxo até a Super Base e sem alterar o contrato público principal do backend. A decisão de arquitetura mantida foi: cada arquivo continua gerando um `LeadBatch` independente, com mapeamento e pipeline seguindo por `batch_id`.

### O que foi implementado

- Novo submodo `batch` dentro do fluxo Bronze, coexistindo com `single` e com o fluxo `etl`.
- Grade de upload com uma linha editável por arquivo selecionado.
- Estado local por linha com os campos planejados:
  - `local_id`
  - `file`
  - `file_name`
  - `quem_enviou`
  - `plataforma_origem`
  - `data_envio`
  - `evento_id`
  - `origem_lote`
  - `tipo_lead_proponente`
  - `ativacao_id`
  - `status_ui`
  - `created_batch_id`
  - `error_message`
- Reuso de dependências existentes por linha:
  - autocomplete de evento via `listReferenciaEventos`
  - quick create de evento via `QuickCreateEventoModal` com `criar_ativacao_padrao_bb: true`
  - listagem/criação de ativações via `listEventoAtivacoes` e `createEventoAtivacao`
  - desbloqueio de importação por ativação via `updateEvento` + `listAgencias`
- Submit batch com:
  - validação por linha
  - envio individual por arquivo usando o contrato atual de `createLeadBatch`
  - concorrência limitada a `3`
  - sucesso parcial preservado
  - retry de linha com erro
- Ação por linha criada para abrir o fluxo atual em `?step=mapping&batch_id=<id>`.

### Problemas resolvidos

- O shell de importação não suportava múltiplos arquivos no Bronze.
- O fluxo anterior era modelado para um único upload por vez.
- Não existia coordenação de dependências por linha para evento, ativação e agência.
- Não existia retry granular por linha nem submit com sucesso parcial.
- O editor inline de agência no batch ficava desabilitado indevidamente no fluxo testado, mesmo após o carregamento de agências.

### Estado geral da entrega

O escopo funcional planejado para `Batch Bronze completo` foi entregue no frontend, com manutenção do contrato atual do backend. A suíte automatizada da página de importação passou integralmente. Permanecem, no entanto, fragilidades assíncronas e de tratamento de erro identificadas em revisão técnica posterior; elas não impedem o uso básico do fluxo, mas devem ser atacadas na próxima etapa.

## 2. Alterações realizadas

### Arquivos alterados

- `frontend/src/pages/leads/ImportacaoPage.tsx`
- `frontend/src/pages/leads/importacao/ImportacaoUploadStep.tsx`
- `frontend/src/pages/leads/importacao/constants.ts`
- `frontend/src/pages/leads/importacao/batch/useBatchUploadDraft.ts`
- `frontend/src/pages/leads/importacao/batch/BatchUploadTable.tsx`
- `frontend/src/pages/leads/importacao/batch/BatchUploadRow.tsx`
- `frontend/src/pages/leads/importacao/batch/InlineEventoAgencyEditor.tsx`
- `frontend/src/pages/__tests__/ImportacaoPage.test.tsx`

### Componentes, serviços e fluxos impactados

#### Frontend

- `ImportacaoPage`
  - passou a orquestrar `single`, `batch` e `etl`
  - incorporou o estado `bronzeMode`
  - passou a rotear o quick-create de evento para bronze simples, ETL ou linha específica do batch
- `ImportacaoUploadStep`
  - passou a renderizar o grid batch no Bronze
  - preservou o shell atual de Bronze simples e ETL
- `BatchUploadTable`
  - tabela principal do batch
  - seleção múltipla de arquivos
  - resumo de status
  - botão de submit em lote
- `BatchUploadRow`
  - edição por linha
  - integração com evento, ativação, agência, retry e handoff para mapping
- `InlineEventoAgencyEditor`
  - preenchimento inline de `agencia_id` quando o evento bloqueia importação por ativação
- `useBatchUploadDraft`
  - hook central de estado e side effects do batch

#### Serviços reutilizados

- `createLeadBatch`
- `listReferenciaEventos`
- `listEventoAtivacoes`
- `createEventoAtivacao`
- `updateEvento`
- `listAgencias`
- `QuickCreateEventoModal` / `createEvento`

### Endpoints impactados

Não houve criação de endpoints novos nesta entrega.

Endpoints reutilizados pelo fluxo:

- `POST /leads/batches`
- `GET /leads/referencias/eventos`
- `GET /evento/{eventoId}/ativacoes`
- `POST /evento/{eventoId}/ativacoes`
- `PUT /evento/{eventoId}`
- `GET /agencias/`

### Regras de negócio adicionadas ou modificadas

- Bronze agora suporta `bronzeMode = "single" | "batch"`.
- Cada arquivo do batch gera um `LeadBatch` independente.
- Defaults de linha:
  - `quem_enviou = user.email`
  - `data_envio = hoje`
  - `status_ui = "draft"`
- `origem_lote = "ativacao"`:
  - exige `evento_id`
  - exige `ativacao_id`
  - depende de evento elegível para importação por ativação
- Evento sem `agencia_id`:
  - mostra editor inline de agência
  - após `updateEvento`, recalcula elegibilidade sem sair do shell
- Submit batch:
  - valida linha a linha
  - envia apenas linhas válidas
  - não faz rollback global
  - permite retry individual

### Trade-offs assumidos explicitamente

- Não foi criado backend agregador para múltiplos arquivos.
- Não foi introduzido `ImportSession`.
- Não foi criado mapeamento unificado entre arquivos.
- O handoff para mapping continua por `batch_id`, um lote por arquivo.
- O estado batch ficou inteiramente no frontend, em hook local, por ser o caminho mais curto e compatível com a arquitetura atual.

## 3. Causa raiz e correções

### Problema tratado 1: ausência de modo batch no shell Bronze

- Causa raiz identificada:
  - o fluxo de upload estava acoplado a um único arquivo e a um único conjunto de metadados de Bronze.
- Ponto exato:
  - `frontend/src/pages/leads/ImportacaoPage.tsx`
  - `frontend/src/pages/leads/importacao/ImportacaoUploadStep.tsx`
- Correção aplicada:
  - adição de `bronzeMode`
  - extração do batch para componentes próprios sob `frontend/src/pages/leads/importacao/batch/`
  - manutenção de `ImportacaoPage` como orquestrador
- Por que essa correção foi escolhida:
  - preserva o shell atual
  - minimiza regressão em `single` e `etl`
  - evita redesenho prematuro do backend

### Problema tratado 2: inexistência de estado por linha para múltiplos arquivos

- Causa raiz identificada:
  - o modelo anterior não suportava persistir metadados independentes por arquivo dentro da mesma interação.
- Ponto exato:
  - `frontend/src/pages/leads/importacao/batch/useBatchUploadDraft.ts`
- Correção aplicada:
  - criação do tipo `BatchUploadRowDraft`
  - criação do hook `useBatchUploadDraft` para encapsular:
    - linhas
    - remoção
    - atualização
    - submit
    - retry
    - side effects de ativação/agência
- Por que essa correção foi escolhida:
  - centraliza a regra de negócio do batch
  - evita espalhar estado e efeitos entre vários componentes
  - permite evolução incremental sem tocar no backend

### Problema tratado 3: inexistência de dependências por linha para ativação e agência

- Causa raiz identificada:
  - o fluxo anterior carregava dependências apenas para o modo single, sem noção de linha.
- Ponto exato:
  - `frontend/src/pages/leads/importacao/batch/useBatchUploadDraft.ts`
  - `frontend/src/pages/leads/importacao/batch/BatchUploadRow.tsx`
  - `frontend/src/pages/leads/importacao/batch/InlineEventoAgencyEditor.tsx`
- Correção aplicada:
  - carga lazy de ativações por `evento_id`
  - editor inline de agência para eventos sem `agencia_id`
  - criação inline de ativação quando o evento não tem ativações
  - recálculo do evento de referência local após `updateEvento`
- Por que essa correção foi escolhida:
  - reutiliza serviços existentes
  - mantém o usuário no mesmo shell
  - resolve o caso operacional sem criar novas APIs

### Problema tratado 4: submit all-or-nothing

- Causa raiz identificada:
  - o fluxo anterior assumia um único upload e não tinha necessidade de granularidade por linha.
- Ponto exato:
  - `frontend/src/pages/leads/importacao/batch/useBatchUploadDraft.ts`
- Correção aplicada:
  - validação por linha
  - `runWithConcurrency(..., 3, ...)`
  - estados `draft | submitting | created | error`
  - `retryRow(localId)`
- Por que essa correção foi escolhida:
  - atende ao requisito funcional com baixa complexidade
  - protege a UX contra falhas parciais
  - evita sobrecarga desnecessária no backend

### Problema tratado 5: editor inline de agência permanecia desabilitado

- Causa raiz identificada:
  - o botão `Salvar agencia` dependia de estado de loading residual e não apenas da disponibilidade real de opções selecionáveis.
- Ponto exato:
  - `frontend/src/pages/leads/importacao/batch/InlineEventoAgencyEditor.tsx`
- Correção aplicada:
  - separação entre “há agências carregadas” e “request ainda está marcada como loading”
  - cálculo de `resolvedAgenciaId`
  - habilitação do CTA baseada em `hasAgencias` + seleção resolvida, e não apenas em `loading`
- Por que essa correção foi escolhida:
  - era a menor correção efetiva para destravar o fluxo
  - eliminou o falso bloqueio que quebrava o teste focado
  - manteve o componente simples

## 4. Validação realizada

### Testes automatizados executados

Executado em `frontend/`:

```powershell
npm run test -- ImportacaoPage.test.tsx --run
```

Resultado final:

- `19 passed`

Teste focado também executado durante depuração:

```powershell
npm run test -- ImportacaoPage.test.tsx --run -t "shows the inline agency editor in batch mode and unlocks activation import after updateEvento"
```

### Cenários cobertos por teste automatizado

- renderização do shell Bronze canônico
- validação de campos obrigatórios no Bronze simples
- envio de lote single e preview Bronze
- envio `origem_lote = ativacao` no modo single
- bloqueio de envio por ativação sem `ativacao_id`
- criação rápida de evento no Bronze simples
- criação ad hoc de ativação no Bronze simples
- batch:
  - criação de uma linha por arquivo selecionado
  - preenchimento inline de agência e desbloqueio da importação por ativação
  - criação inline de ativação
  - submit de linha `ativacao`
  - sucesso parcial com retry apenas da linha com erro
- navegação para mapping preservando `batch_id`
- retomada de mapping e avanço para pipeline
- retorno para novo upload a partir do pipeline
- fluxo ETL:
  - preview com exigência de cabeçalho
  - quick-create de evento
  - confirmação de commit com warnings

### Evidências de que a correção funcionou

- o fluxo batch passou a ser renderizado e exercitado em testes
- o caso de editor inline de agência, que estava falhando, passou no teste focado e na suíte completa
- a suíte de `ImportacaoPage` permaneceu verde, indicando ausência de regressão imediata no shell `single` e no fluxo `etl`

### Validação manual

- Não houve validação manual em browser nesta etapa.
- A evidência principal desta entrega é automatizada, via testes de interface da página.

## 5. Pendências e limitações

### Pendências ainda não resolvidas

As implementações entregues foram revisadas tecnicamente depois, e os seguintes pontos ficaram pendentes:

1. Fragilidade assíncrona no carregamento de agências
- Arquivo: `frontend/src/pages/leads/importacao/batch/useBatchUploadDraft.ts`
- O efeito de `listAgencias` ainda pode sofrer cancelamento prematuro quando `rows` ou `eventos` mudam durante uma request em andamento.

2. Criação de ativação com refresh acoplado
- Arquivos:
  - `frontend/src/pages/leads/importacao/batch/useBatchUploadDraft.ts`
  - `frontend/src/pages/leads/ImportacaoPage.tsx`
- Se `createEventoAtivacao` funcionar e `listEventoAtivacoes` falhar, a UI trata a operação como erro total, apesar da ativação já existir no backend.

3. Tratamento de erro insuficiente no batch inline
- Arquivos:
  - `frontend/src/pages/leads/importacao/batch/BatchUploadRow.tsx`
  - `frontend/src/pages/leads/importacao/batch/InlineEventoAgencyEditor.tsx`
- Erros de `onCreateAtivacao` e `onSaveAgency` não são convertidos em feedback claro por linha.

4. Sessão expirada degradando linhas já criadas
- Arquivo: `frontend/src/pages/leads/importacao/batch/useBatchUploadDraft.ts`
- O branch `!token` ainda pode marcar linhas criadas como erro.

5. Erro ao carregar ativações tratado como lista vazia
- Arquivos:
  - `frontend/src/pages/leads/importacao/batch/useBatchUploadDraft.ts`
  - `frontend/src/pages/leads/importacao/batch/BatchUploadRow.tsx`
  - `frontend/src/pages/leads/importacao/ImportacaoUploadStep.tsx`
- Isso pode induzir criação duplicada de ativação.

6. Auto-seleção implícita da primeira agência
- Arquivo: `frontend/src/pages/leads/importacao/batch/InlineEventoAgencyEditor.tsx`
- Hoje a primeira agência carregada é assumida como seleção inicial.

7. Geração de data baseada em UTC
- Arquivo: `frontend/src/pages/leads/ImportacaoPage.tsx`
- `new Date().toISOString().slice(0, 10)` pode gerar data deslocada em relação ao fuso local.

### Limitações desta etapa

- Não houve verificação manual em ambiente real com backend e dados reais de evento/ativação.
- O batch continua sendo estritamente frontend-driven.
- O fluxo ainda não contempla sessão consolidada ou agrupamento lógico entre lotes.

### Limitações de ambiente

- O workspace está sujo com muitas mudanças não relacionadas ao fluxo de importação.
- O handoff foi produzido sem normalizar ou limpar o restante do worktree.

## 6. Riscos de regressão

### Fluxos que podem ter sido impactados

- Bronze single
- shell de mapping
- shell de pipeline
- quick-create de evento compartilhado entre Bronze e ETL
- fluxo ETL dentro de `ImportacaoPage`

### Dependências sensíveis

- `QuickCreateEventoModal`
  - agora é reaproveitado por três contextos:
    - bronze simples
    - ETL
    - linha do batch
- `listReferenciaEventos`
  - alimenta os três modos
- `listEventoAtivacoes` / `createEventoAtivacao`
  - comportamento compartilhado entre single e batch
- `updateEvento`
  - agora passou a participar diretamente do fluxo de importação

### Comportamentos que merecem revalidação específica

- mudança de `origem_lote` entre `proponente` e `ativacao`
- troca de evento depois de já haver `ativacao_id` preenchido
- uso de quick-create em sequência, em linhas diferentes
- submit batch com várias linhas apontando para o mesmo evento
- timeout e erro de rede durante:
  - carga de agências
  - carga de ativações
  - criação de ativação
  - atualização de agência

## 7. Próximo passo recomendado

### Próxima ação mais importante

Endurecer o fluxo batch contra falhas assíncronas e de rede antes de expandir escopo funcional.

### Por que essa etapa vem agora

O fluxo principal foi entregue, mas os riscos pendentes não são cosméticos:

- podem gerar estado inconsistente na UI
- podem induzir ações duplicadas do usuário
- podem mascarar sucesso parcial como erro total
- podem transformar erros de infraestrutura em decisões erradas de negócio

### Impacto esperado

- maior confiabilidade do batch em ambiente real
- menor chance de duplicidade de ativação
- UX mais previsível em erro parcial
- base mais segura para futura evolução para sessão consolidada

### Arquivos e fluxos a investigar em seguida

Prioridade 1:

- `frontend/src/pages/leads/importacao/batch/useBatchUploadDraft.ts`
- `frontend/src/pages/leads/importacao/batch/InlineEventoAgencyEditor.tsx`
- `frontend/src/pages/leads/importacao/batch/BatchUploadRow.tsx`

Prioridade 2:

- `frontend/src/pages/leads/ImportacaoPage.tsx`
- `frontend/src/pages/__tests__/ImportacaoPage.test.tsx`

### Escopo recomendado da próxima etapa

- corrigir a race de `listAgencias`
- desacoplar sucesso de `createEventoAtivacao` do refresh posterior
- introduzir erro por linha para operações inline
- diferenciar “erro de carga” de “lista vazia” para ativações
- corrigir o branch `!token`
- adicionar testes cobrindo esses cenários

## 8. Instruções práticas para o próximo agente

### Onde continuar

Começar por:

- `frontend/src/pages/leads/importacao/batch/useBatchUploadDraft.ts`
- `frontend/src/pages/leads/importacao/batch/InlineEventoAgencyEditor.tsx`
- `frontend/src/pages/leads/importacao/batch/BatchUploadRow.tsx`
- `frontend/src/pages/__tests__/ImportacaoPage.test.tsx`

### O que observar com atenção

- qualquer efeito com cleanup que possa cancelar requests em andamento
- diferenças entre:
  - “não há dados”
  - “falha ao carregar dados”
  - “operação concluiu parcialmente”
- pontos onde exceções sobem sem conversão para feedback de UI
- campos que hoje são inferidos automaticamente e podem introduzir dado incorreto

### Armadilhas a evitar

- não criar endpoint novo sem necessidade real
- não introduzir `ImportSession` nesta etapa
- não quebrar o fluxo `single` ao endurecer o `batch`
- não tratar lista vazia como sinônimo de erro, nem erro como sinônimo de lista vazia
- não reverter mudanças não relacionadas do worktree

### Hipóteses já descartadas

- não há necessidade de nova rota para viabilizar o batch incremental
- o contrato atual de `POST /leads/batches` já suporta os campos necessários
- o problema do editor inline de agência não era apenas do teste; havia bloqueio real de enablement na UI
- o handoff para mapping continua corretamente centrado em `batch_id`; não houve necessidade de sessão agregadora nesta fase

### Teste de regressão mínimo recomendado antes de seguir

Rodar novamente:

```powershell
cd frontend
npm run test -- ImportacaoPage.test.tsx --run
```

Se houver mudança na lógica assíncrona, adicionar explicitamente testes para:

- falha de `listAgencias`
- falha de `listEventoAtivacoes`
- sucesso de `createEventoAtivacao` seguido de falha no refresh
- erro em `updateEvento`
- submit com `token = null` quando há linhas já criadas

