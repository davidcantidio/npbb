---
doc_id: "TASK-4.md"
user_story_id: "US-6-04-PROBLEMAS-OPERACIONAIS"
task_id: "T4"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T3"
parallel_safe: false
write_scope:
  - "frontend/src/services/ingressos_admin.ts"
  - "frontend/src/pages/AtivosList.tsx"
  - "frontend/src/app/AppRoutes.tsx"
tdd_aplicavel: false
---

# T4 - UI operacional: registrar e listar problemas por evento

## objetivo

Entregar superficie para o operador **registrar** uma ocorrencia (tipo, descricao, evento em contexto) e **listar** ocorrencias do evento selecionado, consumindo a API da T2/T3. UX e componentes alinhados ao padrao existente (Material UI / formularios ja usados em ativos e ingressos).

## precondicoes

- T3 `done`: contrato API validado por testes.
- URL base da API e autenticacao (token/cookies) iguais aos servicos existentes em `frontend/src/services/`.

## orquestracao

- `depends_on`: `T3` (backend estabilizado por testes).
- `parallel_safe`: false.

## arquivos_a_ler_ou_tocar

- `frontend/src/pages/AtivosList.tsx` *(contexto de evento e fluxo admin de ativos)*
- `frontend/src/pages/IngressosPortal.tsx` *(padrao de usuario portal — usar apenas se a US for atendida no portal; preferir superficie operacional admin se for o caso)*
- `frontend/src/services/ingressos_admin.ts` *(padrao fetch + auth)*
- `frontend/src/services/api.ts` ou equivalente de `API_BASE_URL`
- `frontend/src/app/AppRoutes.tsx` *(nova rota ou secao apenas se necessario)*

## passos_atomicos

1. Mapear onde o operador ja escolhe `evento_id` no fluxo de ativos; embutir formulario de criacao (campos minimos da US) e tabela/lista de ocorrencias abaixo ou em dialogo.
2. Implementar funcoes de servico TypeScript: POST criar, GET listar com query de paginacao alinhada ao backend.
3. Tratar estados de carregamento, erro e lista vazia com mensagens em portugues consistentes com o restante do app.
4. Garantir que a listagem dispara sempre com filtro do evento atual (nunca lista global sem filtro, salvo se produto exigir — fora do escopo US).
5. Acessibilidade basica: labels em inputs, feedback de erro de API.

## comandos_permitidos

- `cd frontend && npm run build`
- `cd frontend && npm run lint` *(se configurado no projeto)*

## resultado_esperado

Operador consegue fluxo completo criar + ver lista por evento na UI, sem planilhas paralelas.

## testes_ou_validacoes_obrigatorias

- `npm run build` sem erro.
- Teste manual documentado: criar ocorrencia, recarregar lista, trocar evento e confirmar isolamento visual.

## stop_conditions

- Parar se a API ainda nao expuser CORS ou auth no ambiente local — resolver com T2 antes de UI.
- Parar se o produto exigir rota nova sem decisao de navegacao — escalar PM.
