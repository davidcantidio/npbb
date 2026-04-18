# Task 12 — Fluxo legado: relatório de linhas rejeitadas e motivos

**Prioridade:** P2 (quick win de paridade com ETL)

## Problema

No fluxo **ETL**, o preview devolve linhas rejeitadas com motivo por linha. No fluxo **legado** de preview/import, o retorno é sobretudo **resumo agregado**, sem granularidade por linha. Operadores perdem paridade de diagnóstico entre caminhos e confiam menos no legado para depuração.

## Escopo

- `backend/app/modules/leads_publicidade/application/leads_import_usecases.py` — `preview_import_sample_usecase`, `importar_leads_usecase` e resposta dos endpoints `POST /leads/import/preview` e import final
- Schemas Pydantic / DTOs expostos à API
- UI do fluxo legado, se ainda exposto ao utilizador (`frontend` — páginas de importação legada)

## Critérios de aceite

1. Resposta de preview legado inclui estrutura de **rejeições por linha** (índice ou chave estável + lista de motivos), dentro de limites razoáveis de tamanho (paginação ou cap documentado se necessário).
2. Resposta de import final inclui **agregado** por motivo e, quando possível, amostra ou totais por tipo de erro sem quebrar clientes existentes (versionamento ou campos opcionais).
3. Testes de contrato API atualizados; clientes antigos que ignoram campos novos continuam funcionais.

## Plano de verificação

- Teste de integração: CSV com linhas válidas e inválidas misturadas; assert na estrutura de rejeição por linha no preview.
- Comparar com formato ETL para alinhamento de nomenclatura de campos (quando fizer sentido).

## Skills recomendadas (acionar na execução)

Antes de implementar, **ler** cada skill indicada (`SKILL.md` na pasta listada) e seguir as práticas descritas.

- [.claude/skills/fastapi-expert/SKILL.md](.claude/skills/fastapi-expert/SKILL.md) — schemas Pydantic, versionamento de resposta e endpoints legados.
- [.claude/skills/api-designer/SKILL.md](.claude/skills/api-designer/SKILL.md) — paridade de contrato com o fluxo ETL sem quebrar clientes antigos.
- [.claude/skills/react-expert/SKILL.md](.claude/skills/react-expert/SKILL.md) — se a UI legada ainda for exposta ao utilizador.
- [.claude/skills/typescript-pro/SKILL.md](.claude/skills/typescript-pro/SKILL.md) — tipos do cliente alinhados aos novos campos opcionais.
- [.claude/skills/test-master/SKILL.md](.claude/skills/test-master/SKILL.md) — testes de contrato e regressão do preview legado.

## Subtarefa obrigatória: handoff ao concluir

Ao **terminar** esta tarefa (código, testes e revisão), criar o ficheiro **`auditoria/handoff-task12.md`** com:

1. **Resumo** do formato de rejeições por linha no legado e estratégia de compatibilidade (campos opcionais vs versão de API).
2. **Lista de ficheiros** tocados (use cases, routers, schemas, frontend, testes).
3. **Diffs / revisão**: exemplo de payload antes/depois; `git diff` nos DTOs; notas para equipas consumidoras da API.

O handoff deve permitir continuidade sem reler toda a conversa.

## Referência

Relatório completo: [auditoria/deep-research-report.md](deep-research-report.md) — **Checklist técnico** (legado sem granularidade por linha); **Próximos passos** → quick wins (“expor no legado pelo menos um relatório resumido de linhas rejeitadas e motivos”).
