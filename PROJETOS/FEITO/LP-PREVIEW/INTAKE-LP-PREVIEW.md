---
doc_id: "INTAKE-LP-PREVIEW.md"
version: "1.0"
status: "draft"
owner: "PM"
projeto: "LP-PREVIEW"
intake_kind: "refactor"
source_mode: "original"
origin_audit: "nao_aplicavel"
product_type: "platform-capability"
delivery_surface: "frontend-web"
business_domain: "landing-pages, leads"
criticality: "baixa"
data_sensitivity: "interna"
change_type: "refactor"
audit_rigor: "standard"
integrations: []
last_updated: "2026-03-13"
---

# INTAKE-LP-PREVIEW

## 1. Problema ou Oportunidade

O preview presente na página de configuração de formulário de leads e de
landing page ocupa hoje uma faixa horizontal da tela, posicionada entre
blocos de elementos do formulário. Esse layout fragmenta o fluxo de
configuração, obriga o operador a rolar a página para correlacionar
campo-a-campo com o resultado visual, e não representa a experiência real
do usuário final, que acessa as landing pages predominantemente via
dispositivo móvel.

## 2. Público ou Operador Principal

Operador interno do NPBB responsável pela criação e configuração de
formulários de leads e landing pages.

## 3. Job to Be Done Dominante

Enquanto configuro um formulário ou landing page, quero ver o resultado
visual em tempo real numa simulação fiel ao dispositivo móvel, posicionada
permanentemente ao lado do meu formulário de configuração, para que eu
possa tomar decisões de layout sem alternar contexto ou rolar a tela.

## 4. Fluxo Principal Esperado

1. Operador acessa a página de configuração de formulário de leads
   ou de landing page.
2. O painel de configuração ocupa a porção esquerda da tela.
3. O preview ocupa a porção direita da tela, fixo e visível durante
   toda a sessão de configuração, sem necessidade de scroll.
4. O preview renderiza o conteúdo em viewport de dispositivo móvel
   (largura-alvo: ~390 px, referência iPhone 16 / padrão dominante
   em 2026), com frame visual de celular.
5. A cada alteração no painel esquerdo, o preview atualiza em tempo real
   (comportamento de reatividade mantido — sem regressão).

## 5. Objetivo de Negócio e Métricas de Sucesso

**Objetivo:** Aumentar a eficiência e a confiança do operador no momento
de configurar formulários e landing pages, reduzindo erros de layout
detectados apenas em produção.

**Métricas:**
- Eliminação de reclamações sobre preview não representativo
  (qualitativa, próximas sessões de uso interno)
- Nenhuma regressão de funcionalidade nos dois contextos (zero bugs
  reportados pós-deploy relacionados ao preview)
- [hipótese: redução de iterações de reconfiguração pós-publicação]

## 6. Restrições e Não-Objetivos

**Restrições:**
- O preview não pode introduzir nova dependência de biblioteca externa
  sem aprovação prévia
- A reatividade existente (atualização ao editar campos) deve ser mantida
- Compatibilidade com os dois contextos (leads e landing page)
  obrigatória na mesma entrega

**Não-objetivos:**
- Não é objetivo desta iniciativa alterar a lógica de configuração
  dos formulários em si
- Não é objetivo adicionar funcionalidades ao preview
  (zoom, troca de dispositivo, modo desktop) nesta fase
- Não é objetivo alterar o contrato de API ou modelos de dados

## 7. Dependências e Integrações

- Componente(s) de preview existente(s) na página de configuração de
  leads e na página de configuração de landing page
  [hipótese: podem ser o mesmo componente ou variantes — nome exato
  desconhecido; levantamento necessário na fase de discovery técnico]
- Sistema de layout da página de configuração (grid/flex atual)

## 8. Arquitetura ou Superfícies Impactadas

- Camada de UI (frontend-web) exclusivamente
- Página de configuração de formulário de leads
- Página de configuração de landing page
- Componente de preview em ambas as páginas
- [hipótese: layout global da página pode requerer conversão para
  layout de duas colunas (ex: CSS Grid ou Flexbox row)]

## 9. Riscos Relevantes

- Componente de preview pode não ser isolado, dificultando o
  reposicionamento sem efeitos colaterais
- Layout de duas colunas pode colapsar em viewports menores
  (desktop com resolução baixa ou tablets) — necessita tratamento
  de breakpoint
- Reatividade pode ter acoplamento com o posicionamento atual e
  precisar de ajuste

## 10. Lacunas Conhecidas

- Nome exato do(s) componente(s) de preview no codebase: `nao_definido`
- Estrutura atual de layout da página (CSS Grid / Flexbox / outro): `nao_definido`
- Se o componente de preview é compartilhado entre os dois contextos
  ou são instâncias distintas: `nao_definido`
- Largura-alvo final do frame mobile (390 px proposto como hipótese,
  sujeito a validação com design)

## 11. Rastreabilidade de Origem

Demanda originada diretamente pelo PM em sessão de intake.
Nenhum artefato de auditoria prévio vinculado.

---

## 12. Contexto Específico de Refactor

**Sintoma observado:**
Preview disposto horizontalmente em faixa, intercalado entre blocos
do formulário de configuração, fragmentando o fluxo de trabalho do
operador e não representando a experiência real do usuário final
(mobile).

**Impacto operacional:**
Operador precisa rolar a tela para correlacionar configuração com
resultado visual; preview não simula dispositivo móvel, levando a
decisões de layout baseadas em viewport desktop que não correspondem
à experiência de produção.

**Evidência técnica:**
Comportamento visual observado diretamente na interface pelo PM.
Nenhum bug tracker associado.

**Componente(s) afetado(s):**
Componente(s) de preview na página de configuração de formulário de
leads e na página de configuração de landing page
[nome exato: `nao_definido` — ver Lacunas Conhecidas].

**Riscos de não agir:**
Operadores continuarão tomando decisões de configuração com base em
uma visualização não representativa, aumentando a probabilidade de
retrabalho pós-publicação e de experiências inconsistentes para o
usuário final.
```

---
```
─────────────────────────────────────────
Campos preenchidos: 12/12 seções cobertas
Hipóteses declaradas: 4
Campos nao_definido: 3 (nome do componente, estrutura de layout,
                        componente compartilhado ou instâncias distintas)
Prontidão para PRD: pronto — lacunas são de discovery técnico, não
                    bloqueiam escopo, restrições ou objetivo

CHECKLIST DE PRONTIDÃO PARA PRD
[x] Por que isso existe
[x] Para quem existe
[x] O que entra e o que não entra
[x] Onde a mudança toca na arquitetura
[x] Como o sucesso será medido
[x] Quais restrições e riscos são incontornáveis
[x] O que ainda está em aberto (lacunas conhecidas declaradas)
[x] Origem auditável (intake original direto do PM)
[x] Sintoma observado (refactor)
[x] Impacto operacional (refactor)
[x] Evidência técnica (refactor)
[x] Componente(s) afetado(s) (refactor — parcialmente nao_definido,
    mas não bloqueia PRD)
[x] Riscos de não agir (refactor)
─────────────────────────────────────────
→ "aprovar" para gerar o arquivo
→ "ajustar [instrução]" para revisar antes de gravar
→ "bloqueado" se quiser registrar como incompleto e parar aqui