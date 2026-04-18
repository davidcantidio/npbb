# Task 1 — Validador: aceitar email válido OU CPF válido

**Prioridade:** P0

## Problema

A documentação (`docs/leads_importacao.md`) e a regra de mapeamento descrevem o requisito essencial como **email ou CPF**. Em `validate_normalized_lead_payload`, o código trata CPF ausente ou vazio como inválido e acumula erro de CPF, o que **rejeita leads só com email válido**. Isso contradiz a regra de negócio e provoca perda silenciosa de dados em preview ETL e em `persist_lead_batch()`.

## Escopo

- `backend/app/modules/leads_publicidade/application/etl_import/validators.py` — função `validate_normalized_lead_payload`
- `docs/leads_importacao.md` — alinhar texto se necessário após mudança de comportamento
- Fluxos que chamam esta validação: preview ETL, persistência em `backend/app/modules/leads_publicidade/application/etl_import/persistence.py`

## Critérios de aceite

1. Payload com **email válido** e CPF ausente, vazio ou inválido **não** gera erro de identificação (lista de erros vazia ou sem bloqueio equivalente ao atual).
2. Payload **sem** email válido **e** sem CPF válido continua rejeitado de forma clara.
3. CPF válido continua aceito com ou sem email.
4. Testes automatizados cobrem o caso `{"email": "ok@example.com", "cpf": None}` (e variantes de string vazia).

## Plano de verificação

- Teste unitário em `validate_normalized_lead_payload` com email-only (esperado: sem erro de “CPF inválido” por ausência de CPF).
- Teste de integração ou de serviço ETL: planilha de uma linha só com email válido deve aparecer em **linhas aprovadas** (não em `rejected_rows` por validação de identificador).
- Repro manual: `POST /leads/import/etl/preview` com CSV mínimo uma linha, coluna email preenchida, CPF vazio.

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

Relatório completo: [auditoria/deep-research-report.md](deep-research-report.md) — secção **Achados detalhados** → **Validador rejeita email-only, embora a regra documentada diga email ou CPF**.
