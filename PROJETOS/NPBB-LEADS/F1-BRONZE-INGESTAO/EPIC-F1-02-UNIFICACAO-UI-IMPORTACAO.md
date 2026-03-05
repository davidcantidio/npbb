EPIC-F1-02 — Unificação da UI de Importação
projeto: NPBB-LEADS | fase: F1 | status: ✅
depende de: EPIC-F1-01 (modelos + endpoint bronze operacionais)

1. Resumo
Substituir as duas telas de importação existentes ("Importação" e "Importação
Avançada") por um único fluxo de 2 passos: (1) metadados de envio + upload do
arquivo, (2) preview das colunas detectadas. O objetivo é que o operador chegue
ao Silver com um único ponto de entrada, sem ambiguidade sobre qual tela usar.
2. Contexto Arquitetural

Rotas existentes de importação: identificar em frontend/src/ as rotas que
devem ser unificadas ou redirecionadas
Novo endpoint disponível: POST /leads/batches (criado no EPIC-F1-01)
Frontend: React + MUI, padrão de formulário com stepper já usado em outros
fluxos do projeto
Auth: JWT obrigatório — usar o padrão de autenticação existente no frontend

3. Riscos

Não remover código do backend de importação existente neste épico — apenas
unificar a UI; o backend legado pode coexistir temporariamente
Não quebrar a rota GET /leads (tabela de leads) nem o dashboard

4. Definition of Done

 Única rota de importação no frontend (/leads/importar ou equivalente)
 Step 1: formulário com campos quem enviou, plataforma de origem, data de envio + upload de arquivo
 Step 2: preview das colunas detectadas no arquivo (nomes das colunas, primeiras 3 linhas)
 Submissão do Step 1 chama POST /leads/batches e armazena o batch_id no estado
 Rota "Importação Avançada" redirecionada ou removida
 CI verde sem regressão


Issues
NPBB-F1-02-001 — Componente ImportacaoStepper (Step 1: Metadados + Upload)
tipo: feature | sp: 3 | prioridade: alta | status: ✅
depende de: NPBB-F1-01-002 (endpoint POST /leads/batches)
Descrição:
Criar componente React com Stepper MUI de 2 etapas. Step 1 coleta: quem enviou
(select de usuários ou input livre), plataforma de origem (select: email,
whatsapp, drive, manual, outro), data de envio (date picker), arquivo (CSV ou
XLSX). Ao submeter, chama POST /leads/batches e avança para Step 2.
Critérios de Aceitação:

- [x] Formulário valida que arquivo é CSV ou XLSX antes de submeter
- [x] Todos os campos de metadados obrigatórios (quem enviou, plataforma, data, arquivo)
- [x] Ao submeter com sucesso, exibe batch_id e avança para Step 2
- [x] Erros da API exibidos inline no formulário
- [x] Loading state no botão durante o upload

Tarefas:

- [x] T1: Criar frontend/src/pages/leads/ImportacaoPage.tsx com MUI Stepper
- [x] T2: Implementar Step 1 — campos de metadados + file input
- [x] T3: Implementar chamada POST /leads/batches com FormData
- [x] T4: Exibir batch_id retornado e avançar stepper ao sucesso


NPBB-F1-02-002 — Step 2: Preview de Colunas Detectadas
tipo: feature | sp: 2 | prioridade: alta | status: ✅
depende de: NPBB-F1-02-001
Descrição:
Step 2 do stepper: exibir as colunas detectadas no arquivo recém-enviado e as
primeiras 3 linhas de amostra. Não persiste nada — é apenas confirmação visual
de que o arquivo foi lido corretamente antes de avançar ao mapeamento (F2).
O botão "Avançar para Mapeamento" navega para a rota de mapeamento (F2) passando
o batch_id.
Critérios de Aceitação:

- [x] Tabela MUI com nomes das colunas detectadas + 3 linhas de amostra
- [x] Dados carregados via GET /leads/batches/{id}/preview
- [x] Botão "Avançar para Mapeamento" navega com batch_id
- [x] Botão "Cancelar" volta ao Step 1

Tarefas:

- [x] T1: Endpoint `GET /leads/batches/{id}/preview` validado no backend
- [x] T2: Implementar Step 2 no frontend — tabela de preview
- [x] T3: Navegação para rota de mapeamento (handoff para F2)
- [x] T4: Cobertura de backend para `/leads/batches/{id}/preview` existente em `backend/tests/test_lead_batch_endpoints.py`


NPBB-F1-02-003 — Remover / Redirecionar Rota "Importação Avançada"
tipo: refactor | sp: 1 | prioridade: média | status: ✅
depende de: NPBB-F1-02-001
Descrição:
Identificar a rota "Importação Avançada" no frontend e redirecioná-la para a
nova rota unificada. Remover o item de menu duplicado.
Critérios de Aceitação:

- [x] Apenas 1 entrada de "Importação" no menu lateral
- [x] Acesso à rota antiga redireciona para nova rota
- [x] Sem links quebrados

Tarefas:

- [x] T1: Identificar rotas de importação existentes no router do frontend
- [x] T2: Adicionar redirect da rota antiga para nova
- [x] T3: Remover item duplicado do menu lateral