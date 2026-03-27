---
doc_id: "TASK-4.md"
user_story_id: "US-3-03-UI-CONFIGURACAO-CATEGORIAS-POR-EVENTO"
task_id: "T4"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T3"
parallel_safe: false
write_scope:
  - "frontend/src/pages/AtivosList.tsx"
tdd_aplicavel: false
---

# TASK-4 - Distincao compreensivel entre categoria e modo de fornecimento na UI

## objetivo

Onde a configuracao ou listagens em contexto de evento exibem categoria e modo de fornecimento, apresentar labels, tooltips ou agrupamentos que deixem clara a diferenca para uso posterior em FEATURE-4 e FEATURE-5, utilizando sempre os valores canonicos devolvidos pela API (sem hardcode de strings divergentes do contrato).

## precondicoes

- T3 concluida: fluxo principal e RBAC/erros alinhados.
- T1: tipos ou constantes de modo canonico disponiveis a partir da resposta da API.

## orquestracao

- `depends_on`: ["T3"].
- `parallel_safe`: false.
- `write_scope`: mesma pagina ou componentes extraidos criados nas tasks anteriores; nao alterar backend nesta task.

## arquivos_a_ler_ou_tocar

- `frontend/src/pages/AtivosList.tsx`
- `frontend/src/services/ativos.ts` *(mapeamento de enums/valores canonicos para texto de UI)*

## passos_atomicos

1. Inventariar na UI implementada nas T2-T3 todos os pontos que mostram categoria, modo ou ambos (tabela, formulario de configuracao, detalhes).
2. Definir mapa de apresentacao (ex. funcao `formatModoFornecimento` ou objeto de labels) que traduz valores canonicos da API para texto legivel em portugues, mantendo correspondencia 1:1 com o contrato.
3. Aplicar labels distintas: "Categoria" vs "Modo de fornecimento" (ou terminologia alinhada ao PRD) e, se util, `title`/Tooltip do MUI para contexto operacional breve.
4. Revisar que nenhum valor interno canonico aparece cru ao utilizador sem legenda quando isso prejudicar compreensao.

## comandos_permitidos

- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`
- `cd frontend && npm run build`

## resultado_esperado

Operador distingue visualmente categoria e modo onde ambos forem exibidos, preparando leituras consistentes para fluxos futuros de conciliacao e emissao.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run build`
- Revisao manual dos tres fluxos de contexto de evento tocados pela US (configuracao e, se aplicavel, linhas da listagem que mostrem modo).

## stop_conditions

- Parar se a API ainda nao expuser modo nas leituras usadas pela tela — registrar limitacao e alinhar com US-3-02 antes de simular dados na UI.
