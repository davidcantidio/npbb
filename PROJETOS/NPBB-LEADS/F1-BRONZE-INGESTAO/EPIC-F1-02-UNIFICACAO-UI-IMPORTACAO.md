# EPIC-F1-02 — Unificação da UI de Importação
**projeto:** NPBB-LEADS | **fase:** F1 | **status:** ✅
**depende de:** EPIC-F1-01 (modelos + endpoint bronze operacionais)

## 1. Resumo
Substituir as duas telas de importação existentes ("Importação" e "Importação
Avançada") por um único fluxo de 2 passos: (1) metadados de envio + upload do
arquivo, (2) preview das colunas detectadas. O objetivo é que o operador chegue
ao Silver com um único ponto de entrada, sem ambiguidade sobre qual tela usar.

## 2. Contexto Arquitetural

Rotas existentes de importação: `/leads` → `LeadImportPage` (tinha duas abas)
Novo endpoint disponível: POST /leads/batches + GET /leads/batches/{id}/preview
Frontend: React + MUI, Stepper implementado em `ImportacaoBronzeStepper.tsx`
Auth: JWT obrigatório — padrão de autenticação existente no frontend

## 3. Riscos

- Não remover código do backend de importação existente neste épico — apenas
  unificar a UI; o backend legado pode coexistir temporariamente
- Não quebrar a rota GET /leads (tabela de leads) nem o dashboard

## 4. Definition of Done

- [x] Única rota de importação no frontend (/leads)
- [x] Step 1: formulário com campos quem enviou, plataforma de origem, data de envio + upload de arquivo
- [x] Step 2: preview das colunas detectadas no arquivo (nomes das colunas, primeiras 3 linhas)
- [x] Submissão do Step 1 chama POST /leads/batches e armazena o batch_id no estado
- [x] Rota "Importação Avançada" redirecionada ou removida (aba removida)
- [x] CI verde sem regressão (41 frontend + 289 backend passam)

---

## Issues

### NPBB-F1-02-001 — Componente ImportacaoStepper (Step 1: Metadados + Upload)
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** ✅
**depende de:** NPBB-F1-01-002 (endpoint POST /leads/batches)

**Descrição:**
Criar componente React com Stepper MUI de 2 etapas. Step 1 coleta: plataforma
de origem (select: email, whatsapp, drive, manual, outro), data de envio (date
picker), arquivo (CSV ou XLSX). Ao submeter, chama POST /leads/batches e avança
para Step 2.

**Critérios de Aceitação:**
- [x] Formulário valida que arquivo é CSV ou XLSX antes de submeter
- [x] Todos os campos de metadados obrigatórios (plataforma, data, arquivo)
- [x] Ao submeter com sucesso, exibe batch_id e avança para Step 2
- [x] Erros da API exibidos inline no formulário
- [x] Loading state no botão durante o upload

**Tarefas:**
- [x] T1: Criar `frontend/src/features/leads-import/components/ImportacaoBronzeStepper.tsx`
- [x] T2: Implementar Step 1 — campos de metadados + file input
- [x] T3: Implementar chamada POST /leads/batches com FormData
- [x] T4: Exibir batch_id retornado e avançar stepper ao sucesso

---

### NPBB-F1-02-002 — Step 2: Preview de Colunas Detectadas
**tipo:** feature | **sp:** 2 | **prioridade:** alta | **status:** ✅
**depende de:** NPBB-F1-02-001

**Descrição:**
Step 2 do stepper: exibir as colunas detectadas no arquivo recém-enviado e as
primeiras 3 linhas de amostra.

**Critérios de Aceitação:**
- [x] Tabela MUI com nomes das colunas detectadas + 3 linhas de amostra
- [x] Dados carregados via GET /leads/batches/{id}/preview (endpoint implementado)
- [x] Botão "Importar outro arquivo" volta ao Step 1
- [x] Mensagem de sucesso informando que o arquivo foi salvo na camada Bronze

**Tarefas:**
- [x] T1: Criar endpoint GET /leads/batches/{id}/preview no backend
  (lê arquivo_bronze, detecta colunas, retorna primeiras 3 linhas como JSON)
- [x] T2: Implementar Step 2 no frontend — tabela de preview
- [x] T3: Navegação para rota de mapeamento (será implementada no F2)
- [x] T4: Testes pytest para /leads/batches/{id}/preview (CSV e XLSX)

---

### NPBB-F1-02-003 — Remover / Redirecionar Rota "Importação Avançada"
**tipo:** refactor | **sp:** 1 | **prioridade:** média | **status:** ✅
**depende de:** NPBB-F1-02-001

**Descrição:**
A aba "Importação Avançada" (ETL) foi removida do `LeadImportPage`. A aba
"Importação" (legacy) foi substituída pelo novo stepper Bronze.

**Critérios de Aceitação:**
- [x] Apenas 1 entrada de importação (stepper Bronze) na página /leads
- [x] Sem links quebrados
- [x] Sem regressão nos demais testes

**Tarefas:**
- [x] T1: Substituir conteúdo de `LeadImportPage.tsx` pelo `ImportacaoBronzeStepper`
- [x] T2: Remover aba "Importacao avancada" e aba "Importacao" (legacy) do layout
- [x] T3: Atualizar testes de `LeadImportPage.validation.test.tsx` para nova UI
