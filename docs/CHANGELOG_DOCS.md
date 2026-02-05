# Changelog da Documentacao

## 2026-02-05
### Adicionado
- `docs/INDEX.md` (mapa do repo).
- `docs/SETUP.md` (setup completo backend/frontend).
- `docs/WORKFLOWS.md` (importacao, dashboards, relatorio TMJ).
- `docs/TROUBLESHOOTING.md` (problemas comuns).
- `docs/ARCHITECTURE.md` (visao tecnica).

### Atualizado
- `README.MD`: resumo, comandos rapidos e links.
- `docs/auth.md`: alinhado ao comportamento atual de forgot-password (resposta generica).
- `docs/leads_importacao.md`: endpoints e regras revisadas, encoding corrigido.

### Arquivado/Removido
- `docs/_archive/template_eng_reversa.md` (template legacy movido para reduzir ruido).

### TODOs
- PRD/ADR oficial nao encontrado no repo.
- Verificacao local completa (uvicorn/pytest/vite) depende de `.env` valido e banco acessivel.
