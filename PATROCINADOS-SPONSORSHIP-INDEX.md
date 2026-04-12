# Patrocínio / Patrocinados — índice para revisão (sessão seguinte)

**Gerado para indexação:** use este arquivo como âncora; o patch completo está separado (evita inflar o contexto do MD com milhares de linhas de diff).

## Artefatos na raiz do repositório

| Arquivo | Conteúdo |
|---------|------------|
| [`PATROCINADOS-SPONSORSHIP.full.diff`](PATROCINADOS-SPONSORSHIP.full.diff) | Patch unificado (`git diff --cached` após stage seletivo): **~161 KB**, +2171 / −4 linhas no agregado do stat. |
| Este `PATROCINADOS-SPONSORSHIP-INDEX.md` | Resumo, lista de paths, como regenerar o diff, prompt curto para revisor. |

**Não incluídos** no diff (propositadamente): `cli/`, `patrocinados-modeling-done.md` e outros untracked não ligados a esta implementação.

## Escopo resumido

1. **Backend:** `main.py` (restaura `framework_router` + registra `sponsorship_router`); router [`backend/app/routers/sponsorship.py`](backend/app/routers/sponsorship.py) em `/sponsorship`, auth global `get_current_user`, enums, contagens, XOR membro; schemas [`backend/app/schemas/sponsorship.py`](backend/app/schemas/sponsorship.py); testes [`backend/tests/test_sponsorship_endpoints.py`](backend/tests/test_sponsorship_endpoints.py).
2. **Frontend:** flag `VITE_SPONSORSHIP_USE_API`; serviço [`frontend/src/services/sponsorship.ts`](frontend/src/services/sponsorship.ts); tipos [`frontend/src/types/sponsorship.ts`](frontend/src/types/sponsorship.ts); UI em `features/patrocinados/*` (lista, novo, detalhe API vs local).

## Paths tocados (lista para grep / IDE)

```
backend/app/main.py
backend/app/routers/sponsorship.py
backend/app/schemas/sponsorship.py
backend/tests/test_sponsorship_endpoints.py
frontend/src/features/patrocinados/PatrocinadosListPage.tsx
frontend/src/features/patrocinados/PatrocinadorNewPage.tsx
frontend/src/features/patrocinados/PatrocinadorDetailPage.tsx
frontend/src/features/patrocinados/SponsorshipGroupDetailView.tsx
frontend/src/features/patrocinados/sponsorshipMode.ts
frontend/src/services/sponsorship.ts
frontend/src/types/sponsorship.ts
frontend/src/vite-env.d.ts
```

## Regenerar o diff (se o working tree mudar)

PowerShell (apenas os mesmos paths; ajuste se novos arquivos entrarem no escopo):

```powershell
cd c:\Users\NPBB\npbb
git add backend/app/main.py backend/app/routers/sponsorship.py backend/app/schemas/sponsorship.py backend/tests/test_sponsorship_endpoints.py `
  frontend/src/features/patrocinados/PatrocinadorDetailPage.tsx frontend/src/features/patrocinados/PatrocinadorNewPage.tsx frontend/src/features/patrocinados/PatrocinadosListPage.tsx `
  frontend/src/features/patrocinados/SponsorshipGroupDetailView.tsx frontend/src/features/patrocinados/sponsorshipMode.ts `
  frontend/src/services/sponsorship.ts frontend/src/types/sponsorship.ts frontend/src/vite-env.d.ts
git diff --cached > PATROCINADOS-SPONSORSHIP.full.diff
git reset HEAD
```

## Prompt mínimo para revisor (colar + anexar o `.diff`)

```
Revise o patch em PATROCINADOS-SPONSORSHIP.full.diff no repositório NPBB (FastAPI + React/Vite).
Foque: prefixo /sponsorship vs proxy /api, auth Depends(get_current_user), enums/SQLModel,
_scalar_count, XOR group_member, respostas Read com contagens, testes test_sponsorship_endpoints.py,
e frontend VITE_SPONSORSHIP_USE_API + fetchWithAuth.
Entregue P0/P1/P2 com referências a arquivo e sugestão de patch.
```

## Checagens rápidas sugeridas

```bash
cd backend && PYTHONPATH=..:. SECRET_KEY=test TESTING=true python -m pytest tests/test_sponsorship_endpoints.py -q
cd frontend && npm run typecheck
```

---

**Por que dois arquivos:** o diff completo é pertinente para revisão mecânica e `git apply`/inspeção; o MD é pertinente para **indexação** na próxima sessão sem carregar ~2k linhas de patch no contexto do chat.
