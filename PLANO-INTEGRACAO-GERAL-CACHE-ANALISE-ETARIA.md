> Status em 2026-04-27: este arquivo passa a ser **artefato de origem**.
> A fonte canonica desta frente e:
> `PROJETOS/NPBB/INTAKE-INTEGRACAO-CACHE-ANALISE-ETARIA.md`,
> `PROJETOS/NPBB/PRD-INTEGRACAO-CACHE-ANALISE-ETARIA.md` e
> `PROJETOS/NPBB/features/FEATURE-10-INTEGRACAO-CACHE-ANALISE-ETARIA/`.
> Evidencias novas desta rodada devem ser consolidadas em
> `artifacts/phase-f4/evidence/`.

# Plano de integração geral — cache da análise etária

**Objetivo:** validar e integrar de ponta a ponta a entrega A-C já implementada para `GET /dashboard/leads/analise-etaria`, cobrindo backend, frontend, migração, smoke local, evidências e preparação para staging/rollout.

**Escopo desta sessão futura:** integração geral e correções de regressão encontradas.  
**Fora de escopo:** Fase D (fact table / MV / agregação SQL estrutural), redesign funcional do dashboard e novos contratos públicos.

---

## 1. Contexto atual

A implementação já introduziu:

- cache compartilhado no frontend com TanStack Query;
- cache TTL em memória no backend para o endpoint de análise etária;
- versionamento persistido de invalidação em `dashboard_cache_versions`;
- bump de versão ao final bem-sucedido do pipeline Gold;
- testes focados de backend e frontend para o novo comportamento.

O que falta agora é a **integração geral**, isto é:

1. confirmar que o restante do sistema não regrediu;
2. aplicar a migration nova em ambiente real de desenvolvimento/staging;
3. validar o fluxo completo UI -> API -> pipeline -> invalidação;
4. coletar evidências antes de considerar a entrega pronta para rollout.

---

## 2. Arquivos e áreas que devem ser tratados como foco

- Backend:
  - `backend/app/services/dashboard_service.py`
  - `backend/app/services/dashboard_cache_version_service.py`
  - `backend/app/core/dashboard_cache.py`
  - `backend/app/models/dashboard_cache.py`
  - `backend/app/services/lead_pipeline_service.py`
  - `backend/alembic/versions/0c1d2e3f4a5b_create_dashboard_cache_versions.py`
- Frontend:
  - `frontend/src/main.tsx`
  - `frontend/src/hooks/useAgeAnalysis.ts`
- Testes:
  - `backend/tests/test_dashboard_age_analysis_endpoint.py`
  - `backend/tests/test_dashboard_cache_version_service.py`
  - `frontend/src/hooks/__tests__/useAgeAnalysis.test.tsx`
- Operação:
  - `docs/SETUP.md`
  - `Makefile`
  - `render.yaml`

---

## 3. Estratégia da sessão

Executar nesta ordem:

1. sanity check do workspace e baseline;
2. migrations e validação estrutural do backend;
3. suíte ampla de backend;
4. suíte ampla de frontend;
5. smoke local full-stack;
6. teste manual de invalidação por pipeline Gold;
7. profiling e evidências;
8. staging/rollout checklist;
9. correções de regressão que aparecerem;
10. resumo final com status PASS / FAIL por bloco.

Não pular para staging antes de fechar os blocos 1-7.

---

## 4. Pré-voo obrigatório

### 4.1 Conferir estado do repo

Rodar na raiz:

```bash
git status --short
git diff --stat
```

Critério:

- identificar se há mudanças paralelas de outro trabalho;
- não reverter nada que não seja explicitamente da integração;
- se houver drift em arquivos do mesmo fluxo, incorporar com cuidado antes de continuar.

### 4.2 Subir dependências locais

Backend:

```bash
./scripts/dev_backend.sh
```

Frontend:

```bash
cd frontend
npm run dev
```

Checks mínimos:

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/health/ready
```

Critério:

- API responde `ok` e `ready`;
- frontend abre em `http://localhost:5173`;
- worker local de leads também sobe pelo `dev_backend.sh`.

---

## 5. Migration e integração estrutural

### 5.1 Aplicar migration nova

No backend:

```bash
cd backend
alembic upgrade head
```

### 5.2 Validar a tabela nova

Validar no banco alvo que a tabela existe:

```sql
select domain, version, updated_at, reason, source_batch_id
from dashboard_cache_versions
order by updated_at desc
limit 20;
```

Critério:

- a migration aplica sem erro;
- a tabela `dashboard_cache_versions` existe;
- nenhuma migration anterior entra em conflito.

### 5.3 Validar startup pós-migration

Com a migration aplicada, reiniciar API e worker.

Critério:

- subida limpa;
- endpoint `/dashboard/leads/analise-etaria` segue disponível;
- pipeline Gold segue funcional.

---

## 6. Validação ampla de backend

### 6.1 Rodar suíte focada expandida

No Windows/venv do projeto, respeitando o `PYTHONPATH` do repo:

```bash
cmd.exe /c "cd /d C:\Users\NPBB\npbb\backend && set PYTHONPATH=C:\Users\NPBB\npbb;C:\Users\NPBB\npbb\backend && set SECRET_KEY=ci-secret-key && set TESTING=true && .venv\Scripts\python.exe -m pytest -q tests/test_dashboard_age_analysis_service.py tests/test_dashboard_age_analysis_endpoint.py tests/test_dashboard_cache_version_service.py tests/test_lead_gold_pipeline.py"
```

### 6.2 Rodar suíte backend completa

Usar o comando canônico do repo:

```bash
cd backend
SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q
```

Se o shell não tiver `python`, usar o interpretador do venv explicitamente.

### 6.3 Tratar falhas

Classificar cada falha em:

- regressão direta do cache novo;
- fragilidade pré-existente do repo;
- falha de ambiente;
- teste antigo com expectativa incompatível.

Critério:

- tudo que for regressão direta deve ser corrigido na mesma sessão;
- falhas pré-existentes só podem ficar abertas se forem documentadas com evidência clara.

---

## 7. Validação ampla de frontend

### 7.1 Qualidade local

```bash
cd frontend
npm run lint
npm run typecheck
npm run test -- --run
npm run build
```

### 7.2 Pontos específicos a confirmar

- `useAgeAnalysis` não faz request repetido na mesma chave durante `staleTime`;
- troca de usuário/agência não reaproveita resultado anterior;
- `refetch()` mantém os dados antigos visíveis durante atualização;
- a tela continua funcional sem alteração no contrato de props/composição;
- o `QueryClientProvider` não quebrou outras páginas.

### 7.3 Se houver falhas

Prioridade de correção:

1. quebra de rotas ou bootstrap do app;
2. vazamento de cache entre usuários;
3. erros de tipagem e testes;
4. warnings menores.

---

## 8. Smoke local full-stack

### 8.1 Navegação manual

Abrir:

- `http://localhost:5173/dashboard/leads/analise-etaria`

Validar:

- primeira carga funciona;
- mudar filtros dispara uma única carga por chave;
- voltar ao filtro anterior reaproveita cache;
- refresh manual pelo botão continua funcionando;
- mensagens de erro e loading seguem coerentes.

### 8.2 Teste de isolamento por escopo

Executar com dois usuários diferentes:

- um usuário NPBB/admin;
- um usuário agência com `agencia_id` válido.

Validar:

- ambos acessam a tela sem erro indevido;
- o resultado de um não reaparece no outro;
- a agência continua vendo apenas seu escopo.

### 8.3 Teste de dia de referência

Sem mudar o código, confirmar no payload:

- `age_reference_date` vem coerente com `America/Sao_Paulo`;
- a UI não quebra com essa data.

Se necessário, usar mock/monkeypatch em ambiente de teste para confirmar que a chave muda entre dois dias diferentes.

---

## 9. Teste de invalidação por pipeline Gold

### 9.1 Preparar cenário

1. carregar a tela de análise etária para popular o cache;
2. escolher um lote que, ao ser promovido para Gold, afete o mesmo dashboard;
3. disparar o pipeline Gold.

### 9.2 Confirmar bump de versão

Consultar:

```sql
select domain, version, updated_at, reason, source_batch_id
from dashboard_cache_versions
where domain = 'leads_age_analysis';
```

Critério:

- a versão aumenta após promoção Gold bem-sucedida;
- `reason` reflete o bump do pipeline;
- `source_batch_id` aponta para o lote processado.

### 9.3 Confirmar efeito no endpoint/UI

Após o bump:

- fazer novo GET do endpoint com os mesmos filtros;
- atualizar a UI;
- verificar que o resultado novo reflete os dados mais recentes.

Critério:

- o request pós-bump não reutiliza entrada antiga;
- o dashboard reflete a nova realidade sem precisar alterar contrato da rota.

---

## 10. Profiling e evidências

### 10.1 Rodar profiling dedicado

Usar o script já existente:

```bash
cd backend
python scripts/profile_dashboard_age_analysis.py
```

Se o repo exigir `DIRECT_URL`/`DATABASE_URL` reais para o profiling, configurar antes da execução.

### 10.2 Evidências mínimas a salvar

Salvar em `auditoria/evidencias/`:

- resultado antes/depois do profiling, se houver baseline comparável;
- tempos de hit e miss do endpoint;
- evidência de bump em `dashboard_cache_versions`;
- logs/prints relevantes da UI ou chamadas HTTP;
- resumo do que passou/falhou na integração.

### 10.3 Métricas a observar

- tempo de resposta em miss;
- tempo de resposta em hit;
- redução de chamadas repetidas no frontend;
- logs/metricas `cache hit/miss`;
- tamanho do payload e ausência de erro no contrato.

---

## 11. Gate de qualidade do repo

Rodar, se o ambiente suportar:

```bash
make ci-quality
```

Se `ci-quality` falhar por motivos fora deste fluxo, registrar exatamente:

- comando;
- erro;
- classificação: regressão nova vs. problema legado.

Não declarar a integração pronta sem ao menos tentar esse gate ou justificar claramente por que ele não pôde rodar.

---

## 12. Checklist de staging / rollout

### 12.1 Pré-deploy

- migration revisada;
- `render.yaml` sem conflito com a nova dependência do frontend;
- build local verde;
- testes focados do cache verdes;
- backend completo verificado.

### 12.2 Deploy

1. aplicar migration no alvo;
2. subir API com a nova versão;
3. subir worker com a nova versão;
4. validar `/health/ready`;
5. validar dashboard manualmente;
6. executar um pipeline Gold controlado;
7. confirmar bump de versão e leitura nova do dashboard.

### 12.3 Rollback

Se houver problema:

- rollback de app para build anterior;
- manter atenção para a tabela `dashboard_cache_versions`, que é aditiva e não deve quebrar rollback do código anterior;
- limpar cache em memória reiniciando o processo web, se necessário;
- documentar se o problema estava em migration, bootstrap, tenant scope ou pipeline invalidation.

---

## 13. Critérios de aceite finais

Considerar a integração geral concluída apenas se:

- migration aplicada com sucesso;
- suíte focada backend/frontend verde;
- build frontend verde;
- smoke local full-stack validado;
- invalidação por pipeline Gold comprovada;
- evidências salvas;
- sem vazamento de cache entre usuários/agências;
- sem quebra de contrato do endpoint ou da tela.

---

## 14. Entregáveis da próxima sessão

Ao final da sessão de integração, produzir:

1. correções de regressão encontradas;
2. evidências em `auditoria/evidencias/`;
3. resumo final em Markdown com:
   - comandos executados;
   - o que passou;
   - o que falhou;
   - o que ficou pendente;
   - decisão final: pronto para staging / bloqueado.

---

## 15. Observações para quem assumir a próxima sessão

- O cache de backend é **in-memory por processo**, então o objetivo agora é validar corretamente o comportamento no deploy atual, não torná-lo distribuído.
- A Fase D continua adiada; não abrir refactor estrutural de SQL/MV no meio da integração geral.
- Se aparecer falha de timezone em testes, alinhar a expectativa com `America/Sao_Paulo`, não voltar para `date.today()` puro.
- Se aparecer falha envolvendo `lead_pipeline`, garantir `PYTHONPATH` correto antes de mexer no código.
- Se a suíte ampla falhar por problemas legados já conhecidos do repo, documentar isso explicitamente e isolar do status da integração do cache.
