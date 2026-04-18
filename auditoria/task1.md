# Task 1 — Validador: exigir CPF válido como requisito obrigatório

**Prioridade:** P0

## Problema

A regra vigente de produto é que **CPF é o único identificador obrigatório** para leads importáveis. Versões anteriores desta auditoria ficaram desalinhadas com essa decisão. Esta tarefa deve garantir que validação, mapeamento e documentação tratem **CPF válido como requisito obrigatório**, com email apenas como dado complementar.

## Escopo

- `backend/app/modules/leads_publicidade/application/etl_import/validators.py` — função `validate_normalized_lead_payload`
- `backend/app/routers/leads.py` e validação de mapeamento legado — exigir a coluna canónica `cpf`
- `docs/leads_importacao.md` e documentação correlata — alinhar texto à regra de CPF obrigatório
- Fluxos que chamam esta validação: preview ETL, persistência em `backend/app/modules/leads_publicidade/application/etl_import/persistence.py`

## Critérios de aceite

1. Payload com CPF ausente ou vazio gera erro claro de obrigatoriedade (`CPF ausente` ou equivalente definido).
2. Payload com CPF presente mas inválido continua rejeitado de forma clara.
3. Payload com CPF válido continua aceito, com email opcional.
4. A validação de mapeamento rejeita importações que não mapeiem a coluna canónica `cpf`.
5. Testes automatizados cobrem ausência vs. invalidez de CPF e a rejeição de mapeamento sem `cpf`.

## Plano de verificação

- Teste unitário em `validate_normalized_lead_payload` com `{"email": "ok@example.com", "cpf": None}` (esperado: erro explícito de CPF ausente).
- Teste de integração ou de serviço ETL: planilha de uma linha com email válido e CPF vazio deve aparecer em `rejected_rows`.
- Repro manual: `POST /leads/import/validate` sem mapear `cpf` deve falhar; `POST /leads/import/etl/preview` com CSV mínimo e CPF vazio deve rejeitar a linha.

## Skills recomendadas (acionar na execução)

Antes de implementar, **ler** cada skill indicada (`SKILL.md` na pasta listada) e seguir as práticas descritas.

- [.claude/skills/fastapi-expert/SKILL.md](.claude/skills/fastapi-expert/SKILL.md) — validação Pydantic, contratos de API e camadas de serviço FastAPI.
- [.claude/skills/python-pro/SKILL.md](.claude/skills/python-pro/SKILL.md) — Python 3.11+, tipagem, estilo e testes com pytest.
- [.claude/skills/test-master/SKILL.md](.claude/skills/test-master/SKILL.md) — casos de teste unitário e de integração, mocks e fixtures.
- [.claude/skills/code-documenter/SKILL.md](.claude/skills/code-documenter/SKILL.md) — alinhar `docs/leads_importacao.md` ao comportamento final, se necessário.

## Subtarefa obrigatória: handoff ao concluir

Ao **terminar** esta tarefa (código, testes e revisão), criar o ficheiro **`auditoria/handoff-task1.md`** com:

1. **Resumo** do que foi implementado e decisões tomadas.
2. **Lista de ficheiros** tocados (criados, alterados ou removidos), com caminhos relativos à raiz do repositório.
3. **Diffs / revisão**: quando pertinente, indicar comandos úteis (ex.: `git diff main...HEAD -- backend/`), intervalo de commits, ou destaque a migrações/contratos de API alterados.

O handoff deve permitir continuidade sem reler toda a conversa.

## Referência

Decisão vigente e continuidade: [auditoria/handoff-task1.md](handoff-task1.md). O relatório em [auditoria/deep-research-report.md](deep-research-report.md) foi reconciliado para refletir a mesma decisão consolidada de produto.
