---
doc_id: "TASK-5.md"
user_story_id: "US-6-02-REMANEJAMENTO-AUDITAVEL"
task_id: "T5"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T2"
  - "T3"
  - "T4"
parallel_safe: false
write_scope:
  - "backend/tests/test_ingressos_endpoints.py"
tdd_aplicavel: false
---

# T5 - Validacao integrada e checklist dos criterios Given/When/Then

## objetivo

Consolidar **cobertura de testes** e evidencias que fecham explicitamente os tres criterios Given/When/Then da US-6-02: (1) historico com origem, destino, quantidade, instante, ator e estado remanejado consultavel; (2) bloqueio sem motivo quando politica exige; (3) listagem de auditoria **sem misturar** com aumento/reducao de previsao. Preencher lacunas nos testes de integracao em `test_ingressos_endpoints.py` se T2/T3 deixaram cenarios apenas parciais; adicionar teste E2E leve no frontend **somente** se o repo ja tiver harness (Playwright/Vitest) — caso contrario, reforcar checklist manual documentado no handoff da US.

## precondicoes

- TASK-2, TASK-3 e TASK-4 `done`.
- Comandos de pytest e build do frontend validados localmente.

## orquestracao

- `depends_on`: `["T2", "T3", "T4"]`.
- `parallel_safe`: `false`.
- `write_scope`: `backend/tests/test_ingressos_endpoints.py`; ficheiros de teste frontend apenas se ja existir harness no repo (declarar caminho concreto no PR se criar novo ficheiro).

## arquivos_a_ler_ou_tocar

- `backend/tests/test_ingressos_endpoints.py`
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-6-DISTRIBUICAO-REMANEJAMENTO-AJUSTES-PROBLEMAS/user-stories/US-6-02-REMANEJAMENTO-AUDITAVEL/README.md` *(checklist DoD)*
- Configuracao de CI do repo *(Makefile / GitHub Actions)*

## passos_atomicos

1. Mapear cada Given/When/Then da US a um ou mais testes automatizados existentes; identificar lacunas.
2. Adicionar cenarios de integracao faltantes (fluxo completo POST + GET, politica de motivo, discriminacao de tipo na listagem).
3. Se existir suite E2E frontend, cobrir submit e visualizacao de historico; senao, produzir roteiro manual curto em comentario ou evidencia anexa conforme `GOV-SCRUM` do projeto.
4. Executar `pytest` alvo e `npm run build` do frontend; corrigir falhas ate green.
5. Registar no README da US (handoff) os comandos exatos usados como evidencia, quando o fluxo do projeto exigir.

## comandos_permitidos

- `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest tests/test_ingressos_endpoints.py -q`
- `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q` *(se a US exigir regressao mais larga — justificar no PR)*
- `cd frontend && npm run build`
- `cd frontend && npm test` *(apenas se configurado)*

## resultado_esperado

Suite relevante em green com rastreio claro dos criterios da US; nenhum criterio permanece apenas “testado manualmente” sem registo, salvo excecao documentada.

## testes_ou_validacoes_obrigatorias

- `pytest` nos testes tocados: 0 falhas.
- `npm run build` no frontend: sucesso.

## stop_conditions

- Parar se correcao exigir alteracao de escopo da US (novo tipo de remanejamento ou novo eixo de auditoria) — escalar a revisao de US antes de codificar.
- Parar se testes integrados exigirem Postgres e o ambiente CI so tiver SQLite — seguir convencao `TESTING=true` do AGENTS.md e ajustar fixtures, nao desativar asserts.
