# 1. Resumo executivo
- Saúde geral do frontend da seção **evento**: **regular para produção, abaixo do padrão enterprise**.
- Principais riscos:
- bug crítico de progressão no wizard (`/eventos/novo`) com potencial auto-submissão/autoavanço;
- fragilidade de sessão/autenticação sob token inválido;
- baixa cobertura de testes nas telas e fluxos críticos de evento/leads;
- componentes e serviços monolíticos, elevando risco de regressão.
- **Nota geral: 5.9/10**.  
Justificativa curta: funciona no fluxo básico, mas há risco relevante em UX crítica, robustez de estado/erros, segurança de sessão e testabilidade.
- Smoke executado:
- `npm run typecheck` (ok),
- `npm run build` (ok, com warning de chunk grande),
- `npx vitest list` (apenas testes de auth/cpf; sem cobertura de evento/leads).
- **Não foi possível validar** smoke E2E real com interação autenticada no navegador neste ambiente CLI (sem automação de browser/sessão de UI nesta execução).

# 2. Mapa da área auditada
- Arquivos auditados (núcleo evento):
- `npbb/frontend/src/pages/NewEvent.tsx`
- `npbb/frontend/src/pages/EventsList.tsx`
- `npbb/frontend/src/pages/EventDetail.tsx`
- `npbb/frontend/src/pages/EventLeadFormConfig.tsx`
- `npbb/frontend/src/pages/EventGamificacao.tsx`
- `npbb/frontend/src/pages/EventAtivacoes.tsx`
- `npbb/frontend/src/pages/EventQuestionario.tsx`
- `npbb/frontend/src/components/eventos/EventWizardStepper.tsx`
- `npbb/frontend/src/components/eventos/EventoRow.tsx`
- Fluxo crítico de cadastro de clientes (leads):
- `npbb/frontend/src/pages/LeadsImport.tsx`
- `npbb/frontend/src/services/leads_import.ts`
- `npbb/frontend/src/services/eventos.ts`
- Sessão/segurança/guard:
- `npbb/frontend/src/store/auth.tsx`
- `npbb/frontend/src/components/ProtectedRoute.tsx`
- `npbb/frontend/src/services/auth.ts`
- Fluxos identificados:
- `/eventos` -> `/eventos/novo` ou `/eventos/:id/editar`
- `/eventos/:id/formulario-lead` -> `/eventos/:id/gamificacao` -> `/eventos/:id/ativacoes` -> `/eventos/:id/questionario`
- `/leads` para importação assistida e listagem de leads

# 3. Achados (tabela)

## FE-EVENTO-001
- **ID:** FE-EVENTO-001
- **Título:** Autoavanço/submissão involuntária na etapa de classificação do evento
- **Severidade:** Crítica
- **Categoria:** Bug
- **Localização:** `npbb/frontend/src/pages/NewEvent.tsx:618`, `npbb/frontend/src/pages/NewEvent.tsx:620`, `npbb/frontend/src/pages/NewEvent.tsx:673`, `npbb/frontend/src/pages/NewEvent.tsx:676`, `npbb/frontend/src/pages/NewEvent.tsx:727`, `npbb/frontend/src/pages/NewEvent.tsx:1231`, `npbb/frontend/src/pages/NewEvent.tsx:980`, `npbb/frontend/src/pages/NewEvent.tsx:1086`
- **Evidência:** formulário com `onSubmit`; etapa final navega direto após create/update; campos `Autocomplete` sem bloqueio explícito de Enter; botão final `type="submit"`.
- **Impacto:** usuário pode ser enviado para próxima fase sem concluir configuração de diretoria/territórios.
- **Causa provável:** Enter em campo de autocomplete dispara submit do form na etapa final.
- **Como reproduzir:** em `/eventos/novo`, ir à etapa “Classificação”, interagir com autocomplete e pressionar Enter.
- **Correção recomendada:** bloquear submit por Enter nos campos de classificação; exigir ação explícita no botão final; separar submit de navegação automática.
- **Quick win?** Sim
- **Esforço estimado:** S
- **Prioridade:** P0

## FE-EVENTO-002
- **ID:** FE-EVENTO-002
- **Título:** Stepper mostra “Em breve” em etapas já implementadas
- **Severidade:** Alta
- **Categoria:** Incoerência
- **Localização:** `npbb/frontend/src/components/eventos/EventWizardStepper.tsx:17`, `npbb/frontend/src/components/eventos/EventWizardStepper.tsx:24`, `npbb/frontend/src/pages/EventGamificacao.tsx:208`, `npbb/frontend/src/pages/EventAtivacoes.tsx:270`, `npbb/frontend/src/pages/EventQuestionario.tsx:607`
- **Evidência:** `showComingSoonFrom=2` por padrão; páginas reais de gamificação/ativações/questionário usam o stepper padrão.
- **Impacto:** UX contraditória e perda de confiança do usuário.
- **Causa provável:** configuração de placeholder não removida após implementação das etapas.
- **Como reproduzir:** abrir `/eventos/:id/gamificacao`, `/ativacoes`, `/questionario`.
- **Correção recomendada:** remover “Em breve” para etapas ativas ou tornar `showComingSoonFrom` obrigatório por tela.
- **Quick win?** Sim
- **Esforço estimado:** S
- **Prioridade:** P1

## FE-EVENTO-003
- **ID:** FE-EVENTO-003
- **Título:** Risco de loop de refresh/sessão com token inválido
- **Severidade:** Alta
- **Categoria:** Bug
- **Localização:** `npbb/frontend/src/store/auth.tsx:62`, `npbb/frontend/src/store/auth.tsx:70`, `npbb/frontend/src/components/ProtectedRoute.tsx:15`, `npbb/frontend/src/components/ProtectedRoute.tsx:20`
- **Evidência:** `refresh()` não limpa token em erro; `ProtectedRoute` chama `refresh()` quando `token && !user && !loading`.
- **Impacto:** possível spinner infinito, repetição de requests e bloqueio de navegação autenticada.
- **Causa provável:** tratamento incompleto de sessão inválida no refresh.
- **Como reproduzir:** token inválido no `localStorage` + usuário nulo.
- **Correção recomendada:** em erro de refresh, invalidar sessão (limpar token/user) e redirecionar login; adicionar trava de chamada em voo.
- **Quick win?** Sim
- **Esforço estimado:** S
- **Prioridade:** P1

## FE-EVENTO-004
- **ID:** FE-EVENTO-004
- **Título:** Ação “Editar” em Ativações está exposta mas não implementada
- **Severidade:** Média
- **Categoria:** Incoerência
- **Localização:** `npbb/frontend/src/pages/EventAtivacoes.tsx:522`, `npbb/frontend/src/pages/EventAtivacoes.tsx:525`
- **Evidência:** botão “Editar” exibe snackbar “Edicao sera implementada no proximo ticket.”
- **Impacto:** fricção operacional em fluxo crítico.
- **Causa provável:** feature parcial liberada em produção.
- **Como reproduzir:** abrir tabela de ativações e clicar no ícone de editar.
- **Correção recomendada:** implementar edição real ou remover/ocultar ação.
- **Quick win?** Sim
- **Esforço estimado:** S
- **Prioridade:** P1

## FE-EVENTO-005
- **ID:** FE-EVENTO-005
- **Título:** Mutação de estado aninhado no mapeamento de leads
- **Severidade:** Média
- **Categoria:** Bug
- **Localização:** `npbb/frontend/src/pages/LeadsImport.tsx:405`, `npbb/frontend/src/pages/LeadsImport.tsx:406`, `npbb/frontend/src/pages/LeadsImport.tsx:410`
- **Evidência:** cópia rasa de `preview` e sobrescrita de índice em `suggestions` (array reaproveitado).
- **Impacto:** inconsistências intermitentes de render/state em ajuste de mapeamento.
- **Causa provável:** update não-imutável de estrutura aninhada.
- **Como reproduzir:** alterar mapeamentos rapidamente em múltiplas linhas e observar comportamento inconsistente.
- **Correção recomendada:** atualizar `suggestions` com clone imutável (`map`/spread profundo).
- **Quick win?** Sim
- **Esforço estimado:** S
- **Prioridade:** P1

## FE-EVENTO-006
- **ID:** FE-EVENTO-006
- **Título:** Persistência de alias no fluxo de leads é “fire-and-forget” silenciosa
- **Severidade:** Média
- **Categoria:** Incoerência
- **Localização:** `npbb/frontend/src/pages/LeadsImport.tsx:146`, `npbb/frontend/src/pages/LeadsImport.tsx:164`, `npbb/frontend/src/pages/LeadsImport.tsx:165`
- **Evidência:** `createLeadAlias(...).catch(() => {})` sem await e sem feedback.
- **Impacto:** usuário acredita que mapeamento auxiliar foi persistido, mas pode não ter sido.
- **Causa provável:** alias tratado como cache sem transparência de falha.
- **Como reproduzir:** induzir falha de rede durante confirmação de mapeamento.
- **Correção recomendada:** usar `Promise.allSettled`, consolidar falhas e exibir aviso não bloqueante.
- **Quick win?** Sim
- **Esforço estimado:** S
- **Prioridade:** P2

## FE-EVENTO-007
- **ID:** FE-EVENTO-007
- **Título:** Parsing de erro frágil baseado em `Error.message` JSON stringificado
- **Severidade:** Média
- **Categoria:** Idiomatismo
- **Localização:** `npbb/frontend/src/services/eventos.ts:162`, `npbb/frontend/src/services/leads_import.ts:61`, `npbb/frontend/src/pages/EventAtivacoes.tsx:48`, `npbb/frontend/src/pages/EventGamificacao.tsx:65`
- **Evidência:** handlers usam `JSON.stringify(detail)` e telas fazem parse manual por mensagem.
- **Impacto:** contratos de erro frágeis e inconsistentes entre telas.
- **Causa provável:** ausência de `ApiError` tipado e padronizado.
- **Como reproduzir:** retornar `detail` estruturado alternando shape/campos.
- **Correção recomendada:** centralizar cliente HTTP com `ApiError` (`status`, `code`, `field`, `message`, `extra`).
- **Quick win?** Não
- **Esforço estimado:** M
- **Prioridade:** P1

## FE-EVENTO-008
- **ID:** FE-EVENTO-008
- **Título:** Token de sessão armazenado em `localStorage`
- **Severidade:** Alta
- **Categoria:** Segurança
- **Localização:** `npbb/frontend/src/store/auth.tsx:25`, `npbb/frontend/src/store/auth.tsx:49`, `npbb/frontend/src/store/auth.tsx:56`
- **Evidência:** leitura/escrita/remoção direta de `access_token` no browser storage.
- **Impacto:** maior superfície de exfiltração em cenário de XSS.
- **Causa provável:** estratégia de auth simplificada no frontend.
- **Como reproduzir:** inspeção de storage no navegador.
- **Correção recomendada:** migrar para cookie HttpOnly/SameSite + proteção CSRF no backend.
- **Quick win?** Não
- **Esforço estimado:** L
- **Prioridade:** P1

## FE-EVENTO-009
- **ID:** FE-EVENTO-009
- **Título:** Ausência de timeout/abort/retry padronizado nas chamadas HTTP
- **Severidade:** Média
- **Categoria:** Performance
- **Localização:** `npbb/frontend/src/services/eventos.ts:194`, `npbb/frontend/src/services/eventos.ts:265`, `npbb/frontend/src/services/leads_import.ts:76`, `npbb/frontend/src/services/auth.ts:36`
- **Evidência:** chamadas `fetch` sem `AbortController`, sem timeout de cliente e sem estratégia de retry.
- **Impacto:** UX ruim em rede degradada e risco de múltiplas ações concorrentes.
- **Causa provável:** client HTTP não centralizado.
- **Como reproduzir:** simular alta latência/perda e observar travamentos sem expiração controlada.
- **Correção recomendada:** wrapper `fetchWithTimeout` + cancelamento por tela + retry apenas para GET idempotente.
- **Quick win?** Não
- **Esforço estimado:** M
- **Prioridade:** P2

## FE-EVENTO-010
- **ID:** FE-EVENTO-010
- **Título:** Componente `NewEvent` inchado e com múltiplas responsabilidades
- **Severidade:** Média
- **Categoria:** Monólito
- **Localização:** `npbb/frontend/src/pages/NewEvent.tsx:1`
- **Evidência:** arquivo com ~1156 linhas; mistura carregamento, validação, foco por query, wizard, submit e navegação.
- **Impacto:** manutenção difícil e alto risco de regressão.
- **Causa provável:** crescimento incremental sem extração de hooks/steps.
- **Como reproduzir:** inspeção estrutural.
- **Correção recomendada:** quebrar em container + hooks + componentes de step.
- **Quick win?** Não
- **Esforço estimado:** L
- **Prioridade:** P2

## FE-EVENTO-011
- **ID:** FE-EVENTO-011
- **Título:** `LeadsImport` concentra wizard + regras + listagem em um único componente
- **Severidade:** Média
- **Categoria:** Monólito
- **Localização:** `npbb/frontend/src/pages/LeadsImport.tsx:1`
- **Evidência:** ~612 linhas com múltiplos fluxos concorrentes no mesmo estado local.
- **Impacto:** complexidade cognitiva alta e evolução lenta.
- **Causa provável:** ausência de decomposição por feature.
- **Como reproduzir:** inspeção estrutural.
- **Correção recomendada:** separar wizard de import, tabela de leads e diálogos em módulos independentes.
- **Quick win?** Não
- **Esforço estimado:** M
- **Prioridade:** P2

## FE-EVENTO-012
- **ID:** FE-EVENTO-012
- **Título:** Serviço `eventos.ts` é monolítico e mistura domínios distintos
- **Severidade:** Média
- **Categoria:** Monólito
- **Localização:** `npbb/frontend/src/services/eventos.ts:1`
- **Evidência:** ~619 linhas contendo CRUD evento, CSV, formulário lead, questionário, gamificação e ativações.
- **Impacto:** baixa coesão, difícil versionar contratos por domínio.
- **Causa provável:** centralização excessiva do client REST.
- **Como reproduzir:** inspeção estrutural.
- **Correção recomendada:** modularizar por domínio (`eventos.core`, `eventos.form`, `eventos.gamificacao`, etc.).
- **Quick win?** Não
- **Esforço estimado:** M
- **Prioridade:** P2

## FE-EVENTO-013
- **ID:** FE-EVENTO-013
- **Título:** Mensagens de placeholder desatualizadas no Formulário de Lead
- **Severidade:** Baixa
- **Categoria:** Obsolescência
- **Localização:** `npbb/frontend/src/pages/EventLeadFormConfig.tsx:322`, `npbb/frontend/src/pages/EventLeadFormConfig.tsx:331`, `npbb/frontend/src/pages/EventLeadFormConfig.tsx:172`, `npbb/frontend/src/pages/EventLeadFormConfig.tsx:283`
- **Evidência:** texto diz “ainda não salva”, mas há `handleSave` e botão “Salvar”.
- **Impacto:** confusão de UX e suporte.
- **Causa provável:** texto legado não atualizado.
- **Como reproduzir:** abrir tela `/eventos/:id/formulario-lead`.
- **Correção recomendada:** alinhar copy com comportamento real.
- **Quick win?** Sim
- **Esforço estimado:** S
- **Prioridade:** P3

## FE-EVENTO-014
- **ID:** FE-EVENTO-014
- **Título:** Cobertura de testes insuficiente para evento e leads
- **Severidade:** Alta
- **Categoria:** Testes
- **Localização:** `npbb/frontend/src/services/__tests__/auth.test.ts`, `npbb/frontend/src/services/__tests__/usuarios.password_reset.test.ts`, `npbb/frontend/src/utils/__tests__/cpf.test.ts`
- **Evidência:** não há testes para `NewEvent`, `EventsList`, `EventLeadFormConfig`, `LeadsImport`, `EventGamificacao`, `EventAtivacoes`, `EventQuestionario`.
- **Impacto:** regressões chegam à produção em fluxos críticos.
- **Causa provável:** foco de teste restrito a auth/utils.
- **Como reproduzir:** varredura de testes (`npx vitest list`).
- **Correção recomendada:** suíte mínima por fluxo crítico (wizard evento + leads import).
- **Quick win?** Não
- **Esforço estimado:** M
- **Prioridade:** P1

## FE-EVENTO-015
- **ID:** FE-EVENTO-015
- **Título:** Ausência de TSDoc/JSDoc em exports críticos
- **Severidade:** Baixa
- **Categoria:** Docstring
- **Localização:** `npbb/frontend/src/services/eventos.ts:168`, `npbb/frontend/src/services/leads_import.ts:67`, `npbb/frontend/src/store/auth.tsx:18`, `npbb/frontend/src/components/ProtectedRoute.tsx:10`, `npbb/frontend/src/components/eventos/EventoRow.tsx:71`
- **Evidência:** exports sem documentação formal de contrato/comportamento.
- **Impacto:** onboarding lento e risco de uso incorreto de APIs internas.
- **Causa provável:** ausência de padrão de documentação no frontend.
- **Como reproduzir:** inspeção dos exports.
- **Correção recomendada:** padronizar TSDoc em funções/hooks/componentes exportados.
- **Quick win?** Sim
- **Esforço estimado:** S
- **Prioridade:** P3

## FE-EVENTO-016
- **ID:** FE-EVENTO-016
- **Título:** Lacuna de acessibilidade em ação de QRCode
- **Severidade:** Baixa
- **Categoria:** Acessibilidade
- **Localização:** `npbb/frontend/src/pages/EventDetail.tsx:525`
- **Evidência:** `IconButton` com ícone QR sem `aria-label`.
- **Impacto:** navegação por leitor de tela prejudicada.
- **Causa provável:** ausência de checklist A11y sistemático.
- **Como reproduzir:** inspeção semântica no componente.
- **Correção recomendada:** incluir `aria-label` descritivo e validar com auditoria A11y.
- **Quick win?** Sim
- **Esforço estimado:** S
- **Prioridade:** P3

## FE-EVENTO-017
- **ID:** FE-EVENTO-017
- **Título:** Importador de leads sem validação explícita de tipo/tamanho de arquivo no cliente
- **Severidade:** Média
- **Categoria:** Validação
- **Localização:** `npbb/frontend/src/pages/LeadsImport.tsx:295`, `npbb/frontend/src/pages/LeadsImport.tsx:300`, `npbb/frontend/src/pages/LeadsImport.tsx:301`
- **Evidência:** `accept` existe, mas não há bloqueio por MIME/tamanho nem feedback preventivo; rótulo “Importar XLSX” conflita com `.csv` aceito.
- **Impacto:** falhas evitáveis e UX ambígua.
- **Causa provável:** validação delegada integralmente ao backend.
- **Como reproduzir:** selecionar arquivo inválido/grande e observar feedback tardio.
- **Correção recomendada:** validar extensão/MIME/tamanho antes do upload e corrigir copy do botão.
- **Quick win?** Sim
- **Esforço estimado:** S
- **Prioridade:** P2

## FE-EVENTO-018
- **ID:** FE-EVENTO-018
- **Título:** Bundle principal elevado para o porte do módulo
- **Severidade:** Média
- **Categoria:** Performance
- **Localização:** build frontend (`npm run build`) com chunk principal `~806.20 kB`
- **Evidência:** warning do Vite sobre chunk > 500kB.
- **Impacto:** piora de TTI e experiência em rede móvel.
- **Causa provável:** ausência de code-splitting por rota/módulo.
- **Como reproduzir:** executar build e revisar relatório de chunks.
- **Correção recomendada:** lazy-load de rotas pesadas e split do domínio evento/leads.
- **Quick win?** Não
- **Esforço estimado:** M
- **Prioridade:** P2

# 4. Auditoria especial — Cadastro de clientes (frontend)

- Fluxo atual (inferido):
- upload de arquivo em `/leads`;
- preview com sugestões de mapeamento;
- ajuste manual de campo e referência;
- validação de mapeamento;
- importação e resumo;
- listagem paginada de leads importados.
- Pontos frágeis:
- mutação de estado no mapeamento (`LeadsImport`);
- alias assíncrono silencioso (sem garantia de persistência percebida);
- ausência de timeout/retry/cancel padronizado;
- validação client-side incompleta para arquivo e para deduplicação de campos mapeados.
- Bugs reais/prováveis:
- bug real de update não-imutável no mapping (`npbb/frontend/src/pages/LeadsImport.tsx:405`);
- provável inconsistência de alias em falha de rede (`npbb/frontend/src/pages/LeadsImport.tsx:164`);
- provável concorrência de requisições auxiliares sem cancelamento (`npbb/frontend/src/pages/LeadsImport.tsx:194`).
- Riscos de duplicidade/inconsistência de cadastro:
- import acionado em ambiente lento sem política de idempotência explícita no frontend;
- mapeamentos conflitantes dependem só de erro tardio da API;
- alias parcialmente persistido pode degradar próximas importações.
- Melhorias de UX e robustez:
- bloquear “Importar” com trava in-flight síncrona local;
- validar arquivo antes de enviar (tipo/tamanho);
- mostrar status de persistência de alias (ok/falhou);
- feedback de progresso por etapa (preview, validate, import).
- Melhorias de validação e tipagem:
- restringir campos duplicados no mapeamento no cliente;
- tipar erro com `ApiError` em vez de parse de string;
- remover `any` de handlers críticos.
- Melhorias de segurança e privacidade:
- revisar exibição de PII no grid de leads por perfil;
- reduzir superfície de token no frontend (migrar de `localStorage` para sessão segura);
- padronizar sanitização em mensagens de erro renderizadas.

# 5. Refatoração para código mais conciso e idiomático
- Padrões problemáticos atuais:
- componentes muito grandes e multifuncionais;
- parsing manual de erro por string;
- serviço único com múltiplos domínios;
- estado local denso para fluxos de wizard.
- Padrões idiomáticos sugeridos (React + TS):
- container/presenter por tela;
- hooks de domínio (`useEventWizard*`, `useLeadImport*`);
- cliente HTTP único com erro tipado;
- updates de estado 100% imutáveis.
- Quebras por responsabilidade:
- `NewEvent`: separar steps (agência/info/classificação), carga de domínios, validação e submit;
- `LeadsImport`: separar wizard/import da tabela de listagem;
- `eventos.ts`: separar por subdomínio.
- Estratégia de simplificação sem regressão:
- extrair primeiro comportamento puro e cobrir com testes;
- manter contrato de API estável;
- migrar tela por tela com feature flags internas simples (sem overengineering).

# 6. Plano de ação enterprise (priorizado)

## Fase 0 (hotfixes)
- Objetivo: eliminar falhas de fluxo e incoerências visíveis.
- Itens:
- corrigir auto-submit na etapa de classificação de evento;
- remover “Em breve” das etapas já entregues;
- remover/ocultar botão “Editar” de ativação até implementar;
- corrigir textos desatualizados no Formulário de Lead.
- Dependências: nenhuma estrutural.
- Risco de regressão: baixo.
- Critério de aceite:
- usuário consegue configurar diretoria/territórios sem salto automático;
- stepper sem mensagens contraditórias;
- sem ação fake em produção.

## Fase 1 (estabilização)
- Objetivo: aumentar previsibilidade de estado/erro/rede.
- Itens:
- introduzir `ApiError` tipado;
- padronizar timeout/abort/retry;
- tornar updates de estado imutáveis no mapeamento de leads;
- adicionar validação client-side de arquivo e de mapeamento.
- Dependências: aprovação do contrato de erro interno.
- Risco de regressão: médio.
- Critério de aceite:
- erros consistentes entre telas;
- sem requests órfãs após navegação;
- import de leads com feedback determinístico.

## Fase 2 (refatoração estrutural)
- Objetivo: reduzir complexidade e facilitar manutenção.
- Itens:
- quebrar `NewEvent`/`LeadsImport` em módulos;
- fatiar `services/eventos.ts` por domínio;
- extrair hooks de domínio.
- Dependências: Fase 1 concluída.
- Risco de regressão: médio/alto (controlável com testes).
- Critério de aceite:
- redução de tamanho/complexidade por arquivo;
- sem mudança de comportamento funcional.

## Fase 3 (endurecimento com testes e observabilidade)
- Objetivo: reduzir regressão em produção.
- Itens:
- testes de unidade e integração para fluxos críticos;
- smoke E2E para wizard de evento e import de leads;
- métricas de erro por endpoint/tela.
- Dependências: Fases 0–2.
- Risco de regressão: baixo (após cobertura).
- Critério de aceite:
- suíte cobrindo happy path + erros críticos;
- regressão do bug de autoavanço protegida por teste.

# 7. Checklist de qualidade pós-auditoria
- funcional:
- [ ] wizard de evento não avança sem ação explícita
- [ ] import de leads mantém consistência de mapeamento e resultado
- UX:
- [ ] mensagens e labels coerentes com comportamento real
- [ ] loading/error/success claros em todas as etapas
- acessibilidade:
- [ ] controles iconográficos com `aria-label`
- [ ] navegação por teclado validada nas telas críticas
- segurança:
- [ ] estratégia de token revisada
- [ ] erros sensíveis não expostos em UI
- performance:
- [ ] chunk principal abaixo do alvo definido
- [ ] rotas pesadas com lazy-load
- testes:
- [ ] cobertura de evento/leads com cenários críticos
- [ ] smoke automatizado para regressões de fluxo
- documentação (TSDoc/JSDoc):
- [ ] exports críticos documentados com contrato de uso

---

## Top 10 quick wins (impacto alto / esforço baixo)
1. Bloquear submit por Enter na classificação de evento.
2. Tornar navegação para próxima fase explícita (botão dedicado) após salvar evento.
3. Ajustar `showComingSoonFrom` no stepper.
4. Remover/ocultar editar de ativações até implementar.
5. Corrigir mutação de estado em `LeadsImport`.
6. Exibir aviso quando persistência de alias falhar.
7. Validar extensão/tamanho de arquivo antes do upload de leads.
8. Corrigir textos “ainda não salva” em `EventLeadFormConfig`.
9. Adicionar `aria-label` no botão de QR em `EventDetail`.
10. Adicionar trava local contra double-click em ações de import/salvar.

## Top 10 riscos de produção
1. Autoavanço no cadastro de evento (erro de fluxo crítico).
2. Sessão presa em estado inválido com refresh repetido.
3. Regressões silenciosas por falta de testes de evento/leads.
4. Erros inconsistentes por parse de string JSON.
5. Perda de confiança no alias por persistência silenciosa.
6. Ações concorrentes em rede ruim sem timeout/cancel.
7. Exposição de token via `localStorage`.
8. Componentes monolíticos dificultando correções seguras.
9. Ação “Editar” não implementada em fluxo de ativações.
10. Bundle grande degradando experiência em conexões lentas.

## Lista de refactors sugeridos com nomes novos
1. `NewEvent` -> `EventWizardPage`
2. `handleSubmit` (`NewEvent`) -> `submitEventWizard`
3. `eventStepFields` -> `wizardStepValidationFields`
4. `LeadsImport` -> `LeadImportPage`
5. bloco de mapeamento em `LeadsImport` -> `LeadMappingTable`
6. bloco de listagem em `LeadsImport` -> `LeadListTable`
7. `handleConfirmMapping` -> `validateAndPersistLeadMappings`
8. `services/eventos.ts` -> `services/eventos/core.ts`
9. `services/eventos.ts` (form) -> `services/eventos/formConfig.ts`
10. `services/eventos.ts` (gamificação/ativação/questionário) -> `services/eventos/workflow.ts`

## Template de TSDoc/JSDoc (funções/hooks/componentes críticos)

```ts
/**
 * Executa o submit final do wizard de evento.
 * Garante validação da etapa atual e envia payload consistente para API.
 *
 * @param params.token Token de autenticação do usuário.
 * @param params.eventoId ID do evento em edição (opcional para criação).
 * @param params.form Estado atual do formulário.
 * @returns Promise com o evento persistido.
 * @throws {ApiError} Quando a API retorna erro de negócio/validação.
 */
export async function submitEventWizard(params: SubmitEventWizardParams): Promise<EventoRead> {
  // ...
}
```

```ts
/**
 * Hook de orquestração do fluxo de importação de leads.
 * Controla upload, preview, validação de mapeamento e execução do import.
 *
 * @returns Estado e actions do fluxo de importação.
 */
export function useLeadImportWorkflow(): UseLeadImportWorkflowResult {
  // ...
}
```

```tsx
/**
 * Tabela de mapeamento de colunas de importação de leads.
 * Permite editar campo destino e referências auxiliares por coluna.
 */
export function LeadMappingTable(props: LeadMappingTableProps) {
  // ...
}
```
