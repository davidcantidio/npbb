---
doc_id: "INTAKE-LP-QR-ATIVACOES.md"
version: "1.0"
status: "draft"
owner: "PM"
last_updated: "2026-03-11"
project: "LP"
intake_kind: "new-capability"
source_mode: "original"
origin_project: "nao_aplicavel"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "nao_aplicavel"
product_type: "campaign-experience"
delivery_surface: "fullstack-module"
business_domain: "landing-pages"
criticality: "media"
data_sensitivity: "lgpd"
integrations:
  - "eventos"
  - "formulario-lead"
  - "leads"
change_type: "nova-capacidade"
audit_rigor: "standard"
---

# INTAKE - LP (QR por Ativação)

> Intake para nova mecânica de QR-code por ativação, fluxo CPF-first e reconhecimento de leads entre ativações no mesmo evento.

## 0. Rastreabilidade de Origem

- projeto de origem: LP
- fase de origem: nao_aplicavel
- auditoria de origem: nao_aplicavel
- relatorio de origem: nao_aplicavel
- motivo da abertura deste intake: demanda do usuário na página de formulário de leads (http://127.0.0.1:5173/eventos/111/formulario-lead) para suportar ativações com QR-codes, validação de CPF e reconhecimento de leads entre ativações.

## 1. Resumo Executivo

- nome curto da iniciativa: QR por ativação e fluxo CPF-first
- tese em 1 frase: Cada ativação de um evento terá seu próprio QR-code; o visitante acessa via QR, valida CPF na primeira vez e, em ativações subsequentes no mesmo evento, é reconhecido automaticamente, com cada escaneada registrando uma conversão.
- valor esperado em 3 linhas:
  - Rastreabilidade por ativação: cada QR mapeia para uma ativação e permite medir conversões por ponto de contato.
  - Experiência fluida: lead reconhecido não repete CPF em novas ativações do mesmo evento.
  - Flexibilidade: ativações podem permitir conversão única ou múltipla, com opção de registrar outro CPF quando alguém usa o celular para converter terceiros.

## 2. Problema ou Oportunidade

- problema atual: Não existe conceito de ativação com QR próprio; não há fluxo CPF-first nem reconhecimento de leads entre pontos de contato no mesmo evento; conversões não são atribuídas por ativação.
- evidencia do problema: Página atual de formulário de leads (http://127.0.0.1:5173/eventos/111/formulario-lead) não contempla ativações nem QR-codes; fluxo é genérico.
- custo de nao agir: Perda de granularidade de atribuição; leads repetem dados desnecessariamente; impossibilidade de limitar conversões por ativação.
- por que agora: Demanda explícita do usuário para suportar campanhas com múltiplos pontos de ativação (stands, materiais impressos, etc.) e métricas por ativação.

## 3. Publico e Operadores

- usuario principal: Visitante que escaneia o QR da ativação e preenche o formulário de lead.
- usuario secundario: Operador que configura ativações (QR, tipo de conversão única/múltipla) e visualiza conversões por ativação.
- operador interno: Equipe de marketing/eventos.
- quem aprova ou patrocina: nao_definido

## 4. Jobs to be Done

- job principal: Escanear QR de uma ativação, validar identidade (CPF) e completar o formulário de lead, com reconhecimento automático em ativações subsequentes do mesmo evento.
- jobs secundarios: Configurar ativações com QR, definir se permite conversão única ou múltipla; registrar conversão de terceiro quando o celular é usado por outra pessoa.
- tarefa atual que sera substituida: Fluxo único de formulário sem vínculo com ativações nem reconhecimento de leads.

## 5. Fluxo Principal Desejado

1. Operador cria ativações para o evento; cada ativação gera um QR-code único.
2. Visitante escaneia QR da ativação → é direcionado à landing page.
3. **Primeiro acesso (não reconhecido):** vê apenas o campo CPF. Preenche CPF → validação do dígito verificador.
4. Se CPF válido → exibe o restante dos campos do formulário de lead configurado; preenche e submete → conversão registrada na ativação.
5. **Acesso subsequente (mesmo lead, outra ativação no mesmo evento):** sistema reconhece o lead (ex.: por cookie/session/token) → não exige CPF novamente; exibe diretamente o formulário completo ou confirmação de conversão conforme regra da ativação.
6. Cada escaneada com CPF válido registra uma conversão na ativação correspondente.
7. **Ativação com conversão única:** se o lead já converteu nessa ativação → oferece opção "Registrar outro CPF" (caso use o celular para converter outra pessoa).
8. **Barreira:** se a pessoa tentar cadastrar para outro mas informar o próprio CPF novamente em ativação de conversão única → sistema barra (CPF já convertido nessa ativação).

## 6. Escopo Inicial

### Dentro

- Modelo de dados: Ativação (vínculo com evento, QR único, flag conversão única/múltipla).
- Geração de QR por ativação.
- Fluxo CPF-first: landing exibe apenas CPF no primeiro acesso; validação de dígito verificador.
- Reconhecimento de lead entre ativações do mesmo evento (cookie/session/token).
- Registro de conversão por ativação.
- Opção "Registrar outro CPF" em ativação de conversão única quando o lead já converteu.
- Bloqueio de CPF duplicado em ativação de conversão única.

### Fora

- Validação de CPF contra base externa (Receita Federal); apenas validação algorítmica do dígito verificador.
- Integração com sistemas de impressão de QR (fora de escopo inicial).
- Alteração do modelo de eventos além do necessário para ativações.

## 7. Resultado de Negocio e Metricas

- objetivo principal: Atribuição de conversões por ativação e experiência fluida para leads recorrentes.
- metricas leading: Número de ativações por evento; conversões por ativação; taxa de reconhecimento de leads.
- metricas lagging: Aumento de conversões atribuíveis; redução de abandono por repetição de CPF.
- criterio minimo para considerar sucesso: (1) Cada ativação tem QR único; (2) Fluxo CPF-first com validação; (3) Lead reconhecido não repete CPF; (4) Conversões registradas por ativação; (5) Ativação única/múltipla funcionando; (6) Bloqueio de CPF duplicado em ativação única.

## 8. Restricoes e Guardrails

- restricoes tecnicas: Validação de CPF apenas por dígito verificador (algoritmo); mecanismo de reconhecimento deve respeitar privacidade e LGPD.
- restricoes operacionais: nao_definido
- restricoes legais ou compliance: CPF é dado sensível (LGPD); armazenamento e tratamento conforme política de dados.
- restricoes de prazo: nao_definido
- restricoes de design ou marca: nao_definido

## 9. Dependencias e Integracoes

- sistemas internos impactados: eventos, formulario-lead, leads; possivelmente novo módulo de ativações.
- sistemas externos impactados: nenhum
- dados de entrada necessarios: evento_id, ativação_id (via QR/URL), CPF, demais campos do formulário de lead.
- dados de saida esperados: Conversões por ativação; lead reconhecido entre ativações; bloqueio de CPF duplicado quando aplicável.

## 10. Arquitetura Afetada

- backend: Novo modelo Ativacao; endpoints para QR, validação CPF, reconhecimento de lead, registro de conversão; possíveis migrações.
- frontend: Landing page com fluxo CPF-first; lógica de exibição condicional (CPF vs. formulário completo); opção "Registrar outro CPF"; tratamento de bloqueio.
- banco/migracoes: Tabela ativacoes; possivelmente tabela de conversões por ativação; índices para lookup por CPF+ativação.
- observabilidade: nao_definido
- autorizacao/autenticacao: Landing pública para preenchimento; possível token/session para reconhecimento.
- rollout: Deploy fullstack; migração de dados se necessário.

## 11. Riscos Relevantes

- risco de produto: Mecanismo de reconhecimento (cookie/session) pode falhar em cenários cross-device ou privacidade.
- risco tecnico: Validação apenas por dígito verificador permite CPFs válidos mas inexistentes.
- risco operacional: nao_definido
- risco de dados: CPF é dado sensível; garantir conformidade LGPD.
- risco de adocao: Fluxo CPF-first pode aumentar fricção no primeiro acesso; mitigar com UX clara.

## 12. Nao-Objetivos

- Validação de CPF contra base da Receita Federal.
- Suporte a múltiplos eventos no mesmo fluxo de reconhecimento (escopo inicial: mesmo evento).
- Redesenho completo do formulário de leads além do fluxo CPF-first.

## 13. Contexto Especifico para Problema ou Refatoracao

> nao_aplicavel — intake_kind é new-capability.

## 14. Lacunas Conhecidas

- Mecanismo exato de reconhecimento do lead entre ativações: cookie, session, token na URL, ou combinação — decisão de implementação pendente.
- Persistência do "estado de reconhecido" (por quanto tempo, em qual superfície).
- UX da opção "Registrar outro CPF": onde aparece, copy, fluxo exato.
- Comportamento quando ativação múltipla: lead reconhecido vai direto para formulário ou para confirmação de conversão?
- Definição de "primeiro acesso" vs. "reconhecido": critério técnico (ex.: cookie presente, CPF já convertido em outra ativação do evento).

## 15. Perguntas que o PRD Precisa Responder

- Qual mecanismo de reconhecimento (cookie/session/token) e por quanto tempo?
- Onde e como exibir a opção "Registrar outro CPF" na ativação de conversão única?
- Em ativação múltipla, o lead reconhecido preenche o formulário novamente ou apenas confirma conversão?
- Qual a estrutura de URL do QR (ex.: /eventos/:id/ativacoes/:ativacao_id ou similar)?
- Como garantir que o mesmo dispositivo não seja usado para burlar o bloqueio de CPF duplicado (ex.: limpar cookies)?

## 16. Checklist de Prontidao para PRD

- [x] intake_kind esta definido
- [x] source_mode esta definido
- [x] rastreabilidade de origem esta declarada ou marcada como nao_aplicavel
- [x] problema esta claro
- [x] publico principal esta claro
- [x] fluxo principal esta descrito
- [x] escopo dentro/fora esta fechado
- [x] metricas de sucesso estao declaradas
- [x] restricoes estao declaradas
- [x] dependencias e integracoes estao declaradas
- [x] arquitetura afetada esta mapeada
- [x] riscos relevantes estao declarados
- [x] lacunas conhecidas estao declaradas
- [x] contexto especifico de problema/refatoracao foi preenchido quando aplicavel
