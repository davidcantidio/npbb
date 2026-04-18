# Task 11 — Segurança e compliance: RBAC nos use cases e retenção de dados sensíveis

**Prioridade:** P2

## Problema

O relatório indica que os endpoints exigem autenticação nos testes, mas **autorização por papel** não está claramente aplicada dentro dos use cases, que em muitos sítios **ignoram `current_user`**. Paralelamente, `arquivo_bronze` em `lead_batches` e snapshots ETL (`lead_import_etl_preview_session`) retêm dados potencialmente **sensíveis** sem política explícita de **retenção ou expurgo**.

## Escopo

- Routers e dependências de auth em `backend/app/routers/leads.py` e relacionados
- Use cases em `leads_import_usecases.py`, serviços ETL, pipeline — verificação de permissão por recurso (evento, agência, etc., conforme modelo do produto)
- Política de retenção: job de limpeza, TTL configurável, anonimização ou apagamento de previews e blobs Bronze após N dias / após commit

## Critérios de aceite

1. Matriz de permissões documentada: quem pode preview, commit, pipeline, ver lote de terceiros.
2. Enforce no backend (não só na UI) para operações sensíveis identificadas.
3. Política de retenção **configurável** e mecanismo (cron/worker) documentado; valores por defeito seguros para ambientes não-prod.
4. Evidência de teste (403 para papel inadequado) nos endpoints críticos.

## Plano de verificação

- Testes de API com dois perfis de utilizador (autorizado / não autorizado).
- Verificar após job de expurgo que registos antigos são removidos ou anonimizados conforme política.

## Skills recomendadas (acionar na execução)

Antes de implementar, **ler** cada skill indicada (`SKILL.md` na pasta listada) e seguir as práticas descritas.

- [.claude/skills/secure-code-guardian/SKILL.md](.claude/skills/secure-code-guardian/SKILL.md) — autorização em profundidade, validação de input e sessão.
- [.claude/skills/security-reviewer/SKILL.md](.claude/skills/security-reviewer/SKILL.md) — revisão de superfície RBAC e dados sensíveis em repouso.
- [.claude/skills/fastapi-expert/SKILL.md](.claude/skills/fastapi-expert/SKILL.md) — dependências de utilizador, scopes e routers.
- [.claude/skills/fullstack-guardian/SKILL.md](.claude/skills/fullstack-guardian/SKILL.md) — alinhar enforcement backend com expectativas da UI.
- [.claude/skills/test-master/SKILL.md](.claude/skills/test-master/SKILL.md) — testes 403/200 por papel e testes de job de expurgo (se aplicável).

## Subtarefa obrigatória: handoff ao concluir

Ao **terminar** esta tarefa (código, testes e revisão), criar o ficheiro **`auditoria/handoff-task11.md`** com:

1. **Resumo** da matriz RBAC, política de retenção (TTL, job) e excepções legais/operacionais.
2. **Lista de ficheiros** tocados (routers, use cases, workers, migrações, config).
3. **Diffs / revisão**: `git diff` por área sensível; checklist de deploy (cron, secrets); impacto em dados já armazenados.

O handoff deve permitir continuidade sem reler toda a conversa.

## Referência

Relatório completo: [auditoria/deep-research-report.md](deep-research-report.md) — secção **Segurança e compliance** no **Checklist técnico percorrido**.
