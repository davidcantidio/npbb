# EPIC-F1-01 — Modelo de Dados e Contratos de API
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** BB-LANDING-PAGES-DINAMICAS | **fase:** F1 | **status:** 🔲

---
## 1. Resumo do Épico
Preparar o backend para servir as landing pages dinâmicas com base em **ativação** (ponto
de captação dentro do evento), metadados de evento, configuração visual e conteúdo mínimo.

**Conceito central:** A landing está vinculada à **Ativação**, não apenas ao Evento. O lead
captado é associado à ativação via `AtivacaoLead`. O evento fornece o contexto (template,
categoria) e a ativação identifica o ponto de captação.

## 2. Contexto Arquitetural
- Backend atual em FastAPI com modelos SQLModel
- Modelo existente: `Ativacao` (evento_id), `AtivacaoLead` (lead ↔ ativação)
- O PRD define endpoints por ativação e extensões em evento/ativação
- O `POST /leads/` deve aceitar `ativacao_id` e persistir via AtivacaoLead
- O contrato precisa suportar uso futuro por múltiplos templates sem duplicação

## 3. Riscos e Armadilhas
- Acoplamento excessivo entre payload de landing e estrutura interna do banco
- Campos opcionais mal definidos podem quebrar o fallback `generico`
- Divergência entre dados persistidos e o que o frontend espera renderizar

## 4. Definition of Done do Épico
- [ ] Modelo de evento contempla os campos novos do PRD
- [ ] Endpoint de landing retorna evento, template, formulário e marca
- [ ] Endpoint de template-config retorna configuração visual reutilizável
- [ ] Testes de contrato garantem shape estável das respostas

---
## Issues

### LPD-F1-01-001 — Estender modelo de Evento para landing pages
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Adicionar ao domínio de eventos os campos necessários para categorização, override,
hero e customização mínima do CTA, conforme seção 5.3 do PRD.

**Critérios de Aceitação:**
- [ ] Evento possui `tipo_evento`, `subtipo_evento`, `template_override`, `hero_image_url`, `cta_personalizado` e `descricao_curta`
- [ ] Campos novos possuem validação coerente com o uso previsto no PRD
- [ ] Persistência e serialização não quebram fluxos existentes de eventos

**Tarefas:**
- [ ] T1: Atualizar model/schema de evento com os novos campos
- [ ] T2: Criar migration para os campos adicionados
- [ ] T3: Ajustar serializers/schemas de leitura e escrita do evento
- [ ] T4: Cobrir criação/edição/leitura de evento com testes backend

**Notas técnicas:**
Priorizar compatibilidade retroativa: eventos antigos sem novos campos devem continuar
válidos e cair no fluxo de fallback.

---
### LPD-F1-01-002 — Implementar `GET /ativacoes/{id}/landing` e fallback `GET /eventos/{id}/landing`
**tipo:** feature | **sp:** 5 | **prioridade:** alta | **status:** 🔲
**depende de:** LPD-F1-01-001

**Descrição:**
Criar endpoint por **ativação** que consolida dados da ativação, evento, configuração
visual resolvida, formulário e metadados de marca. Manter fallback por evento para
compatibilidade.

**Critérios de Aceitação:**
- [ ] `GET /ativacoes/{id}/landing` retorna payload com `ativacao_id`, `evento` e template
- [ ] `GET /eventos/{id}/landing` mantido como fallback (sem ativação específica)
- [ ] `categoria`, `tema` e `cta_text` já vêm resolvidos no payload
- [ ] Resposta inclui `event_id` e `ativacao_id` utilizáveis no submit de leads

**Tarefas:**
- [ ] T1: Criar schema de resposta da landing page
- [ ] T2: Integrar serviço de resolução de template ao endpoint
- [ ] T3: Montar bloco `formulario` com campos obrigatórios/opcionais e mensagem de sucesso
- [ ] T4: Montar bloco `marca` com tagline, versão de logo e hero image
- [ ] T5: Escrever testes de contrato com cenários padrão, override e fallback

**Notas técnicas:**
O endpoint deve ser orientado a consumo frontend; evitar expor detalhes internos que
não são usados na renderização da página.

---
### LPD-F1-01-003 — Implementar `GET /ativacoes/{id}/template-config` e `GET /eventos/{id}/template-config`
**tipo:** feature | **sp:** 2 | **prioridade:** média | **status:** 🔲
**depende de:** LPD-F1-01-002

**Descrição:**
Disponibilizar endpoint enxuto para preview e depuração do tema visual, por ativação
ou evento, sem carregar todo o payload da landing.

**Critérios de Aceitação:**
- [ ] Endpoint por ativação e fallback por evento retornam configuração visual
- [ ] Resposta reutiliza a mesma fonte de verdade do endpoint principal
- [ ] Testes garantem consistência entre `template-config` e `landing`

**Tarefas:**
- [ ] T1: Criar schema enxuto de configuração visual
- [ ] T2: Implementar rotas por ativação e evento
- [ ] T3: Adicionar testes de consistência com o endpoint de landing

**Notas técnicas:**
Este endpoint será consumido pelo painel de preview planejado para a F2.

---
### LPD-F1-01-004 — Estender Ativação com `landing_url`, `qr_code_url` e `url_promotor`
**tipo:** feature | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** LPD-F1-01-002

**Descrição:**
Adicionar à entidade Ativação os campos necessários para URL da landing, geração de
QR code e alternativa de acesso via promotor (para quem não consegue ler QR).

**Critérios de Aceitação:**
- [ ] Ativação possui `landing_url` (URL pública da landing), `qr_code_url` (imagem do QR) e `url_promotor` (URL curta/alternativa)
- [ ] `landing_url` é gerada automaticamente ao criar/atualizar ativação
- [ ] Migration aplicável sem quebrar ativações existentes

**Tarefas:**
- [ ] T1: Adicionar campos ao model Ativacao
- [ ] T2: Criar migration
- [ ] T3: Ajustar schemas e serialização
- [ ] T4: Garantir que submit de lead persiste AtivacaoLead com ativacao_id

**Notas técnicas:**
O `url_promotor` pode ser igual à `landing_url` inicialmente; futuramente pode ser uma
URL curta ou página "landing-sem-qr" que redireciona.

## 5. Notas de Implementação Globais
- Manter o contrato estável e versionável; mudanças futuras de payload devem virar
  nova issue/decisão, não ajuste silencioso
- Todos os defaults visuais devem ser derivados do registro central de templates
