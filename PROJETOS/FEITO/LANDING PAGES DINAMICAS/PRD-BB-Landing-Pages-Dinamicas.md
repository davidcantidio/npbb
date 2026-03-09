# PRD — Landing Pages Dinâmicas para Eventos
**Banco do Brasil · Plataforma NPBB — Módulo de Eventos & Leads**

| Campo | Valor |
|---|---|
| Produto | Landing Pages Dinâmicas — Eventos BB |
| Iniciativa | Plataforma NPBB — Módulo de Eventos & Leads |
| Versão | 1.0 — Draft |
| Data | Março 2026 |
| Status | Em revisão |
| Responsável | Produto / Design / Engenharia Frontend |

---

## Sumário Executivo

Este documento define os requisitos para o sistema de Landing Pages Dinâmicas de Eventos do Banco do Brasil. O objetivo é garantir que cada URL de captura de leads gerada pelo sistema NPBB exiba uma experiência visual adequada ao tipo de evento — respeitando integralmente as Diretrizes de Marca BB — ao mesmo tempo em que maximiza a conversão de visitantes em leads qualificados.

### Problema Central

- Todas as landing pages de eventos exibem o mesmo layout genérico, independente do contexto
- Eventos de skate, shows, exposições e reuniões corporativas competem pela mesma atenção visual
- A ausência de adaptação reduz a relevância percebida e prejudica a taxa de conversão
- A identidade de marca BB não é expressa em sua plenitude nos pontos de contato digitais de eventos

### Solução Proposta

- Sistema de templates visuais por categoria de evento, baseado nos territórios de marca BB
- Detecção automática do tipo de evento a partir dos metadados cadastrados no sistema
- Experiência visual coesa com a identidade BB, respeitando paleta, tipografia e grafismos oficiais
- Arquitetura extensível para novas categorias de eventos futuras

---

## 01 · Contexto e Motivação

### 1.1 Contexto do Negócio

O Banco do Brasil patrocina e organiza centenas de eventos anuais distribuídos em múltiplos territórios de marca — esportes, cultura, tecnologia e eventos corporativos. Para cada **ativação** (ponto de captação) dentro de um evento cadastrado no sistema NPBB, é gerada automaticamente uma URL única de captura de leads que pode ser distribuída em peças digitais, QR Codes e comunicações. O participante já está no evento; a landing serve para captar o lead naquele ponto de contato.

Atualmente, todas essas páginas utilizam um layout único e genérico, sem considerar a natureza, o público e o contexto emocional de cada tipo de evento. Isso contraria diretamente a diretriz de marca BB de ser **"incrivelmente humano"** e **"sempre relevante"**.

### 1.2 Alinhamento com a Plataforma de Marca BB

O Manual de Marca BB define quatro pilares de personalidade que devem ser expressos em todos os pontos de contato:

| Pilar de Personalidade BB | Expressão na Landing Page |
|---|---|
| Inteligentemente Simples | Interface clara, formulário direto, hierarquia visual limpa |
| Sempre Relevante | Visual adaptado ao contexto e tipo de evento cadastrado |
| Incrivelmente Humano | Fotografia real, linguagem próxima, conexão emocional |
| Super Encorajador | Tom de voz positivo, CTA motivador, celebração da conquista |

### 1.3 Territórios de Marca como Base de Segmentação

O manual de marca BB define três grandes territórios de patrocínio e conteúdo. Este PRD expande esses territórios para cobrir todos os tipos de evento que o sistema NPBB precisa suportar:

**Territórios mapeados no Manual BB:**
- 🏅 Esporte
- 🎭 Cultura
- 💻 Tecnologia

**Categorias NPBB derivadas:**
- Esporte Radical (Skate, Surfe, etc.)
- Esporte Convencional (Futebol, Atletismo, etc.)
- Show / Espetáculo Musical
- Exposição / Evento Cultural
- Corporativo / Institucional
- Tecnologia / Inovação
- Genérico *(fallback)*

---

## 02 · Objetivos e Métricas de Sucesso

### 2.1 Objetivos do Produto

1. Aumentar a taxa de conversão de visitantes em leads qualificados nas landing pages de eventos
2. Expressar a identidade BB de forma contextualmente relevante em cada tipo de evento
3. Reduzir o tempo de setup de nova landing page para zero (zero configuração manual de tema)
4. Criar arquitetura de templates extensível para novos tipos de eventos futuros
5. Garantir conformidade total com as Diretrizes de Marca Banco do Brasil

### 2.2 KPIs e Critérios de Sucesso

| Métrica | Meta |
|---|---|
| Taxa de Conversão (Lead/Visita) | > 15% por evento *(baseline atual a medir)* |
| Tempo de Carregamento — LCP | < 2.5s em 4G |
| First Input Delay (FID) | < 100ms |
| Taxa de Rejeição (Bounce Rate) | < 50% por categoria de evento |
| Aprovação em Audit de Marca | 100% dos templates aprovados pelo time de marca BB |
| Cobertura de Categorias | 100% dos eventos cadastrados recebem template adequado |
| Acessibilidade | WCAG 2.1 AA em todos os templates |

---

## 03 · Requisitos Funcionais

### 3.1 Sistema de Categorização de Eventos

O sistema deve derivar automaticamente a categoria visual da landing page a partir dos metadados do evento. A categorização ocorre em dois níveis.

#### 3.1.1 Campos de Entrada para Categorização

| Campo | Uso | Prioridade |
|---|---|---|
| `tipo_evento` | Enum cadastrado no sistema (Esporte, Cultura, Corporativo, etc.) | Primário |
| `subtipo_evento` | Campo livre ou enum derivado (Skate, Surfe, Show, Exposição) | Secundário |
| `nome_evento` | Análise de keywords como fallback complementar | Fallback |
| `diretoria_id` | Diretoria responsável pode sugerir template (ex: DIPES → Corporativo) | Auxiliar |

#### 3.1.2 Mapeamento de Categoria para Template Visual

| Categoria Interna | Exemplos de Evento | Tema | Direcionamento Visual |
|---|---|---|---|
| `esporte_radical` | Skate, Surfe, BMX, Escalada | Radical | Rosa/Amarelo vibrante + grafismos dinâmicos |
| `esporte_convencional` | Futebol, Atletismo, Natação, Vôlei | Sport | Azul escuro + Amarelo + energia alta |
| `show_musical` | Show, Concerto, Festival, Música | Show | Roxo + Rosa + atmosfera noturna |
| `evento_cultural` | Exposição, Teatro, CCBB, Dança, Cinema | Cultural | Roxo claro + Verde + elegância |
| `corporativo` | Congresso, Summit, Treinamento, Reunião | Corp | Azul escuro + Amarelo + sobriedade |
| `tecnologia` | Hackathon, Startup, Demo Day, Tech | Tech | Azul claro + Verde + modernidade |
| `generico` | Qualquer evento não categorizado | Default | Paleta principal BB + layout neutro |

### 3.2 Estrutura de Página — Componentes Obrigatórios

Todos os templates devem conter os seguintes blocos funcionais, independente do tema visual:

| Componente | Descrição |
|---|---|
| Hero Section | Identidade imediata do evento: nome, data, local, imagem temática, CTA principal |
| Formulário de Lead | Campos configuráveis por evento: nome, e-mail, CPF, telefone, opcionais |
| Sobre o Evento | Descrição, programação resumida e diferenciais do evento |
| Logo e Assinatura BB | Logotipo BB sempre presente, respeitando área de proteção e versões permitidas |
| Footer | Links de política de privacidade, contato e LGPD |
| Confirmação de Lead | Tela pós-envio com mensagem de tom BB (escala de serotonina: Entusiasmo) |

### 3.3 Formulário de Leads — Comportamento

- Campos obrigatórios padrão: Nome, E-mail
- Campos opcionais configuráveis por evento: CPF, Telefone, Cargo, Empresa, Estado
- Validação em tempo real com feedback visual positivo (tom encorajador)
- Integração direta com a API existente: `POST /leads/import`
- Associação automática ao evento e à ativação via parâmetro na URL (`event_id`, `ativacao_id`)
- Mensagem de sucesso personalizada por categoria de evento
- Prevenção de submissão duplicada por e-mail (deduplicação no frontend)

---

## 04 · Especificação Visual por Template

Esta seção define os parâmetros visuais de cada template, com base nas Diretrizes de Marca BB.

> **Elementos Invariáveis — todos os templates:**
> - Logotipo BB e grafema: sempre presentes, em versões homologadas
> - Tipografia: fonte proprietária BB ou substituta aprovada
> - Tagline: *"Banco do Brasil. Pra tudo que você imaginar."* em posição de destaque
> - Tom de voz: escala de serotonina BB (Atenção → Simpatia → Entusiasmo conforme contexto)
> - Acessibilidade: contraste mínimo WCAG AA em todos os elementos de texto

---

### 4.1 Template: Esporte Radical (Skate, Surfe)

| Parâmetro | Valor |
|---|---|
| Cores Dominantes | `#FF6E91` Rosa Escuro · `#FCFC30` Amarelo · `#3333BD` Azul Escuro |
| Cores de Acento | `#FFA7D3` Rosa Claro · `#83FFEA` Verde Claro |
| Mood Visual | Alta energia, movimento, autenticidade, atitude |
| Grafismos | Formas dinâmicas anguladas, elementos em movimento, splash |
| Fotografia | Atleta em ação, perspectiva dramática, luz natural intensa |
| Tom de Voz | Entusiasmo máximo — celebrar o desempenho e a comunidade |
| CTA Principal | "Quero fazer parte" / "Inscreva-se agora" |
| Layout Hero | Imagem full-bleed, texto sobreposto com sombra, badge de modalidade |

---

### 4.2 Template: Esporte Convencional

| Parâmetro | Valor |
|---|---|
| Cores Dominantes | `#3333BD` Azul Escuro · `#FCFC30` Amarelo · `#FFFFFF` Branco |
| Cores de Acento | `#54DCFC` Azul Claro · `#465EFF` Azul |
| Mood Visual | Orgulho, conquista, vibração, green-and-yellow spirit |
| Grafismos | Formas geométricas sólidas, bandeiras, elementos olímpicos |
| Fotografia | Atleta em momento de vitória, torcida, verde e amarelo em destaque |
| Tom de Voz | Entusiasmo + orgulho nacional — torcer junto, maximizar conquistas |
| CTA Principal | "Torça com a gente" / "Garanta sua vaga" |
| Layout Hero | Split layout: imagem esquerda, formulário direita, header azul |

---

### 4.3 Template: Show / Espetáculo Musical

| Parâmetro | Valor |
|---|---|
| Cores Dominantes | `#735CC6` Roxo Escuro · `#FF6E91` Rosa · `#FCFC30` Amarelo |
| Cores de Acento | `#BDB6FF` Roxo Claro · `#FFA7D3` Rosa Claro |
| Mood Visual | Noturno, vibrante, experiência única, glamour acessível |
| Grafismos | Formas fluidas, brilhos, elementos sonoros abstratos, luzes de palco |
| Fotografia | Palco com iluminação, público emocionado, artista em performance |
| Tom de Voz | Simpatia + Entusiasmo — a emoção de estar presente |
| CTA Principal | "Quero ir" / "Garanta seu ingresso" |
| Layout Hero | Background dark com gradiente roxo, overlay de partículas, destaque no título |

---

### 4.4 Template: Evento Cultural (Exposição, Teatro, CCBB)

| Parâmetro | Valor |
|---|---|
| Cores Dominantes | `#BDB6FF` Roxo Claro · `#00EBD0` Verde Escuro · `#FFFFFF` Branco |
| Cores de Acento | `#FCFC30` Amarelo · `#83FFEA` Verde Claro |
| Mood Visual | Sofisticação acessível, curiosidade, enriquecimento cultural |
| Grafismos | Formas orgânicas suaves, elementos tipográficos como arte, texturas |
| Fotografia | Obra de arte, espaço cultural, pessoas contemplando e interagindo |
| Tom de Voz | Atenção + Simpatia — convidar à experiência, democratizar a cultura |
| CTA Principal | "Quero conhecer" / "Reserve sua visita" |
| Layout Hero | Layout editorial, tipografia grande como elemento visual, paleta clara |

---

### 4.5 Template: Corporativo / Institucional

| Parâmetro | Valor |
|---|---|
| Cores Dominantes | `#3333BD` Azul Escuro · `#FFFFFF` Branco · `#FCFC30` Amarelo |
| Cores de Acento | `#465EFF` Azul · `#F5F5F5` Cinza Claro |
| Mood Visual | Profissionalismo, confiança, clareza, relevância estratégica |
| Grafismos | Linhas retas, grid modular, ícones funcionais |
| Fotografia | Profissionais em contexto de trabalho, ambientes corporativos modernos |
| Tom de Voz | Atenção + Simpatia — informativo, direto, confiável |
| CTA Principal | "Confirmar presença" / "Fazer inscrição" |
| Layout Hero | Header azul com logotipo, título sobreposto, formulário em card branco |

---

### 4.6 Template: Tecnologia / Inovação

| Parâmetro | Valor |
|---|---|
| Cores Dominantes | `#54DCFC` Azul Claro · `#83FFEA` Verde Claro · `#3333BD` Azul Escuro |
| Cores de Acento | `#FCFC30` Amarelo · `#465EFF` Azul Médio |
| Mood Visual | Inovação, futuro, comunidade tech, otimismo tecnológico |
| Grafismos | Grid de pontos, linhas de código abstratas, hexágonos, circuitos |
| Fotografia | Pessoas diversas em ambiente tech, telas de código, eventos de inovação |
| Tom de Voz | Entusiasmo + Simpatia — empoderar, capacitar, inspirar |
| CTA Principal | "Quero participar" / "Me inscreva no hackathon" |
| Layout Hero | Background escuro com gradiente azul-verde, efeito de código em fundo |

---

### 4.7 Template: Genérico (Fallback)

| Parâmetro | Valor |
|---|---|
| Cores Dominantes | `#3333BD` Azul Escuro · `#FCFC30` Amarelo · `#FFFFFF` Branco |
| Mood Visual | Neutro, confiável, identidade BB pura |
| Grafismos | Grafema BB em destaque, formas geométricas básicas da marca |
| Tom de Voz | Simpatia — acolhedor, claro, direto |
| CTA Principal | "Quero participar" / "Faça sua inscrição" |
| Layout Hero | Header azul padrão BB, formulário centralizado, tagline em destaque |

---

## 05 · Arquitetura Técnica

### 5.0 Modelo de Dados — Relação Landing ↔ Ativação

**Conceito central:** A landing page de captação é uma **ação de ativação** dentro do evento. O participante já está presente no evento; a landing serve para captar o lead naquele ponto de contato (stand, totem, promotor).

| Entidade | Relação | Descrição |
|---|---|---|
| **Evento** | 1:N | Um evento possui várias ativações (stands, pontos de captação) |
| **Ativação** | N:1 | Cada ativação pertence a um evento |
| **Landing** | 1:1 com Ativação | Cada ativação possui uma URL única de landing (ou compartilha a do evento) |
| **Lead** | via AtivacaoLead | Lead captado é associado à ativação via `ativacao_lead` |

**URLs de acesso:**
- Por ativação (preferencial): `/landing/ativacoes/{ativacao_id}` — cada ponto de captação tem sua URL e QR code
- Por evento (fallback): `/landing/eventos/{evento_id}` — quando não há ativação específica ou para compatibilidade

**QR Code e acesso via Promotor:**
- Cada ativação deve ter QR code gerado apontando para sua URL de landing
- Alternativa para quem não consegue ler QR: promotor digita/compartilha a URL curta ou o link "landing-sem-qr" equivalente
- O sistema deve prever geração de QR codes e URL alternativa de acesso (via promotor)

### 5.1 Fluxo de Resolução de Template

O sistema deve seguir o seguinte fluxo de decisão para determinar qual template exibir, em ordem de prioridade:

```
1. Campo `template_override` no evento       → usar diretamente se definido
2. Campo `subtipo_evento`                    → mapear via tabela de categorias
3. Campo `tipo_evento`                       → mapear para categoria base
4. Keywords no `nome_evento`                 → inferir categoria por NLP simples
5. Fallback                                  → template `generico`
```

### 5.2 Contrato de API

| Endpoint | Descrição |
|---|---|
| `GET /ativacoes/{id}/landing` | Retorna dados da ativação + evento + configuração do template *(preferencial)* |
| `GET /eventos/{id}/landing` | Retorna dados do evento + configuração do template *(fallback/compatibilidade)* |
| `POST /leads/` | Submissão de lead associado ao evento e à ativação *(existente, estender com ativacao_id)* |
| `GET /ativacoes/{id}/template-config` | Retorna configuração visual do template *(novo)* |
| `GET /ativacoes/{id}/qr-code` | Gera ou retorna QR code da landing da ativação *(novo)* |

**Payload de resposta — `GET /ativacoes/{id}/landing` (e fallback `/eventos/{id}/landing`):**

```json
{
  "ativacao_id": 10,
  "evento": {
    "id": 123,
    "nome": "BB Skate Open 2026",
    "descricao": "...",
    "data_inicio": "2026-04-10",
    "data_fim": "2026-04-12",
    "cidade": "São Paulo",
    "estado": "SP"
  },
  "template": {
    "categoria": "esporte_radical",
    "tema": "Radical",
    "cor_primaria": "#FF6E91",
    "cor_secundaria": "#FCFC30",
    "mood": "Alta energia, movimento, autenticidade",
    "cta_text": "Quero fazer parte"
  },
  "formulario": {
    "campos_obrigatorios": ["nome", "email"],
    "campos_opcionais": ["cpf", "telefone", "estado"],
    "mensagem_sucesso": "Você está dentro! A gente se vê na pista. 🛹"
  },
  "marca": {
    "tagline": "Banco do Brasil. Pra tudo que você imaginar.",
    "versao_logo": "negativo",
    "url_hero_image": "https://..."
  }
}
```

### 5.3 Extensões do Modelo de Dados

**Evento** (campos para categorização e template):

| Campo | Tipo | Descrição |
|---|---|---|
| `tipo_evento` | `VARCHAR(50)` | Enum: Esporte, Cultura, Corporativo, Tecnologia, Show, Outro |
| `subtipo_evento` | `VARCHAR(100)` | Texto livre: Skate, Surfe, Show Musical, Exposição, etc. |
| `template_override` | `VARCHAR(50)` | Nullable — permite forçar um template específico |
| `hero_image_url` | `TEXT` | URL da imagem principal da landing page |
| `cta_personalizado` | `VARCHAR(200)` | Texto do botão de CTA (fallback para padrão do template) |
| `descricao_curta` | `VARCHAR(500)` | Texto para o bloco "Sobre o Evento" |

**Ativação** (campos para landing e acesso):

| Campo | Tipo | Descrição |
|---|---|---|
| `landing_url` | `VARCHAR(500)` | URL pública da landing desta ativação (gerada automaticamente) |
| `qr_code_url` | `TEXT` | URL da imagem do QR code gerado (aponta para `landing_url`) |
| `url_promotor` | `VARCHAR(500)` | URL curta ou alternativa para acesso via promotor (quem não lê QR) |

### 5.4 Arquitetura de Componentes React

```
EventLandingPage          → Orquestrador principal; busca dados e seleciona template
├── ThemeProvider         → Injeta tokens visuais do template via context
├── HeroSection           → Imagem + título + CTA, adaptável por tema
├── LeadForm              → Formulário de captura, campos configuráveis
├── EventDetails          → Descrição, data, local e programação
├── BrandFooter           → Logo BB, tagline e links LGPD (invariável)
└── SuccessScreen         → Tela pós-envio com mensagem por categoria
```

### 5.5 Sistema de Tokens de Tema

Cada template é definido por um objeto de tokens que sobrescreve o tema base BB:

| Token | Descrição |
|---|---|
| `colorPrimary` | Cor principal do hero e elementos de destaque |
| `colorSecondary` | Cor dos CTAs, bordas e acentos |
| `colorBackground` | Cor de fundo geral da página |
| `colorText` | Cor do texto principal |
| `heroLayout` | `"full-bleed"` · `"split"` · `"editorial"` · `"dark-overlay"` |
| `ctaVariant` | `"filled"` · `"outlined"` · `"gradient"` |
| `graphicsStyle` | `"dynamic"` · `"geometric"` · `"organic"` · `"grid"` |
| `toneOfVoice` | `"attention"` · `"warmth"` · `"enthusiasm"` *(escala de serotonina BB)* |
| `ctaDefaultText` | Texto padrão do botão de ação principal |

---

## 06 · Requisitos Não-Funcionais

### 6.1 Performance

- LCP (Largest Contentful Paint) < 2.5s em conexão 4G
- FID (First Input Delay) < 100ms
- CLS (Cumulative Layout Shift) < 0.1
- Imagens de hero servidas em WebP com lazy-loading e srcset responsivo
- Bundle da landing page separado do bundle principal (code splitting)
- SSR ou SSG para URLs de landing page (melhora SEO e performance inicial)

### 6.2 Responsividade

- Design mobile-first: breakpoints em 375px, 768px e 1280px
- Formulário ocupa 100% da largura em mobile
- Hero section: mínimo 320px de altura em mobile, 80vh em desktop
- Touch targets mínimos de 44×44px em todos os elementos interativos

### 6.3 Acessibilidade

- Conformidade WCAG 2.1 AA
- Contraste de texto: mínimo 4.5:1 para texto normal, 3:1 para texto grande
- Todos os campos de formulário com labels visíveis e `aria-label`
- Imagens com `alt` text descritivo
- Navegação por teclado funcional em todo o formulário
- Suporte a leitores de tela (VoiceOver, NVDA)

### 6.4 Segurança e LGPD

- Exibir texto de consentimento LGPD antes da submissão
- Checkbox de aceite obrigatório com link para Política de Privacidade BB
- Dados transmitidos apenas via HTTPS
- Não armazenar CPF ou telefone em `localStorage` / `sessionStorage`
- Token de evento na URL não deve expor informações sensíveis do sistema

---

## 07 · Checklist de Conformidade com Diretrizes de Marca BB

Deve ser validado por template antes do deploy em produção:

| Item | Criticidade |
|---|---|
| Logotipo BB presente e em versão correta por contexto de cor de fundo | ⛔ Obrigatório |
| Grafema BB garante associação à marca (forma preservada) | ⛔ Obrigatório |
| Amarelo BB `#FCFC30` presente como elemento de identidade | ⛔ Obrigatório |
| Tagline *"Banco do Brasil. Pra tudo que você imaginar."* visível | ⛔ Obrigatório |
| Paleta de cores restrita às cores oficiais do manual | ⛔ Obrigatório |
| Tipografia respeita hierarquia visual definida no manual | ⛔ Obrigatório |
| Tom de voz alinhado à escala de serotonina adequada ao contexto | ⛔ Obrigatório |
| Contraste WCAG AA validado para todas as combinações de cor | ⛔ Obrigatório |
| Layout não conflita com área de proteção do logotipo BB | ⛔ Obrigatório |
| CTA em português, positivo e encorajador | ⛔ Obrigatório |
| Fotografia com pessoas brasileiras reais (não stock genérico) | ⚠️ Recomendado |
| Grafismos do território de marca utilizados corretamente | ⚠️ Recomendado |

---

## 08 · Roadmap e Fases de Entrega

### Fase 1 — Fundação *(Semanas 1–3)*

- Definição do contrato de API e extensão do modelo de dados (Evento + Ativação)
- **Vinculação landing ↔ ativação:** endpoints por ativação, lead associado via AtivacaoLead
- Implementação do engine de resolução de template (lógica de categorização)
- Template **Genérico** (fallback) completo e aprovado pela equipe de marca
- Template **Corporativo** completo (cobertura dos eventos internos BB)
- **Geração de QR codes:** serviço que gera imagem QR apontando para URL da landing da ativação
- **Acesso via Promotor:** URL alternativa (curta ou "landing-sem-qr") para participantes que não conseguem ler QR — promotor digita/compartilha o link
- Testes de acessibilidade e performance no template base

### Fase 2 — Templates de Alto Volume *(Semanas 4–6)*

- Template **Esporte Convencional** — maior volume de eventos patrocinados
- Template **Evento Cultural / CCBB** — territórios Cultura e CCBB
- Template **Tecnologia / Inovação** — eventos de tech e startups
- Painel de preview de template no backoffice NPBB
- Documentação de uso para equipes de marketing de eventos

### Fase 3 — Templates Especializados e Extensibilidade *(Semanas 7–9)*

- Template **Esporte Radical** (Skate, Surfe, Modalidades em ascensão)
- Template **Show / Espetáculo Musical**
- Interface de criação de template customizado no backoffice
- Analytics de conversão por template (integração com GA4)
- Testes A/B entre variações de CTA por categoria

---

## 09 · Critérios de Aceite (Definition of Done)

### Por Template

1. Renderiza corretamente nos breakpoints 375px, 768px e 1280px
2. Formulário de leads submete e cria lead vinculado ao evento correto
3. Tela de sucesso exibe mensagem personalizada para a categoria
4. Aprovação visual do time de marca BB (checklist da seção 07 aprovado)
5. LCP < 2.5s medido no Lighthouse em condição 4G simulado
6. Score de acessibilidade ≥ 90 no Lighthouse
7. Contraste WCAG AA validado para todas as combinações de texto/fundo
8. Nenhum erro no console em modo produção

### Para o Sistema de Categorização

1. 100% dos `tipos_evento` cadastrados mapeiam para um template (sem fallback inesperado)
2. Engine de resolução cobre os 5 fluxos de prioridade especificados na seção 5.1
3. Testes unitários cobrem > 80% do código do engine de resolução
4. Novo tipo de evento pode ser adicionado sem modificar código existente

---

## 10 · Referências e Documentos Relacionados

| Documento | Referência |
|---|---|
| Manual de Marca BB | `Diretrizes-de-Marca-Banco-do-Brasil.pdf` (versão vigente) |
| Brandzone BB | Intranet Institucional / Marca |
| API Backend NPBB | Documentação FastAPI — `/docs` (Swagger interno) |
| Sistema de Eventos | Frontend NPBB — módulo `/eventos` (repositório `npbb-frontend`) |
| WCAG 2.1 AA | https://www.w3.org/TR/WCAG21/ |
| Política de Privacidade BB | Portal Banco do Brasil — Privacidade e LGPD |

---

*Banco do Brasil · PRD Landing Pages Dinâmicas v1.0 · Confidencial Interno*
*Pra tudo que você imaginar.*
