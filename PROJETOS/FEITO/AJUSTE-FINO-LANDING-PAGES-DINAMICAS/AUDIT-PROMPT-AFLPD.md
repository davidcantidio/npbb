# Prompt de Auditoria — AJUSTE-FINO-LANDING-PAGES-DINAMICAS
**uso:** colar este prompt inteiro em uma sessão com acesso ao repositório
**escopo:** aderência ao PRD v1.2, antecipação de bugs, refatoração de código monolítico

---

## Contexto que você precisa ter antes de começar

Você é um engenheiro sênior realizando auditoria pós-implementação do projeto
`AJUSTE-FINO-LANDING-PAGES-DINAMICAS` (AFLPD), composto por 4 fases:

- **F1** — Redesign layout form-first e conteúdo derivado da ativação
- **F2** — Rastreabilidade backend (migration + extensão de payload + endpoint de gamificação)
- **F3** — Componente `GamificacaoBlock` + integração no `LandingPageView`
- **F4** — QA, regressão visual e gate de promoção

O PRD de referência é `PRD-LANDING-REDESIGN-ATIVACAO-v1.2.md`. O conjunto de épicos
(F1 a F4) detalha as issues, critérios de aceite e Definition of Done de cada fase.

A auditoria tem três dimensões independentes, executadas em sequência:
1. **Aderência ao PRD** — o que foi implementado corresponde ao que foi especificado?
2. **Antecipação de bugs** — o que pode quebrar em produção que os testes não cobriram?
3. **Saúde do código** — há código monolítico, duplicação ou acoplamento desnecessário?

---

## DIMENSÃO 1 — Aderência ao PRD

### 1.1 Frontend — Layout e Visual (LPD-REDESIGN-01)

Abra `frontend/src/components/landing/LandingPageView.tsx` e verifique cada item:

**Checklist — responda ✅ ou ❌ para cada item, com localização exata no código:**

- [ ] O `Grid` container do hero foi reestruturado para posicionar o formulário à direita em desktop?
- [ ] O item do formulário possui `sx={{ order: { xs: -1, md: 0 } }}` ou equivalente para mobile?
- [ ] A altura mínima do hero (`minHeight`) garante que o formulário fique above the fold em 375px?
- [ ] Todos os `Paper` do componente têm `borderRadius: 3` (ou equivalente a 24px)?
  - Liste quais `Paper` foram encontrados e seus valores de `borderRadius`
- [ ] Os chips `data.template.mood`, `data.template.categoria` e o chip condicional "Radical" estão removidos da view pública?
- [ ] Esses chips estão presentes dentro de um bloco `{isPreview && (...)}` ou equivalente?
- [ ] A hero image tem renderização condicional baseada em `data.marca.url_hero_image`?
- [ ] Existe fallback visual (background gradient/cor do tema) quando a hero image está ausente?
- [ ] O logo BB foi substituído de texto `"BB"` para `<img src="/logo-bb.svg">` ou SVG?
- [ ] O asset `/logo-bb.svg` existe em `frontend/public/`?
- [ ] `renderGraphicOverlay()`, `buildLandingTheme()`, `getLayoutVisualSpec()` e `ThemeProvider` permanecem intocados?

**Investigação adicional:**
Rode um grep no componente e reporte o resultado:
```bash
grep -n "borderRadius" frontend/src/components/landing/LandingPageView.tsx
grep -n "mood\|categoria\|Radical" frontend/src/components/landing/LandingPageView.tsx
grep -n "url_hero_image" frontend/src/components/landing/LandingPageView.tsx
grep -n "logo-bb\|\"BB\"" frontend/src/components/landing/LandingPageView.tsx
```

---

### 1.2 Frontend — Conteúdo Derivado da Ativação (LPD-REDESIGN-02)

- [ ] O título do formulário usa `data.ativacao?.nome ?? data.evento.nome`?
  - **Atenção:** o PRD seção 07 mostra um erro — o fallback está como `data.template.cta_text`, mas o correto é `data.evento.nome`. Verificar qual foi implementado.
- [ ] O subtítulo usa `data.ativacao?.descricao ?? data.evento.descricao_curta`?
- [ ] Existe um `<Alert severity="info">` condicional com `data.ativacao?.mensagem_qrcode`?
- [ ] O texto do CTA resolve `data.evento.cta_personalizado ?? data.template.cta_text`?
- [ ] O bloco "Sobre o evento" está condicional (só renderiza se descrição disponível)?
- [ ] O tipo `LandingAtivacaoInfo` existe no arquivo de tipos?
- [ ] `LandingPageData` inclui campo `ativacao?: LandingAtivacaoInfo | null`?
- [ ] `LandingPageData` inclui campo `gamificacoes: GamificacaoPublic[]`?

**Investigação adicional:**
```bash
grep -n "ativacao\?.nome\|evento\.nome\|template\.cta_text" frontend/src/components/landing/LandingPageView.tsx
grep -n "LandingAtivacaoInfo\|GamificacaoPublic\|LandingPageData" frontend/src/types/landing_public.ts
```

---

### 1.3 Backend — Migration (LPD-REDESIGN-04)

Abra o modelo `AtivacaoLead` em `backend/app/models/models.py`:

- [ ] Campo `gamificacao_id: Optional[int]` com `foreign_key="gamificacao.id"` existe?
- [ ] Campo `gamificacao_completed: Optional[bool]` com `default=False` existe?
- [ ] Campo `gamificacao_completed_at: Optional[datetime]` com `default=None` existe?

Abra a migration correspondente em `backend/alembic/versions/`:

- [ ] A migration adiciona as 3 colunas como nullable?
- [ ] A FK tem `ON DELETE SET NULL`?
- [ ] O downgrade remove as 3 colunas corretamente?

**Investigação adicional:**
```bash
grep -n "gamificacao_id\|gamificacao_completed" backend/app/models/models.py
ls -lt backend/alembic/versions/ | head -5
grep -n "gamificacao\|ON DELETE" backend/alembic/versions/<migration_mais_recente>.py
```

---

### 1.4 Backend — Contrato de API (LPD-REDESIGN-05)

**`GET /ativacoes/{id}/landing`:**

- [ ] O handler inclui os campos `ativacao` (com `id`, `nome`, `descricao`, `mensagem_qrcode`) no payload?
- [ ] O campo `gamificacoes` é sempre um array (nunca `null`)?
- [ ] Os campos existentes (`evento`, `template`, `formulario`, `marca`, `acesso`) continuam presentes?
- [ ] `template` mantém `graphics_style`, `mood` e `categoria` (não foram removidos)?

**`POST /leads/`:**

- [ ] A response inclui `ativacao_lead_id: int`?
- [ ] O handler extrai e retorna o ID do registro `AtivacaoLead` criado?

**`POST /ativacao-leads/{ativacao_lead_id}/gamificacao` (endpoint novo):**

- [ ] O endpoint existe no router?
- [ ] Recebe `gamificacao_id` e `gamificacao_completed`?
- [ ] Retorna 404 quando `ativacao_lead_id` não existe?
- [ ] Retorna 400 quando `gamificacao_id` inválido?
- [ ] `gamificacao_completed_at` é preenchido com `datetime.utcnow()` pelo backend (não vem do request)?
- [ ] O endpoint é idempotente (chamadas repetidas atualizam o mesmo registro sem duplicar)?

**Investigação adicional:**
```bash
grep -rn "ativacao_lead_id\|gamificacao_completed_at" backend/app/routers/
grep -rn "ativacao-leads" backend/app/routers/
cat backend/app/schemas/gamificacao_landing.py 2>/dev/null || echo "arquivo não encontrado"
```

---

### 1.5 Frontend — GamificacaoBlock (LPD-REDESIGN-03)

Abra `frontend/src/components/landing/GamificacaoBlock.tsx`:

- [ ] O arquivo existe?
- [ ] O tipo `GamificacaoState` é `"presenting" | "active" | "completed"` (sem `"idle"`)?
- [ ] O estado inicial do `useState` é `"presenting"`?
- [ ] O botão "Quero participar" está desabilitado quando `!leadSubmitted`?
- [ ] O texto "Preencha o cadastro acima para participar" é renderizado quando `!leadSubmitted`?
- [ ] A transição `PRESENTING → ACTIVE` verifica `leadSubmitted === true` como guard explícito?
- [ ] A transição `ACTIVE → COMPLETED` chama `onComplete(gamificacao.id)`?
- [ ] O estado `COMPLETED` renderiza `titulo_feedback` e `texto_feedback`?
- [ ] O botão "Nova pessoa" chama `onReset()` e reseta o estado interno para `"presenting"`?
- [ ] Existe tratamento de loading/erro na chamada de `onComplete`?

**No `LandingPageView.tsx`:**

- [ ] O bloco `{data.gamificacoes?.length > 0 ? <GamificacaoBlock ... /> : null}` existe?
- [ ] O bloco está posicionado após o conteúdo principal e antes do footer?
- [ ] O pai possui estados `leadSubmitted` e `ativacaoLeadId`?
- [ ] O `handleSubmitSuccess` seta ambos os estados após submit?
- [ ] O `handleGamificacaoComplete` tem guard `if (!ativacaoLeadId) return`?
- [ ] O `handleReset` limpa `leadSubmitted`, `ativacaoLeadId` e o estado do formulário?

**Investigação adicional:**
```bash
grep -n "leadSubmitted\|ativacaoLeadId\|GamificacaoBlock" frontend/src/components/landing/LandingPageView.tsx
grep -n "GamificacaoState\|presenting\|active\|completed" frontend/src/components/landing/GamificacaoBlock.tsx
```

---

## DIMENSÃO 2 — Antecipação de Bugs

Para cada item abaixo, verifique o código e classifique o risco como 🔴 alto, 🟡 médio ou 🟢 baixo. Inclua o trecho de código relevante e a correção sugerida.

### 2.1 Bugs de Tipagem e Nullability

**B-01 — `data.gamificacoes` pode ser `undefined` em payloads antigos**

O campo `gamificacoes` é novo no payload. Payloads cacheados ou de ativações antigas
podem não incluí-lo. O consumer em `LandingPageView` usa `data.gamificacoes.length`
diretamente?

Verificar: há `data.gamificacoes?.length` ou `(data.gamificacoes ?? []).length`?
Se não, isso é um crash garantido em produção com dados legados.

**B-02 — `data.ativacao` null não tratado na cadeia de fallback**

O título do formulário usa `data.ativacao?.nome ?? data.evento.nome`. Mas o subtítulo
e o callout também tratam o caso `data.ativacao === null`? Verificar se existe algum
`data.ativacao.descricao` sem optional chaining.

**B-03 — `ativacao_lead_id` ausente na response legacy**

Se o `POST /leads/` falhar silenciosamente em retornar `ativacao_lead_id` (ex: bug no
serializer), o `handleGamificacaoComplete` vai receber `null`. O guard existe mas o
botão de gamificação ficará habilitado sem que a chamada seja possível. Como o usuário
é informado desse erro?

**B-04 — Race condition no reset**

O `handleReset` reseta `leadSubmitted`, `ativacaoLeadId` e o estado do formulário.
Se o reset acontece enquanto `handleGamificacaoComplete` ainda está em flight (await),
o `ativacaoLeadId` pode ser `null` quando a chamada terminar. O guard `if (!ativacaoLeadId) return`
no início da função não protege o await que já foi iniciado.

Verificar: o botão "Concluí" é desabilitado durante o loading? O reset pode ser
disparado enquanto a chamada está em andamento?

**B-05 — `gamificacao_completed_at` com timezone**

O backend usa `datetime.utcnow()`. Em Python 3.12+, `datetime.utcnow()` é deprecated
em favor de `datetime.now(timezone.utc)`. Verificar qual foi usado e se o campo
`TIMESTAMP WITH TIME ZONE` da migration está alinhado com o formato retornado.

### 2.2 Bugs de Fluxo e Estado

**B-06 — Estado `COMPLETED` após reset do formulário**

Se o usuário clica "Nova pessoa" e o `handleReset` reseta o estado do pai, o
`GamificacaoBlock` volta para `PRESENTING` via `onReset`. Mas se o componente for
desmontado e remontado (ex: condicional `gamificacoes.length > 0` re-avaliada),
o estado interno é resetado automaticamente. Verificar se há alguma inconsistência
entre o reset via `onReset` e o reset via desmontagem.

**B-07 — Guard de transição PRESENTING → ACTIVE**

A especificação exige que o guard verifique `leadSubmitted === true` explicitamente.
Se o botão "Quero participar" não estiver desabilitado via `disabled={!leadSubmitted}`
E também não houver verificação no handler de clique, um clique rápido antes do
submit pode causar transição inválida. Verificar se o guard existe em dois lugares
(atributo `disabled` E handler) ou apenas em um.

**B-08 — Idempotência do endpoint de gamificação**

O endpoint `POST /ativacao-leads/{id}/gamificacao` deve ser idempotente. Verificar:
o handler faz `UPDATE` (idempotente) ou `INSERT`? Se fizer `INSERT` ou verificar
`gamificacao_completed` antes de atualizar, pode rejeitar uma segunda chamada
(ex: retry após erro de rede) como erro em vez de sucesso.

**B-09 — `mensagem_qrcode` com conteúdo inseguro**

O callout renderiza `data.ativacao.mensagem_qrcode` diretamente. Verificar se há
sanitização de XSS. O PRD especifica renderização como texto puro (sem `dangerouslySetInnerHTML`),
mas se o componente `<Alert>` do MUI recebe children como string, está seguro — confirmar.

### 2.3 Bugs de API e Contrato

**B-10 — `gamificacoes: []` vs `gamificacoes: null` no payload**

O PRD especifica que `gamificacoes` é SEMPRE um array (nunca `null`). Se o backend
retornar `null` quando não há gamificação (ex: join retorna `None`), o frontend
quebrará em `data.gamificacoes.length`. Verificar o serializer Pydantic:
`gamificacoes: List[GamificacaoPublicSchema] = []` com default vazio?

**B-11 — FK constraint em `gamificacao_id` sem `ON DELETE SET NULL`**

Se a migration não incluiu `ON DELETE SET NULL`, deletar uma gamificação causará erro
de FK em todos os `AtivacaoLead` que a referenciam. Verificar o DDL gerado pela migration.

**B-12 — Cache do payload de landing**

Se o payload `GET /ativacoes/{id}/landing` for cacheado (Redis, CDN ou in-memory),
o cache pode não incluir os novos campos `ativacao` e `gamificacoes`. Verificar se
existe cache e se a estratégia de invalidação/cache key foi atualizada.

---

## DIMENSÃO 3 — Saúde do Código

### 3.1 Complexidade e Responsabilidade Única

**Analisar `LandingPageView.tsx`:**

Conte o número de linhas do componente. Se ultrapassar 300 linhas, mapear:
- Quantos `useState` existem no componente raiz?
- O componente mistura lógica de negócio (resolução de fallbacks, handlers de API) com JSX de layout?
- A lógica de resolução de conteúdo (`ativacao.nome ?? evento.nome`) está centralizada em uma função `resolveLandingContent(data)` ou espalhada inline?

**Ação esperada se problema encontrado:**
Listar candidatos a extração: quais trechos se beneficiariam de custom hooks (`useGamificacaoState`, `useLandingContent`) ou componentes separados (`HeroContextual`, `FormularioCaptacao`)?

**Analisar `GamificacaoBlock.tsx`:**

- O JSX do componente ultrapassa 100 linhas?
- Os sub-estados visuais (`GamificacaoCard`, `GamificacaoFeedback`) foram extraídos ou estão inline?
- A lógica de loading/erro está misturada com a máquina de estados?

### 3.2 Duplicação

Verificar se a cadeia de fallback de conteúdo (`ativacao.nome ?? evento.nome`,
`ativacao.descricao ?? evento.descricao_curta`, etc.) está repetida em mais de um lugar.
Se sim, extrair para `resolveLandingContent(data: LandingPageData)`.

```bash
grep -n "ativacao?.nome\|evento\.nome\|cta_personalizado" frontend/src/components/landing/LandingPageView.tsx | wc -l
```

Se o resultado for > 1 para a mesma expressão, há duplicação.

### 3.3 Schemas Pydantic

- Os schemas novos (`LandingAtivacaoSchema`, `GamificacaoPublicSchema`, `GamificacaoCompleteRequest`,
  `GamificacaoCompleteResponse`) foram criados em arquivo separado conforme especificado
  (`backend/app/schemas/gamificacao_landing.py`) ou foram adicionados em schemas existentes?
- Se adicionados em schemas existentes, isso polui módulos com responsabilidade diferente —
  registrar como refatoração necessária.

### 3.4 Handler de endpoint com mais de 20 linhas

O PRD especifica que handlers com mais de 20 linhas devem ter a lógica extraída para
use case separado. Verificar:

```bash
grep -n "def " backend/app/routers/ativacoes.py backend/app/routers/leads.py 2>/dev/null
```

Para cada handler dos endpoints afetados, contar linhas. Se ultrapassar 20, verificar
se use case foi criado ou se lógica está inline no handler.

### 3.5 Testes

Verificar existência e qualidade:

```bash
find backend/tests -name "*.py" | xargs grep -l "gamificacao\|ativacao_lead" 2>/dev/null
find frontend/src -name "*.test.*" | xargs grep -l "GamificacaoBlock\|LandingPageView" 2>/dev/null
```

- Existem testes para o endpoint novo `POST /ativacao-leads/{id}/gamificacao`?
- Existem testes para o `GamificacaoBlock` cobrindo as 3 transições de estado?
- Os testes do `LandingPageView` cobrem o cenário com `data.gamificacoes = []`?
- Existe algum teste e2e do fluxo completo UC-03?

---

## Formato do Relatório de Saída

Ao final da auditoria, gere um relatório estruturado com as seguintes seções:

```markdown
# Relatório de Auditoria — AFLPD
**data:** <data>
**revisor:** <nome>
**versão auditada:** <hash do commit ou tag>

## Resumo Executivo
<2-3 frases com veredicto geral: pronto para produção, precisa de correções menores, ou bloqueado>

## 1. Aderência ao PRD
### Itens conformes ✅
<lista com referência ao critério e localização no código>

### Itens não conformes ❌
<lista com critério, o que foi encontrado, e correção necessária>

### Itens não verificáveis (sem evidência)
<lista de itens que não puderam ser verificados e por quê>

## 2. Bugs Antecipados
| ID | Descrição | Risco | Arquivo:Linha | Correção sugerida |
|---|---|---|---|---|
| B-01 | ... | 🔴 | ... | ... |

## 3. Débitos de Código
| Componente/Arquivo | Problema | Impacto | Ação sugerida |
|---|---|---|---|
| ... | ... | ... | ... |

## 4. Cobertura de Testes
| Funcionalidade | Teste existe? | Tipo | Observação |
|---|---|---|---|
| ... | ✅/❌ | unit/integration/e2e | ... |

## 5. Decisão
**promote** / **hold**

Justificativa:
<mínimo 3 frases com fundamentação objetiva>

Ações bloqueantes (se hold):
1. <ação específica com responsável e arquivo>
2. ...

Ações não-bloqueantes (melhorias para próxima sprint):
1. ...
```

---

## Notas para o auditor

- Os 3 testes pré-existentes com falha em `test_leads_import_etl_usecases.py`
  (strict keyword argument mismatch) são falhas conhecidas **não relacionadas** a este projeto — ignorar.
- O veredicto `promote` requer **zero** itens ❌ de aderência ao PRD nos blocos
  LPD-REDESIGN-01 a LPD-REDESIGN-05, e **zero** bugs de risco 🔴.
- Bugs de risco 🟡 podem ir para produção acompanhados de issue registrada.
- Débitos de código não bloqueiam promoção, mas devem ser registrados.
