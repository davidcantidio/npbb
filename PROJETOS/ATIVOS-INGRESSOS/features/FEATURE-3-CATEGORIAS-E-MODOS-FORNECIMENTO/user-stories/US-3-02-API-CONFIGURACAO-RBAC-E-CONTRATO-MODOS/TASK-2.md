---
doc_id: "TASK-2.md"
user_story_id: "US-3-02-API-CONFIGURACAO-RBAC-E-CONTRATO-MODOS"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "backend/app/routers/ativos.py"
  - "backend/app/schemas/ativos.py"
  - "backend/app/models/models.py"
tdd_aplicavel: false
---

# TASK-2 - Escrita da configuracao de categorias por evento com validacao do trio inicial

## objetivo

Permitir que um cliente autenticado **com permissao de configuracao** (detalhada na TASK-3 se necessario para ordem de implementacao; nesta task focar na regra de negocio e persistencia) altere o subconjunto de categorias habilitadas para um evento, aceitando apenas categorias do **trio inicial** (pista, pista premium, camarote) conforme FEATURE-3 e PRD, persistindo de forma coerente com o modelo da US-3-01.

## precondicoes

- TASK-1 concluida (`done`): contrato de leitura e exposicao dos modos canonicos estabilizado.
- Modelo e migracoes da US-3-01 aplicaveis no ambiente de desenvolvimento.

## orquestracao

- `depends_on`: `T1`.
- `parallel_safe`: `false`.

## arquivos_a_ler_ou_tocar

- `backend/app/routers/ativos.py`
- `backend/app/schemas/ativos.py`
- `backend/app/models/models.py` *(e tabelas de configuracao introduzidas na US-3-01)*
- `backend/app/db/database.py` / padrao de sessao existente
- [FEATURE-3.md](../../FEATURE-3.md) *(criterios de aceite de subset)*

## passos_atomicos

1. Definir schema Pydantic de entrada para o payload de atualizacao (lista ou conjunto de categorias habilitadas, limitado ao catalogo inicial).
2. Implementar camada de validacao: rejeitar com 4xx claro qualquer categoria fora do trio permitido ou duplicatas incoerentes; mensagens alinhadas a `app/utils/http_errors`.
3. Implementar endpoint (PATCH/PUT conforme convencao do projeto) que persista apenas o subset valido para o `evento_id` indicado, dentro da mesma visibilidade de agencia/dominio usada em GET.
4. Garantir transacao e consistencia (commit unico, rollback em erro).
5. **Auditoria operacional**: se a estrategia de logs/auditoria estiver centralizada na [US-3-04](../US-3-04-REGRESSAO-TESTES-E-OBSERVABILIDADE-CONFIG/README.md), registrar em comentario ou issue interna o hook necessario; implementar apenas logging estrutural minimo nesta task se o manifesto FEATURE-3 sec. 7 exigir registro na camada API sem esperar a US-3-04.

## comandos_permitidos

- `cd backend && PYTHONPATH=<raiz>:<raiz>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_ativos_endpoints.py -q`
- `cd backend && ruff check app/routers/ativos.py app/schemas/ativos.py`

## resultado_esperado

- Subset valido persiste e e refletido nas leituras subsequentes (GET da TASK-1).
- Subset invalido retorna 4xx sem alterar o estado persistido.

## testes_ou_validacoes_obrigatorias

- Teste ou validacao manual documentada: atualizacao valida + GET confirma valores.
- Payload com categoria nao permitida retorna 4xx com corpo de erro explicito.

## stop_conditions

- Parar se a definicao exata dos identificadores de categoria no banco (IDs vs slugs) nao estiver disponivel apos US-3-01.
- Parar se RBAC nao puder ser aplicado sem refatorar autenticacao; nesse caso concluir apenas validacao de negocio e coordenar com TASK-3 na mesma sessao de implementacao.
