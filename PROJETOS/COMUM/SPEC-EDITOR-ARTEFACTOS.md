---
doc_id: "SPEC-EDITOR-ARTEFACTOS.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-30"
---

# SPEC — Edicao de artefatos Markdown em `PROJETOS/`

Objetivo: reduzir falhas de patch e reescritas destrutivas por agentes quando
ficheiros tem historico misto de encoding ou finais de linha.

## 1. Formato preferido

- **Encoding:** UTF-8 **sem** BOM.
- **Fins de linha:** LF (Unix), coerentes com o resto do repositorio Git.

## 2. Falhas de patch ou diff

Quando uma edicao incremental falhar repetidamente num ficheiro grande
(ex.: `AUDIT-LOG.md`):

- **nao** apague e recrie o ficheiro inteiro salvo risco documentado de perda de
  historico ou ordem de tabelas
- preferir: editar **blocos pequenos** (secao ou linhas concretas), reler o
  trecho exato do disco e reaplicar
- se o problema for encoding visivel (caracteres substituidos), normalizar o
  ficheiro para UTF-8 sem BOM num **commit dedicado** de higiene, antes de
  mudancas semanticas

## 3. Tabelas e logs normativos

- Em `AUDIT-LOG.md` e relatorios, acrescente **linhas novas** em vez de reordenar
  tabelas sem necessidade, para manter diffs revievable.

## 4. Segredos

- **Nunca** coloque URLs com password, tokens ou `host.env` pessoal em ficheiros
  versionados; ver `SPEC-RUNTIME-POSTGRES-MATRIX.md`.

## 5. Documentos relacionados

| Documento | Relacao |
|-----------|---------|
| `GOV-AUDITORIA.md` | Outputs incluem `AUDIT-LOG.md` e relatorios sob `auditorias/` |
| `SESSION-AUDITAR-FEATURE.md` | Grava `AUDIT-LOG.md` e relatorios; aplicar edicao incremental |
| `GOV-FRAMEWORK-MASTER.md` | Secao 3 indexa esta spec |
| `boot-prompt.md` | Nivel 2 inclui esta spec |
| `TEMPLATE-AUDITORIA-FEATURE.md` | Estrutura dos relatorios em Markdown |
