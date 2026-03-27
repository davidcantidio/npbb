---
doc_id: "TASK-4.md"
user_story_id: "US-7-02-AUTENTICACAO-INTEGRADOR"
task_id: "T4"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T3"
parallel_safe: false
write_scope:
  - "backend/tests/test_integrador_auth.py"
  - "backend/tests/conftest.py"
tdd_aplicavel: true
---

# TASK-4 - Testes automatizados, rota de verificacao e documentacao operacional minima

## objetivo

Garantir **testes automatizados** que cubram **pelo menos um caminho positivo e um negativo** de autenticacao do integrador (criterio Given/When/Then da US), usando `TestClient` ou chamada directa a dependencias com `Request` fake, **sem** depender das rotas finais de ingestao da US-7-03. Documentar no `DECISAO-AUTH-INTEGRADOR.md` ou subsecao anexa as variaveis de ambiente, rotacao de segredos e o comando de teste de evidencia.

## precondicoes

- TASK-3 concluida (`done`): validacao de segredos e contexto de integrador funcionais.
- `DECISAO-AUTH-INTEGRADOR.md` atualizavel para notas operacionais.

## orquestracao

- `depends_on`: `T3`.
- `parallel_safe`: `false`.
- `write_scope`: conforme frontmatter.

## arquivos_a_ler_ou_tocar

- `backend/app/core/integrador_auth.py`
- `backend/tests/test_auth_dependency.py` *(padrao de testes de auth existente)*
- `backend/tests/conftest.py` *(fixture compartilhada se necessario)*
- `backend/tests/test_integrador_auth.py` *(criar ou estender)*
- `DECISAO-AUTH-INTEGRADOR.md`
- `backend/app/main.py` *(apenas se testes de integracao exigirem app com router montado)*

## testes_red

- testes_a_escrever_primeiro:
  - `test_integrador_sem_credencial_recebe_401_ou_403`: chamar endpoint ou dependencia sem header — esperar status 401 ou 403.
  - `test_integrador_com_credencial_valida_propaga_contexto`: com env/fixture de segredo valido — esperar 200 ou sucesso na dependencia com `integrador_id` definido.
- comando_para_rodar:
  - `cd backend && PYTHONPATH=<raiz>:<raiz>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_integrador_auth.py -q`
- criterio_red:
  - Antes da implementacao completa da stack T2-T3, os testes podem falhar; apos T3, a suite deve passar. Se passarem antes da implementacao, revisar se os testes estao a validar o comportamento real.

## passos_atomicos

1. Escrever os testes listados em `testes_red` (e ajustar nomes conforme convencao do projeto).
2. Montar aplicacao minima de teste: `FastAPI()` com rota GET protegida pelo `Depends` de integrador **ou** testes unitarios que invoquem a dependencia com `Request`/`Headers` construidos.
3. Usar `monkeypatch.setenv` para segredos de teste (nunca valores reais).
4. Confirmar que nenhum teste persiste dados de recebimento ou chama use cases de FEATURE-4.
5. Atualizar `DECISAO-AUTH-INTEGRADOR.md` com secao **Operacao**: variaveis de ambiente, rotacao, e comando `pytest` de evidencia para revisao da US.

## comandos_permitidos

- `cd backend && PYTHONPATH=<raiz>:<raiz>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_integrador_auth.py -q`
- `cd backend && ruff check tests/test_integrador_auth.py`

## resultado_esperado

- Suite `tests/test_integrador_auth.py` verde em CI local com `TESTING=true`.
- Documentacao operacional minima no ficheiro de decisao, rastreavel para operadores.
- Criterio da US sobre testes positivo/negativo satisfeito.

## testes_ou_validacoes_obrigatorias

- Pelo menos dois testes automatizados: um negativo (401/403), um positivo (contexto ou 200).
- Nenhum segredo ou token completo impresso em falhas de assert.

## stop_conditions

- Parar se for impossivel testar sem routers de ingestao **e** sem conseguir instanciar dependencia isoladamente — nesse caso documentar lacuna e pedir ajuste de escopo na US.
