---
doc_id: "INTAKE-UX.md"
version: "1.0"
status: "draft"
owner: "PM"
projeto: "UX"
intake_kind: "refactor"
source_mode: "original"
origin_audit: "nao_aplicavel"
product_type: "platform-capability"
delivery_surface: "frontend-web"
business_domain: "landing-pages, leads, eventos"
criticality: "media"
data_sensitivity: "interna"
change_type: "refactor"
audit_rigor: "standard"
integrations: []
last_updated: "2026-03-13"
supersedes: "INTAKE-LP-PREVIEW.md"
---

# INTAKE-UX

## 1. Problema ou Oportunidade

O wizard de configuração de evento (5 etapas: Evento, Landing Page,
Gamificação, Ativações, Questionário) apresenta múltiplos problemas de
diagramação e densidade visual que prejudicam a experiência do operador:

- Campos de formulário com largura excessiva ocupando toda a área útil
- Preview da landing posicionado de forma fragmentada, sem coluna fixa
- Dropdown de "Tema" duplicado — dois seletores com propósitos sobrepostos
- Box informativo azul redundante com as próprias opções do seletor
- Seção "Governança e performance" desnecessária para o fluxo de
  configuração principal
- Texto descritivo acima do preview sem valor operacional
- Lista de campos possíveis em 2 colunas com indicação de ordem por texto,
  sem suporte a reordenação por arrastar
- Campos adicionais visíveis por padrão, gerando densidade desnecessária
- Ausência de padrão visual consistente entre as etapas do wizard
- Fontes e espaçamentos fora do padrão, resultando em falta de harmonia

Este intake evolui e absorve o INTAKE-LP-PREVIEW.md, cuja proposta de
preview vertical à direita é subconjunto deste escopo mais amplo.

## 2. Público ou Operador Principal

Operador interno do NPBB responsável pela criação e configuração de
eventos, formulários de leads, gamificações e ativações.

## 3. Job to Be Done Dominante

Enquanto configuro as etapas do meu evento, quero uma interface limpa,
organizada em duas colunas (configuração à esquerda, contexto à direita),
com boa respiro visual e sem informações redundantes, para que eu consiga
configurar com eficiência e confiança sem distrações ou ruído visual.

## 4. Fluxo Principal Esperado

1. Operador acessa qualquer etapa do wizard de configuração de evento.
2. A tela está dividida em duas colunas fixas:
   - **Coluna esquerda:** painel de configuração da etapa atual
   - **Coluna direita:** conteúdo contextual da etapa (preview mobile
     ou lista de itens configurados)
3. Na etapa **Landing Page:**
   - Coluna esquerda: seletor de template único (campo "Contexto da
     landing"), CTA personalizado, Descrição curta e seleção de campos
   - Coluna direita: preview da landing em frame mobile (≈390 px,
     padrão dominante 2026), sem texto descritivo acima
   - Campos possíveis exibidos em 1 coluna; CPF, Nome, Sobrenome e
     Data de nascimento pré-selecionados e visíveis por padrão
     (CPF não pode ser desmarcado); demais campos acessíveis via
     botão "+"; ordem definida por drag-and-drop
4. Na etapa **Gamificação:**
   - Coluna esquerda: formulário de configuração de gamificação
   - Coluna direita: lista das gamificações criadas (comportamento
     atual mantido)
5. Na etapa **Ativações:**
   - Coluna esquerda: formulário de configuração de ativação
   - Coluna direita: preview da página de ativação como o usuário
     final a vê, em frame mobile
6. Nas demais etapas (Evento, Questionário):
   - Padrão de duas colunas aplicado; coluna direita com conteúdo
     contextual relevante à etapa
   - Mesma linguagem visual: respiro, fontes, espaçamentos

## 5. Objetivo de Negócio e Métricas de Sucesso

**Objetivo:** Elevar a qualidade da experiência de configuração do
operador, reduzindo ruído visual, redundâncias e fricção no fluxo,
e estabelecer um padrão visual consistente para todas as etapas do
wizard.

**Métricas:**
- Nenhuma regressão funcional nas 5 etapas do wizard
- Eliminação de 100% dos elementos listados como removidos no escopo
- Validação interna pelo PM de que a interface atende aos critérios
  de limpeza e harmonia visual antes do deploy
- [hipótese: redução de dúvidas operacionais sobre função dos
  controles, observável em próximas sessões de uso]

## 6. Restrições e Não-Objetivos

**Restrições:**
- Nenhuma alteração de contrato de API ou modelo de dados
- CPF deve permanecer como campo obrigatório e não desmarcável
- A reatividade do preview (atualização em tempo real ao editar
  campos) deve ser mantida sem regressão
- O padrão de duas colunas deve ser aplicado de forma responsiva:
  definir comportamento em viewports menores
  [hipótese: colapso para coluna única abaixo de breakpoint a definir]
- Nenhuma nova dependência de biblioteca externa sem aprovação prévia

**Não-objetivos:**
- Não é objetivo desta iniciativa adicionar novas funcionalidades
  de configuração (novos campos, novos tipos de gamificação, etc.)
- Não é objetivo redesenhar o sistema de design global da plataforma
- Não é objetivo alterar o comportamento de publicação ou salvamento
- Não é objetivo implementar preview interativo (o preview permanece
  somente-leitura com interações desabilitadas)

## 7. Dependências e Integrações

- Componentes de preview de landing page e de ativação
  [hipótese: podem ser o mesmo componente ou variantes — nomes
  exatos desconhecidos; levantamento necessário em discovery técnico]
- Sistema de layout do wizard (estrutura de páginas das 5 etapas)
- Componente de seleção de campos possíveis
- Componente de drag-and-drop para reordenação (pode requerer
  introdução de biblioteca como dnd-kit ou similar)
  [hipótese: ainda não existe no codebase — verificar]

## 8. Arquitetura ou Superfícies Impactadas

- Camada de UI (frontend-web) exclusivamente
- Todas as 5 páginas do wizard: Evento, Landing Page,
  Gamificação, Ativações, Questionário
- Componentes de preview (landing e ativação)
- Componente de campos possíveis (layout, drag-and-drop, visibilidade
  progressiva via botão "+")
- Sistema de grid/layout do wizard (migração para duas colunas fixas)

## 9. Riscos Relevantes

- Componente de preview pode ter acoplamento com o posicionamento
  atual, exigindo refatoração além do layout
- Introdução de drag-and-drop pode trazer nova dependência de
  biblioteca — avaliar impacto no bundle
- Layout de duas colunas pode colapsar de forma inesperada em
  resoluções intermediárias (tablets, laptops pequenos)
- Aplicar o padrão a 5 etapas aumenta a superfície de regressão;
  testes manuais por etapa são necessários antes do deploy
- A remoção do seletor de "Tema" redundante requer confirmação de
  que o seletor remanescente ("Contexto da landing") cobre 100%
  dos valores e comportamentos do removido

## 10. Lacunas Conhecidas

- Nomes exatos dos componentes de preview no codebase: `nao_definido`
- Estrutura atual de layout do wizard (CSS Grid / Flexbox / outro):
  `nao_definido`
- Biblioteca de drag-and-drop disponível ou a adotar: `nao_definido`
- Breakpoint de colapso para coluna única: `nao_definido`
- Conteúdo da coluna direita nas etapas Evento e Questionário:
  `nao_definido` — definir em discovery antes do PRD
- Confirmação de que o seletor "Contexto da landing" cobre todos
  os valores do dropdown "Tema" removido: `nao_definido`

## 11. Rastreabilidade de Origem

Demanda originada diretamente pelo PM em sessão de intake, com base
em análise visual da interface atual documentada por screenshots
(Captura_de_Tela_2026-03-13, imagens 1–4).

Evolui e absorve: `INTAKE-LP-PREVIEW.md` (preview vertical mobile-first),
cujo escopo está integralmente contido neste intake.

---

## 12. Contexto Específico de Refactor

**Sintoma observado:**
Interface do wizard com múltiplas camadas de ruído visual: campos
excessivamente largos, elementos redundantes (dropdown duplicado,
box informativo, texto descritivo sem valor), preview fragmentado
sem coluna fixa, lista de campos em 2 colunas com reordenação
apenas textual, densidade desproporcional e inconsistência visual
entre etapas.

**Impacto operacional:**
Operador enfrenta fricção desnecessária em cada etapa do wizard:
precisa ignorar informações redundantes, não consegue correlacionar
configuração com resultado visual sem scroll, e não pode reordenar
campos de forma intuitiva. A inconsistência entre etapas aumenta
a carga cognitiva e reduz a confiança na configuração.

**Evidência técnica:**
Screenshots da interface atual fornecidos pelo PM em sessão de
intake (2026-03-13), cobrindo as etapas Landing Page,
Gamificação e Ativações. Problemas identificados diretamente
na interface em produção local (localhost).

**Componente(s) afetado(s):**
- Páginas das 5 etapas do wizard
- Componente de preview de landing (nome exato: `nao_definido`)
- Componente de preview de ativação (nome exato: `nao_definido`)
- Componente de seleção/reordenação de campos possíveis
- Sistema de layout/grid do wizard

**Riscos de não agir:**
A inconsistência visual e a densidade de informação continuarão
gerando fricção operacional crescente à medida que novas
funcionalidades forem adicionadas ao wizard. O padrão atual,
se não corrigido agora, tende a ser replicado em novas etapas,
aumentando o custo de refatoração futura.
```

---
```
─────────────────────────────────────────
Campos preenchidos: 12/12 seções cobertas
Hipóteses declaradas: 5
Campos nao_definido: 6 (todos de discovery técnico — não bloqueiam
                        escopo, restrições ou objetivo)

CHECKLIST DE PRONTIDÃO PARA PRD
[x] Por que isso existe
[x] Para quem existe
[x] O que entra e o que não entra
[x] Onde a mudança toca na arquitetura
[x] Como o sucesso será medido
[x] Quais restrições e riscos são incontornáveis
[x] O que ainda está em aberto (lacunas conhecidas declaradas)
[x] Origem auditável (intake original + screenshots do PM)
[x] Sintoma observado (refactor)
[x] Impacto operacional (refactor)
[x] Evidência técnica (refactor)
[x] Componente(s) afetado(s) (refactor — parcialmente nao_definido,
    não bloqueia PRD)
[x] Riscos de não agir (refactor)

Prontidão para PRD: pronto
─────────────────────────────────────────
→ "aprovar" para gerar o arquivo
→ "ajustar [instrução]" para revisar antes de gravar
→ "bloqueado" se quiser registrar como incompleto e parar aqui