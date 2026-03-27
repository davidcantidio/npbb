---
doc_id: "TASK-1.md"
user_story_id: "US-3-03-UI-CONFIGURACAO-CATEGORIAS-POR-EVENTO"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on: []
parallel_safe: false
write_scope:
  - "frontend/src/services/ativos.ts"
tdd_aplicavel: false
---

# TASK-1 - Cliente HTTP e tipos para configuracao de categorias e modos canonicos

## objetivo

Expor em `frontend/src/services/ativos.ts` funcoes tipadas para ler e gravar o subset de categorias habilitadas por evento e para obter os modos canonicos de fornecimento, consumindo o contrato entregue pela [US-3-02](../../US-3-02-API-CONFIGURACAO-RBAC-E-CONTRATO-MODOS/README.md) (paths, verbos HTTP e payloads alinhados ao backend, ex. `backend/app/routers/ativos.py` ou documentacao OpenAPI gerada).

## precondicoes

- [US-3-02](../../US-3-02-API-CONFIGURACAO-RBAC-E-CONTRATO-MODOS/README.md) concluida (`done`) e contrato de API estavel (endpoints e schemas acordados).
- Leitura do contrato real (OpenAPI em `/docs` do backend ou artefatos da US-3-02) antes de fixar URLs e tipos.

## orquestracao

- `depends_on`: nenhuma task anterior nesta US.
- `parallel_safe`: false.
- `write_scope`: apenas o servico de ativos no frontend; nao introduzir duplicacao de `handleResponse` — reutilizar o padrao existente em `ativos.ts` (`fetch` + `Authorization: Bearer`).

## arquivos_a_ler_ou_tocar

- `frontend/src/services/ativos.ts`
- `frontend/src/services/http.ts` *(se necessario para `API_BASE_URL` ou helpers)*
- Contrato da API definido na US-3-02 / OpenAPI do backend

## passos_atomicos

1. Identificar no backend os endpoints de leitura/escrita de configuracao de categorias por evento e o endpoint ou enum que expoe os dois modos canonicos (**interno emitido com QR** e **externo recebido**).
2. Definir tipos TypeScript espelhando o JSON de request/response (catalogo inicial trio, subset habilitado, modo por linha ou estrutura acordada).
3. Implementar `async` functions que chamam esses endpoints com `token: string`, tratando erros via o mesmo mecanismo que `listAtivos` / `atribuirCota` (mensagens utilizaveis na UI).
4. Exportar as funcoes e tipos para uso em `AtivosList.tsx` (ou componentes filhos) nas tasks seguintes.

## comandos_permitidos

- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`

## resultado_esperado

Servico de ativos com funcoes claras para configuracao por evento e leitura de modos canonicos, sem acoplamento a componentes React.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run typecheck` sem erros novos atribuiveis a esta alteracao.
- Revisao manual: assinaturas alinhadas ao contrato documentado na US-3-02.

## stop_conditions

- Parar se os endpoints ou o schema JSON ainda nao existirem no backend (bloqueio ate US-3-02).
- Parar se o contrato divergir entre OpenAPI e implementacao backend — escalar alinhamento antes de fixar tipos.
