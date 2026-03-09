# PRD — Redesign e Evolução da Landing Page de Ativação (v1.2)
**Banco do Brasil · Plataforma NPBB — Módulo de Landing Pages Dinâmicas**

| Campo | Valor |
|---|---|
| Produto | Landing Pages de Ativação — Redesign v2 |
| Iniciativa | BB-LANDING-PAGES-DINAMICAS — Sprint de Qualidade |
| Versão | 1.2 |
| Data | Março 2026 |
| Status | Em revisão |
| Referência | `frontend/src/components/landing/LandingPageView.tsx` · `PRD-BB-Landing-Pages-Dinamicas.md` |

---

## Histórico de Revisões

| Versão | Correções |
|---|---|
| 1.0 | Rascunho inicial |
| 1.1 | (1) `graphics_style` e `renderGraphicOverlay()` restaurados; (2) `mood`/`categoria` mantidos no payload, removidos apenas da view pública; (3) bloco de gamificação posicionado como seção da página, não dependente de submit |
| 1.2 | (A) Eliminação do Fluxo B — botões de gamificação só habilitados após submit, evitando necessidade de endpoint PATCH não especificado; endpoint `POST /ativacao-leads/{id}/gamificacao` adicionado para persistência pós-submit; (B) Cenário de múltiplas gamificações movido para fora de escopo — requer mudança de schema; (C) Estado `IDLE` removido da máquina de estados interna ao `GamificacaoBlock` — responsabilidade delegada ao componente pai |

---

## Sumário Executivo

Este documento define os requisitos para a segunda iteração da landing page de ativação do NPBB. Os problemas centrais são: (1) layout inadequado que não prioriza o formulário acima da dobra; (2) dados de configuração interna expostos como texto ao usuário (`mood` como chip, `categoria` como badge); (3) ausência de integração real com os dados da ativação — formulário hoje é genérico, ignorando nome, descrição, CTA e gamificação da ativação cadastrada; (4) rastreabilidade incompleta — conversão não registra qual gamificação foi responsável pela captação.

---

## 01 · Diagnóstico do Estado Atual

### 1.1 Problemas de Layout e Apresentação

| Problema | Localização | Impacto |
|---|---|---|
| `borderRadius: 6` (48px) nos cards | Todos os `Paper` em `LandingPageView.tsx` | Conflita com linguagem visual BB |
| Formulário não aparece above the fold | Grid hero de 2 colunas com formulário posicionado abaixo no fluxo de documento | Usuário precisa rolar para interagir |
| Chip `{data.template.mood}` visível na view pública | Hero card | "Profissional, confiavel e estrategico" exposto como conteúdo ao usuário final |
| Chips `categoria` e "Radical" visíveis na view pública | Hero card | Dados de configuração interna expostos |
| Hero image obrigatória no grid | `Box component="img"` sem condicional | Layout quebrado quando `url_hero_image` é placeholder |
| Logo BB como texto `"BB"` em `Box` | Blocos de logo no hero e footer | Marca mal representada |

### 1.2 O que não é alterado

- **`graphics_style` permanece no payload público** — consumido funcionalmente por `renderGraphicOverlay()`, não exibido como texto.
- **`renderGraphicOverlay()` não é alterada** — é o mecanismo central de diferenciação visual entre templates.
- **`mood` e `categoria` permanecem em `LandingTemplateConfig`** — apenas seus chips de texto são removidos da view pública. O modo `preview` do backoffice pode continuar exibindo-os.

### 1.3 Problemas de Vínculo com a Ativação

| Campo ignorado hoje | Uso esperado |
|---|---|
| `Ativacao.nome` | Título do formulário |
| `Ativacao.descricao` | Contexto abaixo do título |
| `Ativacao.mensagem_qrcode` | Callout de orientação acima dos campos |
| `Ativacao.gamificacao_id` | Determina se bloco de gamificação é renderizado |
| `Gamificacao.*` | Alimenta o fluxo gamificado |

### 1.4 Problemas de Rastreabilidade

- `AtivacaoLead` não possui `gamificacao_id` — impossível saber qual gamificação um lead completou.
- `LandingSubmitPayload` não carrega `gamificacao_id`.
- `LandingSubmitResponse` não retorna `ativacao_lead_id` — impossível referenciar o registro criado em chamadas subsequentes.

---

## 02 · Objetivos

1. **Form-first** — formulário visível acima da dobra em todos os breakpoints.
2. **Ativação-driven** — título, subtítulo, CTA e orientação derivados dos dados da ativação.
3. **Gamificação integrada** — bloco visível desde o carregamento; participação habilitada após submit do formulário; feedback inline; persistência via endpoint dedicado.
4. **Identidade BB limpa** — remoção de chips de texto internos e border-radius excessivo, sem destruir infraestrutura de diferenciação visual.
5. **Rastreabilidade completa** — lead convertido registra `ativacao_id` e `gamificacao_id`.

---

## 03 · Requisitos Funcionais

### 3.1 Novo Layout — Form-First

#### 3.1.1 Estrutura da Página

```
┌─────────────────────────────────────────────────────────┐
│  HEADER  (logo BB — imagem/SVG + nome do evento)        │
├──────────────────────┬──────────────────────────────────┤
│                      │                                  │
│  HERO CONTEXTUAL     │  FORMULÁRIO  ← above the fold    │
│  — nome da ativação  │  — título: ativacao.nome         │
│  — descrição curta   │  — callout: mensagem_qrcode      │
│  — imagem (opcional) │  — campos configurados           │
│                      │  — consentimento LGPD            │
│                      │  — CTA primário                  │
│                      │                                  │
├──────────────────────┴──────────────────────────────────┤
│  BLOCO GAMIFICAÇÃO  (renderizado pelo pai apenas quando  │
│  gamificacoes.length > 0)                               │
├─────────────────────────────────────────────────────────┤
│  FOOTER MARCA BB                                        │
└─────────────────────────────────────────────────────────┘
```

**Mobile:** formulário aparece primeiro (`order: -1`), antes do bloco hero contextual.

#### 3.1.2 Ajustes Visuais

| Elemento | Antes | Depois |
|---|---|---|
| `borderRadius` de todos os `Paper` | `6` (48px) | `3` (24px) |
| Chip `{data.template.mood}` | Visível na view pública | Removido da view pública; mantido no modo `preview` |
| Chips `categoria` e "Radical" | Visíveis na view pública | Removidos da view pública; mantidos no modo `preview` |
| `renderGraphicOverlay()` | Presente e funcional | Mantida sem alteração |
| Hero image | Sempre renderizada | Condicional — apenas se `url_hero_image` presente e não vazia |
| Logo BB | Texto `"BB"` em `Box` | `<img>` ou SVG do grafema BB |
| Bloco "Sobre o evento" | Sempre visível | Condicional — apenas se `ativacao.descricao` ou `evento.descricao_curta` não vazio |

### 3.2 Título, Subtítulo e CTA Derivados da Ativação

| Elemento de UI | Fonte (prioridade decrescente) |
|---|---|
| Título da seção do formulário | `ativacao.nome` → `evento.nome` |
| Subtítulo / descrição de contexto | `ativacao.descricao` → `evento.descricao_curta` |
| Callout de orientação (acima dos campos) | `ativacao.mensagem_qrcode` — exibido somente se presente |
| Texto do botão CTA | `evento.cta_personalizado` → `template.cta_text` |
| Mensagem de sucesso | `formulario.mensagem_sucesso` (sem alteração) |

Nenhum campo de `template` (`mood`, `categoria`, `tema`, `tone_of_voice`) deve ser renderizado como texto visível na view pública.

### 3.3 Fluxo de Gamificação na Landing

#### 3.3.1 Posicionamento e Habilitação

O bloco de gamificação é uma **seção da página**, renderizada pelo componente pai quando `data.gamificacoes.length > 0`. O bloco é **visível desde o carregamento** — o usuário lê nome, descrição e prêmio da gamificação antes de preencher o formulário.

Os **botões de interação** (participar, concluir) ficam **desabilitados** até que o formulário seja submetido com sucesso. Um texto de orientação explica: *"Preencha o cadastro acima para participar."*

Essa decisão garante que `ativacao_lead_id` já exista quando o usuário concluir a gamificação, eliminando a necessidade de busca ou criação retroativa de registro.

#### 3.3.2 Estrutura do Bloco

O modelo atual suporta no máximo 1 gamificação por ativação (`Ativacao.gamificacao_id` como FK única). O bloco exibe o card diretamente, sem dropdown. Suporte a múltiplas gamificações está fora de escopo desta versão (ver seção 11).

```
Estado PRESENTING (antes do submit):
┌─────────────────────────────────────────────┐
│  🏆  [gamificacao.nome]                     │
│  [gamificacao.descricao]                    │
│  Prêmio: [gamificacao.premio]               │
│                                             │
│  [Quero participar]  ← desabilitado         │
│  "Preencha o cadastro acima para participar"│
└─────────────────────────────────────────────┘

Estado PRESENTING (após submit):
┌─────────────────────────────────────────────┐
│  🏆  [gamificacao.nome]                     │
│  [gamificacao.descricao]                    │
│  Prêmio: [gamificacao.premio]               │
│                                             │
│  [Quero participar]  ← habilitado           │
└─────────────────────────────────────────────┘
```

#### 3.3.3 Máquina de Estados do `GamificacaoBlock`

O componente é montado pelo pai somente quando `data.gamificacoes.length > 0`. Não existe estado `IDLE` interno — a decisão de não montar é do pai.

```
PRESENTING  →  ACTIVE  →  COMPLETED
               ↑
         (requer leadSubmitted === true
          + ação do usuário)
```

| Estado | Descrição | Gatilho de entrada |
|---|---|---|
| `PRESENTING` | Card visível; botão desabilitado ou habilitado conforme `leadSubmitted` | Montagem do componente |
| `ACTIVE` | Instruções de participação visíveis; botão "Concluí" disponível | `leadSubmitted === true` + clique em "Quero participar" |
| `COMPLETED` | `titulo_feedback` + `texto_feedback` exibidos | Clique em "Concluí" + `onComplete` disparado |

Transições:
- Montagem → `PRESENTING`
- `PRESENTING` → `ACTIVE`: requer `leadSubmitted === true` + clique do usuário
- `ACTIVE` → `COMPLETED`: clique em "Concluí" → dispara `onComplete(gamificacaoId)`
- `COMPLETED` → `PRESENTING`: clique em "Nova pessoa" → reset completo (formulário + bloco)

---

## 04 · Rastreabilidade — Modelo de Dados

### 4.1 Extensão de `AtivacaoLead`

| Campo | Tipo | Nullable | Default | Descrição |
|---|---|---|---|---|
| `gamificacao_id` | `INTEGER FK gamificacao.id` | sim | NULL | Gamificação concluída pelo lead |
| `gamificacao_completed` | `BOOLEAN` | sim | FALSE | Se o lead completou a gamificação |
| `gamificacao_completed_at` | `TIMESTAMP WITH TIME ZONE` | sim | NULL | Data/hora da conclusão |

Migration com todos os campos nullable/com default — sem lock de tabela, sem impacto em registros existentes.

### 4.2 `LeadConversao` — sem alteração

O registro de conclusão de gamificação pertence a `AtivacaoLead`. Nenhuma alteração em `LeadConversao`.

---

## 05 · Contrato de API

### 5.1 `GET /ativacoes/{id}/landing` — Extensão do Payload

Campos adicionados ao payload existente (nenhum campo removido):

```json
{
  "ativacao_id": 10,
  "ativacao": {
    "id": 10,
    "nome": "Stand Principal — Skate Open",
    "descricao": "Venha conhecer os atletas patrocinados pelo BB",
    "mensagem_qrcode": "Escaneie para se cadastrar e concorrer!"
  },
  "gamificacoes": [
    {
      "id": 5,
      "nome": "Desafio do Ollie",
      "descricao": "Execute um ollie e mostre para o promotor!",
      "premio": "Squeeze BB exclusivo",
      "titulo_feedback": "Arrasei! 🛹",
      "texto_feedback": "Você completou o desafio e está concorrendo ao prêmio!"
    }
  ],
  "evento": { "...sem alterações..." },
  "template": { "...todos os campos mantidos incluindo graphics_style, mood, categoria..." },
  "formulario": { "...sem alterações..." },
  "marca": { "...sem alterações..." },
  "acesso": { "...sem alterações..." }
}
```

`gamificacoes` é sempre um array — vazio (`[]`) quando não há gamificação vinculada.

### 5.2 `POST /leads/` — Extensão

**Request** (campos adicionados):
```json
{
  "...campos existentes...",
  "gamificacao_id": null,
  "gamificacao_completed": false
}
```

**Response** (campos adicionados):
```json
{
  "lead_id": 1,
  "ativacao_lead_id": 42,
  "event_id": 123,
  "ativacao_id": 10,
  "gamificacao_id": null,
  "gamificacao_completed": false,
  "mensagem_sucesso": "string"
}
```

`ativacao_lead_id` é novo e necessário para o endpoint de gamificação.

### 5.3 `POST /ativacao-leads/{ativacao_lead_id}/gamificacao` — Novo Endpoint

Atualiza os campos de gamificação em `AtivacaoLead` após o submit do formulário.

**Request:**
```json
{
  "gamificacao_id": 5,
  "gamificacao_completed": true
}
```

**Response:**
```json
{
  "ativacao_lead_id": 42,
  "gamificacao_id": 5,
  "gamificacao_completed": true,
  "gamificacao_completed_at": "2026-03-06T18:00:00Z"
}
```

**Autenticação:** endpoint público, protegido pelo `ativacao_lead_id` opaco retornado no submit. O frontend não precisa de token — o ID já limita o acesso ao registro criado naquela sessão.

---

## 06 · Especificação de Tipos Frontend

### 6.1 Extensão de `LandingPageData`

```typescript
// landing_public.ts

export type GamificacaoPublic = {
  id: number;
  nome: string;
  descricao: string;
  premio: string;
  titulo_feedback: string;
  texto_feedback: string;
};

export type LandingAtivacaoInfo = {
  id: number;
  nome: string;
  descricao?: string | null;
  mensagem_qrcode?: string | null;
};

export type LandingPageData = {
  ativacao_id?: number | null;
  ativacao?: LandingAtivacaoInfo | null;       // NOVO
  gamificacoes: GamificacaoPublic[];           // NOVO — sempre array
  evento: LandingEvent;
  template: LandingTemplateConfig;             // sem remoção de campos
  formulario: LandingForm;
  marca: LandingBrand;
  acesso: LandingAccess;
};
```

### 6.2 Extensão de Submit

```typescript
export type LandingSubmitPayload = {
  // ...campos existentes...
  gamificacao_id?: number | null;              // NOVO
  gamificacao_completed?: boolean | null;      // NOVO
};

export type LandingSubmitResponse = {
  lead_id: number;
  ativacao_lead_id: number;                    // NOVO
  event_id: number;
  ativacao_id?: number | null;
  gamificacao_id?: number | null;
  gamificacao_completed?: boolean | null;
  mensagem_sucesso: string;
};
```

### 6.3 Novo serviço para endpoint de gamificação

```typescript
export type GamificacaoCompletePayload = {
  gamificacao_id: number;
  gamificacao_completed: boolean;
};

export type GamificacaoCompleteResponse = {
  ativacao_lead_id: number;
  gamificacao_id: number;
  gamificacao_completed: boolean;
  gamificacao_completed_at: string;
};

export async function completeGamificacao(
  ativacaoLeadId: number,
  payload: GamificacaoCompletePayload,
): Promise<GamificacaoCompleteResponse> {
  const res = await fetchWithAuth(
    `/ativacao-leads/${ativacaoLeadId}/gamificacao`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      retries: 0,
    },
  );
  return handleApiResponse<GamificacaoCompleteResponse>(res);
}
```

### 6.4 Interface do `GamificacaoBlock`

```typescript
type GamificacaoState = "presenting" | "active" | "completed";
// Sem "idle" — responsabilidade de não-montagem é do pai

type GamificacaoBlockProps = {
  gamificacoes: GamificacaoPublic[];   // length >= 1 garantido pelo pai
  leadSubmitted: boolean;             // habilita botões de interação
  onComplete: (gamificacaoId: number) => void;
  onReset: () => void;
};
```

---

## 07 · Mudanças em `LandingPageView.tsx`

### Remover

```tsx
// Chip mood — view pública
<Chip label={data.template.mood} ... />

// Chip esporte_radical condicional
{data.template.categoria === "esporte_radical" ? <Chip label="Radical" ... /> : null}

// Chip categoria — view pública (manter apenas dentro do bloco isPreview)
```

### Manter sem alteração

```tsx
renderGraphicOverlay(data)
buildLandingTheme(data)
getLayoutVisualSpec(data)
ThemeProvider
```

### Modificar

```tsx
// borderRadius — todos os Paper: de 6 para 3

// Título do formulário
<Typography variant="h5">
  {data.ativacao?.nome ?? data.template.cta_text}
</Typography>

// Callout de orientação — adicionar acima dos campos
{data.ativacao?.mensagem_qrcode ? (
  <Alert severity="info">{data.ativacao.mensagem_qrcode}</Alert>
) : null}

// Hero image — tornar condicional
{data.marca.url_hero_image ? (
  <Box component="img" src={data.marca.url_hero_image} ... />
) : (
  <Box sx={{ background: layout.heroBackground, minHeight: layout.imageMinHeight }} />
)}

// Logo BB — de texto para imagem
<Box component="img" src="/logo-bb.svg" alt="Banco do Brasil" ... />
```

### Adicionar

```tsx
const [leadSubmitted, setLeadSubmitted] = useState(false);
const [ativacaoLeadId, setAtivacaoLeadId] = useState<number | null>(null);

const handleSubmitSuccess = (response: LandingSubmitResponse) => {
  setSubmitted(response);
  setLeadSubmitted(true);
  setAtivacaoLeadId(response.ativacao_lead_id);
};

const handleGamificacaoComplete = async (gamificacaoId: number) => {
  if (!ativacaoLeadId) return;
  await completeGamificacao(ativacaoLeadId, {
    gamificacao_id: gamificacaoId,
    gamificacao_completed: true,
  });
};

// Bloco de gamificação — após conteúdo, antes do footer
{data.gamificacoes.length > 0 ? (
  <GamificacaoBlock
    gamificacoes={data.gamificacoes}
    leadSubmitted={leadSubmitted}
    onComplete={handleGamificacaoComplete}
    onReset={handleReset}
  />
) : null}
```

---

## 08 · Casos de Uso

### UC-01 — Ativação sem gamificação
1. Usuário acessa URL; formulário visível acima da dobra com título = `ativacao.nome`
2. Preenche campos, marca LGPD, clica CTA
3. Vê mensagem de sucesso
4. Nenhum bloco de gamificação na página

### UC-02 — Ativação com mensagem de orientação
1. Callout visível acima dos campos com texto de `mensagem_qrcode`
2. Fluxo de formulário normal

### UC-03 — Ativação com gamificação (fluxo completo)
1. Usuário acessa URL; formulário acima da dobra
2. Abaixo: card da gamificação com nome, descrição e prêmio; botão desabilitado com "Preencha o cadastro acima para participar"
3. Usuário preenche e submete o formulário → `ativacao_lead_id` recebido
4. Botão "Quero participar" é habilitado
5. Usuário clica → estado `ACTIVE`; instruções exibidas
6. Usuário realiza atividade no mundo físico
7. Clica "Concluí" → `POST /ativacao-leads/{id}/gamificacao` disparado → estado `COMPLETED`
8. Feedback exibido
9. "Nova pessoa" → reset completo

### UC-04 — Preview no backoffice
1. Chips `mood`, `categoria` e `tema` visíveis (modo `isPreview`)
2. Formulário desabilitado
3. Bloco de gamificação visível em somente-leitura (botões desabilitados)
4. Checklist mínimo de ativação exibido

---

## 09 · Critérios de Aceite

**LPD-REDESIGN-01 — Layout e visual:**
- [ ] Formulário visível sem scroll em 375px, 768px e 1280px
- [ ] `borderRadius` máximo nos cards = 24px
- [ ] Chips `mood` e `categoria` ausentes na view pública; presentes no modo `preview`
- [ ] `renderGraphicOverlay()` sem regressão visual entre templates
- [ ] Hero image renderizada condicionalmente
- [ ] Logo BB via imagem/SVG

**LPD-REDESIGN-02 — Dados da ativação:**
- [ ] Título usa `ativacao.nome` quando disponível
- [ ] Callout exibido quando `mensagem_qrcode` presente
- [ ] CTA resolve `evento.cta_personalizado` antes do default do template

**LPD-REDESIGN-03 — Fluxo de gamificação:**
- [ ] Bloco renderizado desde o carregamento quando `gamificacoes.length > 0`
- [ ] Botões desabilitados antes do submit, com orientação textual visível
- [ ] Botões habilitados após submit bem-sucedido
- [ ] Transições `PRESENTING → ACTIVE → COMPLETED` corretas
- [ ] `POST /ativacao-leads/{id}/gamificacao` disparado ao concluir
- [ ] Feedback exibido no estado `COMPLETED`
- [ ] Reset completo funcional

**LPD-REDESIGN-04 — Rastreabilidade backend:**
- [ ] Migration em `AtivacaoLead` com 3 novos campos (nullable, sem lock)
- [ ] `ativacao_lead_id` presente na response do submit
- [ ] `POST /ativacao-leads/{id}/gamificacao` persiste corretamente
- [ ] Consulta "leads que completaram gamificação X na ativação Y" possível

**LPD-REDESIGN-05 — Contrato de API:**
- [ ] Payload de landing inclui `ativacao` com `nome`, `descricao`, `mensagem_qrcode`
- [ ] `gamificacoes` sempre presente como array
- [ ] Nenhum campo removido de `template`
- [ ] Testes de contrato atualizados

---

## 10 · Dependências e Riscos

| Dependência | Impacto | Mitigação |
|---|---|---|
| Migration `AtivacaoLead` | Possível janela de manutenção | Todos nullable — sem lock |
| `ativacao_lead_id` na response do submit | Frontend depende desse ID | Definido no contrato 5.2 |
| `gamificacoes` como campo novo no payload | Dados cacheados podem não ter o campo | `data.gamificacoes ?? []` no consumer |
| Modelo 1:1 ativação-gamificação | Dropdown futuro requer schema change | Array no contrato antecipa sem breaking change |

---

## 11 · Fora de Escopo

- **Múltiplas gamificações por ativação** — requer mudança de schema (`gamificacao_id` FK → tabela associativa `ativacao_gamificacao`); dropdown de seleção depende disso; ambos são épico futuro
- Editor visual livre de templates
- Upload de imagem hero pela interface
- Notificações pós-cadastro
- Alteração de `LeadConversao`
- Preview em tempo real de customizações (EPIC-F3-03)

---

## 12 · Roadmap Sugerido

| Sprint | Issues | Entrega |
|---|---|---|
| Sprint 1 | LPD-REDESIGN-01 + LPD-REDESIGN-02 | Layout form-first, ajustes visuais, título/CTA da ativação |
| Sprint 2 | LPD-REDESIGN-04 + LPD-REDESIGN-05 | Migration + extensão de API backend |
| Sprint 3 | LPD-REDESIGN-03 | `GamificacaoBlock` + fluxo completo frontend |
| Sprint 4 | Regression + QA de marca | Validação visual, acessibilidade, checklist BB |

---

*Banco do Brasil · PRD Landing Redesign v1.2 · Confidencial Interno*
*Pra tudo que você imaginar.*
