# EPIC-F3-02 — Integração Gamificação no LandingPageView
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** AJUSTE-FINO-LANDING-PAGES-DINAMICAS | **fase:** F3 | **status:** 🔲

---
## 1. Resumo do Épico
Integrar o componente `GamificacaoBlock` ao `LandingPageView`, gerenciar os estados
`leadSubmitted` e `ativacaoLeadId` no componente pai, conectar o callback `onComplete`
ao serviço `completeGamificacao()`, e implementar o fluxo de reset completo ("Nova
pessoa") que limpa formulário e retorna o bloco de gamificação ao estado inicial.

**Resultado de Negócio Mensurável:** O fluxo completo UC-03 (ativação com gamificação)
funciona end-to-end: formulário → habilitação do bloco → participação → conclusão →
persistência → feedback → reset para próximo lead.

## 2. Contexto Arquitetural
- Componente pai: `frontend/src/components/landing/LandingPageView.tsx`
- Componente filho: `frontend/src/components/landing/GamificacaoBlock.tsx` (criado no EPIC-F3-01)
- Serviço: `completeGamificacao()` (criado no EPIC-F3-01)
- Estado do pai precisa de: `leadSubmitted: boolean`, `ativacaoLeadId: number | null`
- `handleSubmitSuccess` precisa capturar `ativacao_lead_id` da response do submit
- `handleReset` precisa limpar formulário, `submitted`, `leadSubmitted` e `ativacaoLeadId`
- Posição do bloco: após conteúdo principal, antes do footer

## 3. Riscos e Armadilhas
- O `handleSubmitSuccess` atual pode não receber `ativacao_lead_id` se o backend não estiver atualizado — testar com backend F2
- Montagem condicional (`gamificacoes.length > 0`) deve usar optional chaining: `data.gamificacoes?.length > 0`
- Reset deve ser atômico — todos os estados resetados no mesmo batch para evitar flicker
- `completeGamificacao` é async — erros de rede devem ser tratados sem quebrar o estado da UI

## 4. Definition of Done do Épico
- [ ] `LandingPageView` possui estados `leadSubmitted` e `ativacaoLeadId`
- [ ] `handleSubmitSuccess` captura `ativacao_lead_id` da response e seta `leadSubmitted=true`
- [ ] `GamificacaoBlock` montado condicionalmente quando `data.gamificacoes?.length > 0`
- [ ] `GamificacaoBlock` posicionado após conteúdo principal, antes do footer
- [ ] Callback `onComplete` chama `completeGamificacao(ativacaoLeadId, payload)` com tratamento de erro
- [ ] Callback `onReset` limpa formulário, `submitted`, `leadSubmitted` e `ativacaoLeadId`
- [ ] Fluxo UC-03 funcional end-to-end
- [ ] Fluxo UC-01 (sem gamificação) não afetado — bloco não aparece
- [ ] Modo preview: bloco visível em somente-leitura (botões desabilitados)

---
## Issues

### AFLPD-F3-02-001 — Gerenciar estado de gamificação no LandingPageView
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Adicionar estados `leadSubmitted` e `ativacaoLeadId` ao `LandingPageView`, atualizar
`handleSubmitSuccess` para capturar `ativacao_lead_id` da response, e criar
`handleGamificacaoComplete` que chama o serviço de conclusão de gamificação.

**Plano TDD:**
- **Red:** Escrever teste que submete formulário com mock de API retornando `ativacao_lead_id=42` e verifica que `leadSubmitted` torna-se `true` e `ativacaoLeadId` é `42`.
- **Green:** Adicionar `useState` para `leadSubmitted` e `ativacaoLeadId`, atualizar handler de submit, criar `handleGamificacaoComplete`.
- **Refactor:** Extrair lógica de estado de gamificação para custom hook `useGamificacaoState` se complexidade justificar.

**Critérios de Aceitação:**
- Given formulário submetido com sucesso, When response contém `ativacao_lead_id: 42`, Then `leadSubmitted` é `true` e `ativacaoLeadId` é `42`
- Given `ativacaoLeadId` é `42`, When `handleGamificacaoComplete(5)` chamado, Then `completeGamificacao(42, { gamificacao_id: 5, gamificacao_completed: true })` é invocado
- Given `ativacaoLeadId` é `null`, When `handleGamificacaoComplete` chamado, Then nenhuma chamada API é feita (early return)

**Tarefas:**
- [ ] T1: Adicionar `const [leadSubmitted, setLeadSubmitted] = useState(false)` ao componente
- [ ] T2: Adicionar `const [ativacaoLeadId, setAtivacaoLeadId] = useState<number | null>(null)` ao componente
- [ ] T3: Atualizar `handleSubmitSuccess` para extrair `ativacao_lead_id` da response e setar ambos os estados
- [ ] T4: Criar `handleGamificacaoComplete` com guard `if (!ativacaoLeadId) return` e chamada ao serviço
- [ ] T5: Adicionar tratamento de erro na chamada async (try/catch com feedback ao usuário)

**Notas técnicas:**
A tipagem de `LandingSubmitResponse` já deve incluir `ativacao_lead_id` (definida na
F1 EPIC-F1-02). O `handleGamificacaoComplete` é async mas declarado como
`async (gamificacaoId: number) => void` para compatibilidade com `GamificacaoBlockProps.onComplete`.

---
### AFLPD-F3-02-002 — Montar GamificacaoBlock condicional e implementar reset
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** AFLPD-F3-02-001

**Descrição:**
Montar o `GamificacaoBlock` condicionalmente no JSX do `LandingPageView` (quando
`gamificacoes.length > 0`), posicioná-lo antes do footer, passar as props necessárias,
e implementar `handleReset` que limpa todos os estados (formulário, submitted,
leadSubmitted, ativacaoLeadId).

**Plano TDD:**
- **Red:** Escrever teste que renderiza landing com `gamificacoes: []` e verifica que `GamificacaoBlock` não está no DOM. Escrever teste com `gamificacoes: [...]` e verificar presença. Escrever teste que clica "Nova pessoa" e verifica reset completo.
- **Green:** Adicionar montagem condicional no JSX, passar props, implementar `handleReset`.
- **Refactor:** Verificar que `handleReset` é atômico (todos os setters no mesmo batch) para evitar re-renders intermediários.

**Critérios de Aceitação:**
- Given `data.gamificacoes` vazio, When landing renderizada, Then `GamificacaoBlock` não presente no DOM
- Given `data.gamificacoes` com 1 item, When landing renderizada, Then `GamificacaoBlock` presente entre conteúdo e footer
- Given estado COMPLETED, When "Nova pessoa" clicado, Then formulário limpo, `leadSubmitted=false`, `ativacaoLeadId=null`, bloco em PRESENTING
- Given modo preview, When landing renderizada com gamificações, Then bloco visível com botões desabilitados

**Tarefas:**
- [ ] T1: Adicionar renderização condicional: `{data.gamificacoes?.length > 0 && <GamificacaoBlock ... />}`
- [ ] T2: Posicionar bloco após seção de conteúdo, antes do `<footer>`
- [ ] T3: Passar props: `gamificacoes`, `leadSubmitted`, `onComplete={handleGamificacaoComplete}`, `onReset={handleReset}`
- [ ] T4: Implementar `handleReset`: resetar formulário, `setSubmitted(null)`, `setLeadSubmitted(false)`, `setAtivacaoLeadId(null)`
- [ ] T5: Tratar modo preview: passar `leadSubmitted={false}` para manter botões desabilitados
- [ ] T6: Testar fluxo UC-03 completo: formulário → gamificação → reset

**Notas técnicas:**
O `handleReset` deve usar `React.startTransition` ou batch updates para evitar flicker
durante o reset de múltiplos estados. Em modo preview (`isPreview`), o bloco de
gamificação é visível mas em somente-leitura — `leadSubmitted` fixo em `false`.

## 5. Notas de Implementação Globais
- O fluxo end-to-end (UC-03) deve ser testado manualmente após integração
- Erros de rede no endpoint de gamificação não devem quebrar a UI — exibir toast/snackbar
- O reset deve ser instantâneo e sem transições visuais desnecessárias
- Preview mode: bloco visível, botões desabilitados, sem funcionalidade de submit
