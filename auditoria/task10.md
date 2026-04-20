# Task 10 — Upload: defesa em profundidade (OWASP / contenção)

**Prioridade:** P3

## Problema

O repositório já valida extensão e conteúdo em vários casos (testes para `.txt`, XLSX inválido, ZIP disfarçado). Falta, contudo, uma estratégia explícita de **defesa em profundidade**: storage isolado, quarentena, observabilidade de rejeições e eventual varredura antimalware, alinhada a boas práticas OWASP para upload seguro.

## Escopo

- [backend/app/services/imports/file_reader.py](backend/app/services/imports/file_reader.py) e caminhos ETL de leitura de bytes
- Storage de uploads (alinhar com task 6 se object storage já estiver em curso)
- Logging/métricas por motivo de rejeição; pipeline de quarentena (bucket/prefix separado)
- Documentação de ameaça e mitigação (não precisa de código antivírus se o risco for aceite formalmente)

## Critérios de aceite

1. Documento curto (ADR ou secção em doc interna) com modelo de ameaça para uploads e mitigações implementadas ou explicitamente fora de escopo.
2. Rejeições de tipo/conteúdo produzem **métrica ou log estruturado** correlacionável (`request_id`, utilizador).
3. Qualquer nova dependência externa (scanner, etc.) fica atrás de feature flag.

## Plano de verificação

- Testes existentes de rejeição mantidos; novos casos se novas verificações forem adicionadas.
- Checklist de revisão de segurança no handoff.

## Skills recomendadas (acionar na execução)

- [.claude/skills/secure-code-guardian/SKILL.md](.claude/skills/secure-code-guardian/SKILL.md)
- [.claude/skills/security-reviewer/SKILL.md](.claude/skills/security-reviewer/SKILL.md)
- [.claude/skills/python-pro/SKILL.md](.claude/skills/python-pro/SKILL.md)
- [.claude/skills/monitoring-expert/SKILL.md](.claude/skills/monitoring-expert/SKILL.md)

## Subtarefa obrigatória: handoff ao concluir

Ao **terminar** esta tarefa, criar **`auditoria/handoff-task10.md`**.

## Referência

Relatório completo: [auditoria/deep-research-report.md](deep-research-report.md) — **Principais problemas encontrados** → **Segurança de arquivo tem base razoável, mas ainda não está em defesa em profundidade**; **Priorização final** (item 10).
