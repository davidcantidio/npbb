---
doc_id: "TASK-4.md"
user_story_id: "US-7-04-OPENAPI-CONTRATO-E-QUALIDADE"
task_id: "T4"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T1"
  - "T2"
  - "T3"
parallel_safe: false
write_scope:
  - "backend/app/main.py"
  - "backend/app/routers/ativos_ingressos_externo.py"
  - "backend/app/schemas/ativos_ingressos_externo.py"
tdd_aplicavel: false
---

# TASK-4 - Revisao de seguranca do contrato OpenAPI exposto

## objetivo

Revisar o artefato OpenAPI publico e exemplos associados para garantir que nao expoem dados sensiveis (tokens, credenciais, PII real), que descricoes nao revelam detalhes internos desnecessarios (stack traces, nomes internos de filas) e que o superficie documentada esta alinhada ao que integradores devem ver.

## precondicoes

- T1, T2 e T3 concluidas (`done`).
- OpenAPI final acessivel como na T1.

## orquestracao

- `depends_on`: `["T1", "T2", "T3"]`.
- `parallel_safe`: `false`.
- `write_scope`: mesmos ficheiros de documentacao de API da T1; alteracoes apenas em descricoes, exemplos e metadados OpenAPI, sem mudar semantica de negocio salvo correcao de vazamento.

## arquivos_a_ler_ou_tocar

- Schema OpenAPI exportado ou fontes em router/schemas tocados na T1
- `backend/app/main.py` se `openapi_tags` ou metadata global precisar de ajuste de descricao
- Resultados da T2: garantir que exemplos usados nos testes nao foram copiados para documentacao publica com dados reais

## passos_atomicos

1. Percorrer todos os `example`/`examples` no OpenAPI e substituir por valores ficticios (emails `@example.com`, tokens `redacted`, IDs UUID fixos de exemplo).
2. Revisar descricoes de endpoints e erros: remover referencias a implementacao interna que nao sejam necessarias ao integrador.
3. Confirmar que rotas internas ou administrativas nao aparecem no mesmo documento publico destinado a ticketeiras, salvo decisao documentada.
4. Validar que cabecalhos de autenticacao estao descritos como esquema seguro (Bearer, etc.) sem exemplos de segredo valido.
5. Registrar no handoff da US qualquer limitacao conhecida (ex.: `/docs` desligado em producao) se for politica de deploy.

## comandos_permitidos

- Revisao manual de `/openapi.json` ou `/docs`
- `cd backend && PYTHONPATH=..:. SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ativos_ingressos_externo_contract.py` (regressao rapida apos apenas mudancas de metadata, se aplicavel)

## resultado_esperado

Contrato publico adequado para partilha com integradores externos, sem vazamento de segredos ou PII nos exemplos e com descricoes profissionais.

## testes_ou_validacoes_obrigatorias

- Checklist: nenhum exemplo contem JWT real, senha, ou email/telefone de producao.
- Opcional: script ou grep no repositorio nos ficheiros de schema por padroes proibidos (`sk-`, `Bearer eyJ`, etc.) — apenas se ja existir ferramenta; nao expandir escopo para novo pipeline de seguranca.

## stop_conditions

- Parar se for necessario desenhar autenticacao ou escopo novo nao coberto pela US-7-02/7-03.
- Parar se a revisao encontrar bug funcional grave: abrir tarefa corretiva na US ou predecessoras em vez de “parchar” apenas documentacao.
