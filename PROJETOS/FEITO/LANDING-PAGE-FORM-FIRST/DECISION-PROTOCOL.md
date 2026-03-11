---
doc_id: "DECISION-PROTOCOL.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-08"
---

# DECISION-PROTOCOL - LANDING-PAGE-FORM-FIRST

## Objetivo

Registrar decisoes do projeto Landing Page Form-Only quando houver alteracao de escopo, convencao visual, estrutura de componentes ou qualquer outro ajuste que contradiga o framework comum ou o PRD vigente.

## Status Atual

## Decisoes Registradas

### 2026-03-08 - Remocao definitiva do modelo legado da landing

- decisao: a landing publica e o modo preview passam a compartilhar o mesmo layout form-only
- implicacao_visual: header, hero, hero image, about, brand summary, checklist e chips operacionais deixam de existir no produto
- implicacao_tecnica: `hero_image_url` sai do formulario de backoffice, dos payloads publicos, dos schemas de evento, da validacao de escrita e da persistencia em banco
- implicacao_de_preview: o preview permanece somente com um badge discreto de `Preview` e interacoes desabilitadas
- impacto_documental: issues que assumiam preservacao temporaria de blocos legados ficam reescritas ou canceladas conforme o novo escopo canonico

## Regras Locais

- usar `PROJETOS/COMUM/GOV-DECISOES.md` como taxonomia base
- registrar neste arquivo apenas decisoes especificas do projeto
- qualquer mudanca estrutural deve referenciar o documento comum correspondente
- decisoes sobre paleta de cores ou tokens visuais devem referenciar o Manual BB
