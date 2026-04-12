# Auditoria do módulo Patrocinados vs canônico de Sponsorship

Reexecutei as validações informadas no worktree atual com os comandos corretos de ambiente:

- backend: `PYTHONPATH=c:/Users/NPBB/npbb;c:/Users/NPBB/npbb/backend SECRET_KEY=ci-secret-key TESTING=true backend/.venv/Scripts/python.exe -m pytest -q backend/tests/test_sponsorship_endpoints.py`
- frontend: `cd frontend && npm run test -- src/pages/__tests__/PatrocinadosPages.smoke.test.tsx`

No estado atual, `backend/tests/test_sponsorship_endpoints.py` cobre cenários negativos canônicos para `clause_id` de outro contrato e `status=rejected` sem `rejection_reason`, e o smoke `frontend/src/pages/__tests__/PatrocinadosPages.smoke.test.tsx` cobre tanto o redirect numérico quanto a falha explícita para IDs string/UUID do legado local.

O harness backend também habilita `PRAGMA foreign_keys=ON`, então o verde desse arquivo passa a provar ao menos uma constraint relacional real no SQLite de teste.

## 1) Classificação

### aderente

- A cadeia canônica principal está modelada no backend e migrada: contrato aponta para grupo, cláusula para contrato, contrapartida para contrato+cláusula, ocorrência para contrapartida, entrega para ocorrência e evidência para entrega em `backend/app/models/sponsorship_models.py:213`, `backend/app/models/sponsorship_models.py:254`, `backend/app/models/sponsorship_models.py:276`, `backend/app/models/sponsorship_models.py:313`, `backend/app/models/sponsorship_models.py:369`, `backend/app/models/sponsorship_models.py:385` e `backend/alembic/versions/2a9cfc2167a4_add_sponsorship_contract_module.py:93`, `backend/alembic/versions/2a9cfc2167a4_add_sponsorship_contract_module.py:112`, `backend/alembic/versions/2a9cfc2167a4_add_sponsorship_contract_module.py:125`, `backend/alembic/versions/2a9cfc2167a4_add_sponsorship_contract_module.py:145`, `backend/alembic/versions/2a9cfc2167a4_add_sponsorship_contract_module.py:172`, `backend/alembic/versions/2a9cfc2167a4_add_sponsorship_contract_module.py:185`.
- O módulo `/sponsorship` está efetivamente conectado na aplicação em `backend/app/main.py:197`.
- O frontend ativo é owner-first: as rotas públicas agora entram por pessoas, instituições e grupos em `frontend/src/app/AppRoutes.tsx:125` e a tela principal reforça isso em `frontend/src/features/patrocinados/PatrocinadosPage.tsx:100`.
- Contratos e contrapartidas continuam operando sob grupo na UX ativa: as telas de pessoa e instituição só abrem a operação via criação de grupo em `frontend/src/features/patrocinados/SponsoredPersonDetailPage.tsx:291` e `frontend/src/features/patrocinados/SponsoredInstitutionDetailPage.tsx:291`.
- O fallback local foi bloqueado na experiência principal quando `VITE_SPONSORSHIP_USE_API=false`, via `frontend/src/features/patrocinados/PatrocinadosPage.tsx:82` e `frontend/src/features/patrocinados/ApiRequiredPanel.tsx:16`.
- Os endpoints owner-first e contadores pedidos nesta seção existem de fato em `backend/app/routers/sponsorship.py:123`, `backend/app/routers/sponsorship.py:177`, `backend/app/routers/sponsorship.py:241`, `backend/app/routers/sponsorship.py:337`.

### parcialmente aderente

- O contrato já tem campos de arquivo original e metadados no modelo (`backend/app/models/sponsorship_models.py:218`), mas `SponsorshipContractCreate/Update` não expõem esses campos (`backend/app/schemas/sponsorship.py:189`) e a UI de contrato também não (`frontend/src/features/patrocinados/SponsorshipGroupPanels/GroupContractsPanel.tsx:44`).
- A ocorrência existe como unidade operacional central, mas o `responsibility_type` da ocorrência ficou escondido no contrato público: ele existe no modelo (`backend/app/models/sponsorship_models.py:317`), o router até tenta parsear no create (`backend/app/routers/sponsorship.py:847`), mas o schema de create/update/read não o expõe (`backend/app/schemas/sponsorship.py:328`, `backend/app/schemas/sponsorship.py:340`, `backend/app/schemas/sponsorship.py:348`) e o frontend também não (`frontend/src/types/sponsorship.ts:223`, `frontend/src/features/patrocinados/SponsorshipGroupPanels/GroupOccurrencesPanel.tsx:130`).
- Validação/rejeição/reversão estão só parcialmente cobertas: o modelo guarda `validated_by_user_id`, `validated_at`, `rejection_reason` e `internal_notes` (`backend/app/models/sponsorship_models.py:320`), mas a API usa patch genérico de ocorrência (`backend/app/routers/sponsorship.py:864`) e a UI ativa não oferece fluxo de validar/rejeitar/reverter, só criar/remover ocorrência e responsáveis (`frontend/src/features/patrocinados/SponsorshipGroupPanels/GroupOccurrencesPanel.tsx:130`, `frontend/src/features/patrocinados/SponsorshipGroupPanels/GroupOccurrencesPanel.tsx:149`, `frontend/src/features/patrocinados/SponsorshipGroupPanels/GroupOccurrencesPanel.tsx:159`).
- A semântica errada de “patrocinador” saiu da navegação ativa, mas ainda existe bastante código legado com essa modelagem no diretório `frontend/src/features/patrocinados/`.

### divergente

- A integridade canônica de responsáveis não é reforçada: `create_responsible` só persiste `member_id` sem verificar se o membro pertence ao grupo do contrato da ocorrência, nem aplica cardinalidade `individual=1` / `collective>=2` (`backend/app/routers/sponsorship.py:911`), contrariando `patrocinados-modelagem-canonica.md:491`.
- `rejection_reason` não é obrigatório quando a ocorrência vai para `rejected`: o patch aceita `status` e `rejection_reason` opcionais (`backend/app/schemas/sponsorship.py:340`, `backend/app/routers/sponsorship.py:870`), contrariando `patrocinados-modelagem-canonica.md:496`.
- A consistência “contrapartida aponta para cláusula do mesmo contrato” não é garantida no backend: o create de requirement sobrescreve só `contract_id` pelo path e aceita qualquer `clause_id` válido (`backend/app/routers/sponsorship.py:754`), contrariando `patrocinados-modelagem-canonica.md:493`.
- A rota legada `/patrocinados/:id` continua sendo compatibilidade parcial para o legado real: a navegação nova aceita só IDs numéricos de grupo e o smoke agora também cobre explicitamente a falha para IDs string/UUID do legado local (`frontend/src/features/patrocinados/LegacySponsorshipGroupRedirect.tsx:3`, `frontend/src/pages/__tests__/PatrocinadosPages.smoke.test.tsx:47` e `frontend/src/pages/__tests__/PatrocinadosPages.smoke.test.tsx:58`).

### ainda não implementado

- Upload/persistência pública do PDF original do contrato e seus metadados de storage.
- Fluxo público de `contract_extraction_draft` com revisão/aprovação humana.
- Fluxo ativo de frontend para validar, rejeitar e reverter ocorrência com registro de quem validou e quando.
- Cobertura adicional para regras canônicas ainda não implementadas no router, como mesmo grupo/cardinalidade de responsáveis.

## 2) Achados P0/P1/P2

- **P0** `backend/app/routers/sponsorship.py:911`: ocorrência pode receber responsável de grupo errado e sem cardinalidade canônica; isso permite gravar dado operacional incorreto contra `patrocinados-modelagem-canonica.md:492-498`.
- **P0** `backend/app/routers/sponsorship.py:864`: ocorrência pode ficar `rejected` sem `rejection_reason`; viola regra canônica e gera trilha de auditoria incompleta.
- **P0** `frontend/src/features/patrocinados/LegacySponsorshipGroupRedirect.tsx:3` + `frontend/src/services/patrocinados_local.ts:25`: a “compatibilidade” da rota antiga não cobre os IDs reais do legado local; isso é compatibilidade falsa.
- **P1** `backend/app/models/sponsorship_models.py:218` + `backend/app/schemas/sponsorship.py:189` + `frontend/src/features/patrocinados/SponsorshipGroupPanels/GroupContractsPanel.tsx:44`: o domínio pede arquivo original preservado, mas a API/UI pública não conseguem capturá-lo.
- **P1** `backend/app/models/sponsorship_models.py:317` + `backend/app/schemas/sponsorship.py:328` + `frontend/src/types/sponsorship.ts:223`: `responsibility_type` da ocorrência existe no modelo e some no contrato público; a variação por período do canônico não fica operável.
- **P1** `backend/app/routers/sponsorship.py:754`: o backend não valida se `clause_id` pertence ao `contract_id` do path; a UI ativa evita isso por seleção, mas a API não.
- **P1** `backend/app/models/sponsorship_models.py:131` + `backend/app/routers/sponsorship.py:394`: `social_profile` não tem FK polimórfica nem validação de owner existente; a API permite perfil social órfão.
- **P2** `frontend/src/features/patrocinados/Patrocinador*.tsx`, `frontend/src/features/patrocinados/PatrocinadosListPage.tsx`, `frontend/src/features/patrocinados/SponsorshipGroupDetailView.tsx`, `frontend/src/features/patrocinados/defaults.ts`, `frontend/src/features/patrocinados/PatrocinadorForm.tsx`, `frontend/src/services/patrocinados_local.ts`, `frontend/src/types/patrocinados.ts`: legado morto no app ativo, mas ainda grande o suficiente para confundir manutenção.
- **P2 resolvido** `backend/tests/test_sponsorship_endpoints.py` e `frontend/src/pages/__tests__/PatrocinadosPages.smoke.test.tsx`: a cobertura agora testa regra negativa canônica no backend (`clause_id` de contrato errado, `rejected` sem motivo e FK real em SQLite com `PRAGMA foreign_keys=ON`) e cobre no frontend a falha explícita para IDs string/UUID da rota legada.

## 3) Inconsistências objetivas entre canônico e comportamento real

- O canônico diz que a responsabilidade pode variar por ocorrência; o comportamento público atual só expõe `responsibility_type` na contrapartida, não na ocorrência.
- O canônico exige `rejection_reason` em rejeição; a API atual aceita `rejected` sem motivo.
- O canônico exige responsáveis do mesmo grupo do contrato; a API atual aceita qualquer `group_member`.
- O canônico exige preservar o PDF original e referência de storage; o modelo tem campos, mas a API/UI ativa não têm jornada para preenchê-los.
- O canônico elimina a entidade de patrocinador como centro do domínio; a UX ativa já seguiu isso, mas o repositório ainda contém um bloco legado relevante com `Patrocinador`, `patrocinados_local` e tipos próprios.
- A seção pediu `/patrocinados/:id` só como compatibilidade; no estado real ela só é compatível com IDs numéricos de grupo, não com o legado local que a própria base ainda mantém.

## 4) Código legado/stale

- `frontend/src/types/patrocinados.ts`: morto na app ativa; só alimenta o legado `Patrocinador*` e `patrocinados_local`.
- `frontend/src/services/patrocinados_local.ts`: morto na app ativa; mantém o domínio errado em `localStorage` e gera IDs incompatíveis com a “compatibilidade” nova.
- `frontend/src/features/patrocinados/PatrocinadorNewPage.tsx`: morto na navegação ativa; ainda contém bifurcação API/local.
- `frontend/src/features/patrocinados/PatrocinadorDetailPage.tsx`: morto na navegação ativa; em `apiMode` ainda desvia para `SponsorshipGroupDetailView`, criando uma UX paralela se alguém o reimportar.
- `frontend/src/features/patrocinados/PatrocinadosListPage.tsx`: morto na navegação ativa; ainda encapsula listagem errada por “patrocinador”.
- `frontend/src/features/patrocinados/SponsorshipGroupDetailView.tsx`: morto na navegação ativa; só fica parcialmente alcançável através do legado morto `PatrocinadorDetailPage`.
- `frontend/src/features/patrocinados/defaults.ts` e `frontend/src/features/patrocinados/PatrocinadorForm.tsx`: mortos; só sustentam páginas legadas.
- `frontend/src/features/patrocinados/index.ts:1`: isola bem o legado porque exporta só as páginas novas; isso favorece remoção ou isolamento explícito.

## 5) Menor plano corretivo possível

- Backend: endurecer `occurrence_responsible` e `occurrence` com validações de mesmo grupo, cardinalidade por `responsibility_type` e `rejection_reason` obrigatório; validar também `clause_id` contra `contract_id`.
- Contrato público: expor ao menos os campos de referência do arquivo original no schema/router e adicionar o menor input de UI para upload ou vínculo do arquivo.
- Ocorrência pública: incluir `responsibility_type` em create/read/update e registrar `validated_by_user_id` / `validated_at` quando status virar `validated`.
- Compatibilidade/limpeza: ou remover a alegação de compatibilidade de `/patrocinados/:id`, ou tratar explicitamente IDs legados string; em paralelo, remover/isolar `Patrocinador*`, `patrocinados_local` e tipos antigos.
- Testes: adicionar casos negativos para grupo errado, `rejected` sem motivo, cardinalidade `individual/collective`, `clause_id` de contrato errado, e rodar com FK real habilitada.
