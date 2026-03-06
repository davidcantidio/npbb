# EPIC-F3-01 — Componente GamificacaoBlock e Máquina de Estados
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** AJUSTE-FINO-LANDING-PAGES-DINAMICAS | **fase:** F3 | **status:** 🔲

---
## 1. Resumo do Épico
Criar o componente React `GamificacaoBlock` com máquina de estados interna
(`PRESENTING → ACTIVE → COMPLETED`), tipagem via `GamificacaoBlockProps`, renderização
do card de gamificação (nome, descrição, prêmio) e lógica de habilitação de botões
controlada pela prop `leadSubmitted`.

**Resultado de Negócio Mensurável:** O bloco de gamificação é apresentado na landing
page de forma visualmente integrada, guiando o lead do cadastro à participação na
gamificação com feedback imediato.

## 2. Contexto Arquitetural
- Componente: `frontend/src/components/landing/GamificacaoBlock.tsx` (novo)
- Tipos: `GamificacaoPublic`, `GamificacaoBlockProps` em `frontend/src/types/landing_public.ts`
- Props recebidas do pai: `gamificacoes` (array), `leadSubmitted` (boolean), `onComplete` (callback), `onReset` (callback)
- Estado interno: `GamificacaoState = "presenting" | "active" | "completed"`
- Sem estado `IDLE` — responsabilidade de não-montagem é do componente pai
- Componentes MUI: `Paper`, `Typography`, `Button`, `Alert`

## 3. Riscos e Armadilhas
- `gamificacoes` como array pode ter length > 1 no futuro — componente deve renderizar `gamificacoes[0]` por ora
- Transição `PRESENTING → ACTIVE` deve verificar `leadSubmitted === true` como guard
- `onComplete` é async (chama API) — tratar loading state e erro
- `onReset` deve retornar o estado interno para `PRESENTING`, não para um estado inexistente

## 4. Definition of Done do Épico
- [ ] Componente `GamificacaoBlock.tsx` criado em `frontend/src/components/landing/`
- [ ] Tipo `GamificacaoState` definido como union type `"presenting" | "active" | "completed"`
- [ ] Interface `GamificacaoBlockProps` com `gamificacoes`, `leadSubmitted`, `onComplete`, `onReset`
- [ ] Estado `PRESENTING`: exibe nome, descrição, prêmio; botão desabilitado quando `!leadSubmitted`
- [ ] Estado `PRESENTING` com `leadSubmitted=true`: botão habilitado
- [ ] Texto de orientação "Preencha o cadastro acima para participar" quando `!leadSubmitted`
- [ ] Estado `ACTIVE`: instruções de participação visíveis; botão "Concluí" disponível
- [ ] Estado `COMPLETED`: `titulo_feedback` e `texto_feedback` exibidos
- [ ] Transições corretas e guards implementados
- [ ] Tratamento de loading e erro na chamada de `onComplete`

---
## Issues

### AFLPD-F3-01-001 — Criar tipos e interface do GamificacaoBlock
**tipo:** feature | **sp:** 2 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Definir os tipos TypeScript necessários para o componente `GamificacaoBlock`:
`GamificacaoState`, `GamificacaoBlockProps`, e os tipos de serviço
`GamificacaoCompletePayload` e `GamificacaoCompleteResponse`. Criar a função de
serviço `completeGamificacao()`.

**Plano TDD:**
- **Red:** Escrever teste de tipo que instancia `GamificacaoBlockProps` com todos os campos e verifica compilação.
- **Green:** Adicionar tipos ao arquivo `landing_public.ts` e criar serviço em `frontend/src/services/` ou arquivo equivalente.
- **Refactor:** Consolidar tipos de gamificação em seção dedicada do arquivo de tipos.

**Critérios de Aceitação:**
- Given arquivo de tipos, When compilado com `tsc --noEmit`, Then todos os tipos de gamificação compilam sem erro
- Given `completeGamificacao(42, { gamificacao_id: 5, gamificacao_completed: true })`, When chamado, Then retorna `GamificacaoCompleteResponse` tipada

**Tarefas:**
- [ ] T1: Adicionar `type GamificacaoState = "presenting" | "active" | "completed"` ao arquivo de tipos
- [ ] T2: Adicionar interface `GamificacaoBlockProps` com `gamificacoes: GamificacaoPublic[]`, `leadSubmitted: boolean`, `onComplete: (gamificacaoId: number) => void`, `onReset: () => void`
- [ ] T3: Adicionar tipos `GamificacaoCompletePayload` e `GamificacaoCompleteResponse`
- [ ] T4: Implementar função `completeGamificacao(ativacaoLeadId, payload)` no módulo de serviços da landing
- [ ] T5: Verificar compilação TypeScript

**Notas técnicas:**
`onComplete` é declarado como `(gamificacaoId: number) => void` na interface porque
o componente não gerencia a promise — o pai que faz a chamada API é quem trata o
await. Se necessário, o componente pode chamar `onComplete` e tratar loading
internamente via try/catch se `onComplete` retornar Promise.

---
### AFLPD-F3-01-002 — Implementar componente GamificacaoBlock com máquina de estados
**tipo:** feature | **sp:** 5 | **prioridade:** alta | **status:** 🔲
**depende de:** AFLPD-F3-01-001

**Descrição:**
Implementar o componente React `GamificacaoBlock` com máquina de estados interna
(`PRESENTING → ACTIVE → COMPLETED`), renderização condicional por estado, guards
de transição e tratamento de loading/erro.

**Plano TDD:**
- **Red:** Escrever testes que: (1) renderizam o bloco com `leadSubmitted=false` e verificam botão desabilitado; (2) renderizam com `leadSubmitted=true`, simulam clique em "Quero participar" e verificam transição para ACTIVE; (3) simulam clique em "Concluí" e verificam chamada de `onComplete` e exibição de feedback.
- **Green:** Implementar componente com `useState<GamificacaoState>("presenting")`, renderização condicional por estado, guards e callbacks.
- **Refactor:** Extrair sub-componentes se o JSX exceder 100 linhas (ex: `GamificacaoCard`, `GamificacaoFeedback`).

**Critérios de Aceitação:**
- Given `leadSubmitted=false`, When bloco renderizado, Then botão "Quero participar" está desabilitado e texto "Preencha o cadastro acima para participar" visível
- Given `leadSubmitted=true`, When botão "Quero participar" clicado, Then estado transiciona para ACTIVE e instruções de participação aparecem
- Given estado ACTIVE, When botão "Concluí" clicado, Then `onComplete(gamificacaoId)` é chamado e estado transiciona para COMPLETED
- Given estado COMPLETED, When bloco renderizado, Then `titulo_feedback` e `texto_feedback` da gamificação são exibidos
- Given estado COMPLETED, When "Nova pessoa" clicado, Then `onReset()` é chamado

**Tarefas:**
- [ ] T1: Criar arquivo `frontend/src/components/landing/GamificacaoBlock.tsx`
- [ ] T2: Implementar estado interno com `useState<GamificacaoState>("presenting")`
- [ ] T3: Renderizar card PRESENTING: nome, descrição, prêmio, botão condicional
- [ ] T4: Implementar guard: transição para ACTIVE só quando `leadSubmitted === true`
- [ ] T5: Renderizar estado ACTIVE: instruções + botão "Concluí"
- [ ] T6: Implementar transição ACTIVE → COMPLETED: chamar `onComplete`, exibir loading, tratar erro
- [ ] T7: Renderizar estado COMPLETED: `titulo_feedback` + `texto_feedback`
- [ ] T8: Implementar "Nova pessoa" → chamar `onReset()` e resetar estado para PRESENTING

**Notas técnicas:**
O componente usa `gamificacoes[0]` por padrão (modelo 1:1). A prop `gamificacoes`
é array para compatibilidade futura. O loading state durante `onComplete` pode usar
um `useState<boolean>(false)` local para desabilitar o botão "Concluí" enquanto a
API responde.

## 5. Notas de Implementação Globais
- O componente deve ser puro — sem efeitos colaterais além das callbacks
- Testar com gamificação completa (todos os campos) e com campos opcionais ausentes
- Acessibilidade: botões desabilitados devem ter `aria-disabled` e texto de orientação deve ser legível por screen readers
- O estilo visual deve seguir o `Paper` com `borderRadius: 3` (24px) da F1
