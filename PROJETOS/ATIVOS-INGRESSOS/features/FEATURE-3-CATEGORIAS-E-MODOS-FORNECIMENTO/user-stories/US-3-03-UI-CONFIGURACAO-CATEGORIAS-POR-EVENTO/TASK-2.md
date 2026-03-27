---
doc_id: "TASK-2.md"
user_story_id: "US-3-03-UI-CONFIGURACAO-CATEGORIAS-POR-EVENTO"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "frontend/src/pages/AtivosList.tsx"
tdd_aplicavel: false
---

# TASK-2 - Fluxo UI para subset de categorias por evento (persistencia e refresco)

## objetivo

Na superficie de ativos (`AtivosList.tsx` ou componente extraido na mesma pasta de paginas se reduzir complexidade), permitir que o operador selecione um evento, ajuste quais categorias do catalogo inicial aplicam-se a esse evento e persista via API; apos gravacao, a UI deve refletir o estado atual (refetch ou invalidacao), cumprindo o primeiro criterio Given/When/Then da US.

## precondicoes

- T1 concluida: funcoes em `ativos.ts` disponiveis e tipadas.
- Padrao visual MUI e filtros existentes em `AtivosList.tsx` (Autocomplete evento/diretoria) como referencia de UX.

## orquestracao

- `depends_on`: ["T1"].
- `parallel_safe`: false.
- `write_scope`: pagina principal; se criar `frontend/src/pages/*ConfigCategorias*.tsx` ou subpasta de componentes, incluir esses caminhos no commit e na evidencia de revisao.

## arquivos_a_ler_ou_tocar

- `frontend/src/pages/AtivosList.tsx`
- `frontend/src/services/ativos.ts` *(consumo apenas; alteracoes minimas se faltar helper)*
- `frontend/src/services/eventos.ts` *(lista de eventos ja usada nos filtros)*

## passos_atomicos

1. Acoplar o fluxo de configuracao ao `evento_id` selecionado (reutilizar estado de filtros ou estado local dedicado, de forma explicita na UI).
2. Carregar da API o estado atual do subset para o evento (via funcoes da T1) ao abrir o fluxo ou ao mudar de evento.
3. Renderizar controles para habilitar/desabilitar cada categoria do trio inicial conforme contrato (checkboxes, switches ou equivalente alinhado ao MUI ja usado na pagina).
4. Implementar acao de gravar que chama a API de atualizacao; em sucesso, recarregar dados de configuracao ou atualizar estado local a partir da resposta para garantir consistencia pos-recarga da pagina.
5. Tratar estado de carregamento e erro basico (sem aprofundar RBAC — reservado para T3).

## comandos_permitidos

- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`
- `cd frontend && npm run build`

## resultado_esperado

Operador com token valido consegue ajustar e persistir o subset de categorias por evento e ver o resultado refletido na sessao atual apos gravacao.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run build` apos alteracoes.
- Verificacao manual: escolher evento, alterar subset, gravar, recarregar a pagina e confirmar que o subset persiste (criterio de aceite da US).

## stop_conditions

- Parar se a API da T1 nao estiver disponivel ou retornar erros de contrato nao documentados.
- Parar se for necessario alterar escopo de negocio (ex. mais de tres categorias) sem atualizacao de PRD/US.
