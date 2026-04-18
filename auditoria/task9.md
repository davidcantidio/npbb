# Task 9 — Validação de upload: além da extensão e do tamanho

**Prioridade:** P3

## Problema

A validação em `file_reader.py` e leitura em `extract.py` baseia-se sobretudo na **extensão** do nome e no **tamanho** do stream. Ficheiros com extensão forjada (ex.: `.xlsx` com conteúdo inválido) avançam no fluxo até falharem no parser, com custo de recursos e UX pior. Não há verificação leve de **assinatura mágica** ou coerência MIME/conteúdo.

## Escopo

- `backend/app/services/imports/file_reader.py` — `_validate_extension`, `inspect_upload`
- `backend/app/modules/leads_publicidade/application/etl_import/extract.py` — `read_upload_bytes` se aplicável
- Respostas HTTP consistentes para “tipo inválido” **antes** de processamento pesado

## Critérios de aceite

1. Combinação de extensão com verificação mínima de conteúdo (magic bytes para ZIP/XLSX, sniff CSV seguro) que **rejeita cedo** conteúdo incoerente.
2. Erro claro para o cliente (sem stack trace em produção).
3. Teste automatizado: ficheiro renomeado com extensão aceite e bytes incorrectos → rejeição imediata na validação.

## Plano de verificação

- Teste unitário com payload mínimo errado por tipo.
- Teste manual documentado no PR opcional.

## Skills recomendadas (acionar na execução)

Antes de implementar, **ler** cada skill indicada (`SKILL.md` na pasta listada) e seguir as práticas descritas.

- [.claude/skills/secure-code-guardian/SKILL.md](.claude/skills/secure-code-guardian/SKILL.md) — validação de uploads, limites de tamanho e mensagens de erro seguras.
- [.claude/skills/python-pro/SKILL.md](.claude/skills/python-pro/SKILL.md) — `file_reader.py`, `extract.py` e leitura incremental de bytes.
- [.claude/skills/fastapi-expert/SKILL.md](.claude/skills/fastapi-expert/SKILL.md) — respostas HTTP consistentes para rejeição antecipada.
- [.claude/skills/test-master/SKILL.md](.claude/skills/test-master/SKILL.md) — testes com ficheiros de extensão forjada e conteúdo inválido.

## Subtarefa obrigatória: handoff ao concluir

Ao **terminar** esta tarefa (código, testes e revisão), criar o ficheiro **`auditoria/handoff-task9.md`** com:

1. **Resumo** das regras de validação (magic bytes, MIME) e limites mantidos.
2. **Lista de ficheiros** tocados no backend e testes associados.
3. **Diffs / revisão**: `git diff` nos módulos de upload; notas sobre compatibilidade com clientes que já enviam ficheiros limítrofes.

O handoff deve permitir continuidade sem reler toda a conversa.

## Referência

Relatório completo: [auditoria/deep-research-report.md](deep-research-report.md) — secção **Achados detalhados** → **A superfície de upload continua validando basicamente extensão e tamanho**; **Segurança e compliance** no checklist.
