# Task 8 — Política única de merge: Gold vs legado/ETL

**Prioridade:** P2

## Problema

No caminho Gold, `_merge_lead_payload_if_missing` só preenche campos quando o valor atual está **vazio**. No legado/ETL, `merge_lead` em `persistence.py` pode **atualizar** campos já preenchidos (com excepções específicas). O mesmo lead importado por fluxos diferentes fica com **semântica de “última importação vence”** inconsistente, difícil de explicar ao utilizador.

## Escopo

- `backend/app/services/lead_pipeline_service.py` — `_merge_lead_payload_if_missing` e inserção Gold
- `backend/app/modules/leads_publicidade/application/etl_import/persistence.py` — `merge_lead`
- Documentação de produto: política única (ex.: sempre não-destrutivo; sempre sobrescrever campos X; versão por campo; etc.)

## Critérios de aceite

1. Documento curto (ADR ou secção em doc existente) define a **política de merge** para os três fluxos.
2. Implementação alinhada: Gold, legado e ETL aplicam as **mesmas regras** para os campos no âmbito definido, ou divergências explícitas e justificadas com flags.
3. Testes que cobrem: dois lotes Gold sucessivos com campo já preenchido e valor diferente no segundo; cenário equivalente em ETL/legado — resultados coerentes com a política.

## Plano de verificação

- Tabela de casos (campo vazio / preenchido / nulo) × fluxo × resultado esperado.
- Testes automatizados para assimetria actual (deve passar com nova política explícita).

## Skills recomendadas (acionar na execução)

Antes de implementar, **ler** cada skill indicada (`SKILL.md` na pasta listada) e seguir as práticas descritas.

- [.claude/skills/python-pro/SKILL.md](.claude/skills/python-pro/SKILL.md) — funções de merge partilhadas e reutilização entre Gold e ETL.
- [.claude/skills/feature-forge/SKILL.md](.claude/skills/feature-forge/SKILL.md) — formalizar a política de merge com critérios de aceite e matriz de casos (se ainda não existir ADR).
- [.claude/skills/test-master/SKILL.md](.claude/skills/test-master/SKILL.md) — tabela de casos × fluxo e testes de não-regressão.
- [.claude/skills/architecture-designer/SKILL.md](.claude/skills/architecture-designer/SKILL.md) — opcional, para ADR curto sobre política única de dados.

## Subtarefa obrigatória: handoff ao concluir

Ao **terminar** esta tarefa (código, testes e revisão), criar o ficheiro **`auditoria/handoff-task8.md`** com:

1. **Resumo** da política de merge acordada e como cada fluxo a aplica.
2. **Lista de ficheiros** tocados (`lead_pipeline_service`, `persistence.py`, testes, documentação).
3. **Diffs / revisão**: trechos críticos de merge (funções puras vs efeitos laterais); `git diff` focado nesses ficheiros.

O handoff deve permitir continuidade sem reler toda a conversa.

## Referência

Relatório completo: [auditoria/deep-research-report.md](deep-research-report.md) — secção **Achados detalhados** → **O Gold reimporta sem atualizar dados já preenchidos**; **Checklist técnico** → qualidade e consistência.
