# Task 9 — Política de merge: visibilidade e modos configuráveis

**Prioridade:** P2

## Problema

A política **não destrutiva** (`merge_lead_payload_fill_missing`) protege dados existentes, mas pode **ignorar dados novos** sem transparência: o operador vê sucesso parcial sem perceber que campos foram preservados por política, gerando divergência entre expectativa e base.

## Escopo

- [backend/app/modules/leads_publicidade/application/etl_import/persistence.py](backend/app/modules/leads_publicidade/application/etl_import/persistence.py) e rotinas partilhadas de merge
- Resposta de commit ETL / legado: estrutura “campos ignorados por política”, contagens e motivos
- UI: resumo pós-commit com ligação à documentação de modos (`fill_missing`, `prefer_import`, `prefer_existing`) com confirmação explícita quando o modo não for o default

## Critérios de aceite

1. O resultado de importação indica **quantos campos** foram preenchidos vs ignorados por política (mínimo viável acordado com produto).
2. Modos alternativos só disponíveis em **fluxos controlados** (flag, role, ou ambiente) com confirmação e auditoria.
3. Testes cobrindo pelo menos o modo default e um modo alternativo mockado.

## Plano de verificação

- Testes de integração no commit ETL com payload que colide com lead existente.
- Revisão de copy com produto.

## Skills recomendadas (acionar na execução)

- [.claude/skills/python-pro/SKILL.md](.claude/skills/python-pro/SKILL.md)
- [.claude/skills/fastapi-expert/SKILL.md](.claude/skills/fastapi-expert/SKILL.md)
- [.claude/skills/react-expert/SKILL.md](.claude/skills/react-expert/SKILL.md)
- [.claude/skills/feature-forge/SKILL.md](.claude/skills/feature-forge/SKILL.md)
- [.claude/skills/test-master/SKILL.md](.claude/skills/test-master/SKILL.md)

## Subtarefa obrigatória: handoff ao concluir

Ao **terminar** esta tarefa, criar **`auditoria/handoff-task9.md`**.

## Referência

Relatório completo: [auditoria/deep-research-report.md](deep-research-report.md) — **Principais problemas encontrados** → **Política de dedupe e merge é segura para preservação, mas arriscada para atualização**; **Priorização final** (item 9).
