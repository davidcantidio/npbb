# Task 2 — Commit ETL: não selar `committed` com falha parcial

**Prioridade:** P0

## Problema

`commit_preview_session` pode montar `EtlCommitResult(status="committed")` mesmo quando `persist_lead_batch()` reporta `skipped > 0` e `has_errors=True`. Depois `mark_committed()` grava o resultado e `get_commit_result()` devolve cache para o mesmo `session_token`, **impedindo replay** das linhas que falharam. O operador vê commit concluído, mas o estado persistido pode ser parcial e irreversível via API.

## Escopo

- `backend/app/modules/leads_publicidade/application/etl_import/commit_service.py` — `commit_preview_session`
- Repositório de sessão de preview ETL — `preview_session_repository.py` (`mark_committed`, `get_commit_result`, estados possíveis)
- Esquema/contrato de `EtlCommitResult` / `status` da sessão (ex.: `partial_failure`, `failed` vs `committed`)
- Endpoints `/leads/import/etl/commit` e documentação de erro para o cliente

## Critérios de aceite

1. Se a persistência tiver erros ou linhas skipped conforme regra acordada, a sessão **não** é marcada como `committed` com semântica de “tudo concluído com sucesso”.
2. Estado persistido reflete **falha parcial** (ou equivalente) com motivos utilizáveis para o operador.
3. Chamadas subsequentes com o mesmo `session_token` **podem** retentar linhas falhadas (estratégia explícita: `retry_failed_rows`, replay seguro, ou documentar fluxo manual mínimo).
4. Teste de integração cobre o caminho: simular falha em uma linha durante commit, verificar que o status não congela sucesso falso e que o comportamento de retry é o definido.

## Plano de verificação

- Monkeypatch ou falha controlada em `_ensure_canonical_event_link`, `db.commit()` ou persistência de uma linha; executar commit ETL; assert sobre `status` e sobre possibilidade de reprocessamento.
- Reutilizar cenário mental do relatório: 9.999 linhas OK, linha 10.000 falha — sessão não deve ser tratada como commit bem-sucedido fechado sem opção de correção.

## Skills recomendadas (acionar na execução)

Antes de implementar, **ler** cada skill indicada (`SKILL.md` na pasta listada) e seguir as práticas descritas.

- [.claude/skills/fastapi-expert/SKILL.md](.claude/skills/fastapi-expert/SKILL.md) — fluxos de commit, estados de sessão e respostas HTTP consistentes.
- [.claude/skills/python-pro/SKILL.md](.claude/skills/python-pro/SKILL.md) — transações, repositórios e modelagem de resultados parciais.
- [.claude/skills/test-master/SKILL.md](.claude/skills/test-master/SKILL.md) — testes de integração com falha injectada e asserts de idempotência/retry.
- [.claude/skills/debugging-wizard/SKILL.md](.claude/skills/debugging-wizard/SKILL.md) — isolar estados inconsistentes de sessão e reproduzir cenários parciais.

## Subtarefa obrigatória: handoff ao concluir

Ao **terminar** esta tarefa (código, testes e revisão), criar o ficheiro **`auditoria/handoff-task2.md`** com:

1. **Resumo** do que foi implementado e decisões tomadas (incluindo semântica de `status` da sessão).
2. **Lista de ficheiros** tocados (criados, alterados ou removidos), com caminhos relativos à raiz do repositório.
3. **Diffs / revisão**: quando pertinente, indicar comandos úteis (ex.: `git diff main...HEAD -- backend/app/modules/leads_publicidade/`), intervalo de commits, ou alterações de schema/migração.

O handoff deve permitir continuidade sem reler toda a conversa.

## Referência

Relatório completo: [auditoria/deep-research-report.md](deep-research-report.md) — secção **Achados detalhados** → **Commit ETL pode concluir com falha parcial e bloquear reprocessamento real**.
