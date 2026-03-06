# Protocolo de Decisões — Landing Pages Dinâmicas

**projeto:** BB-LANDING-PAGES-DINAMICAS | **version:** 1.0.0

---

## DECISÃO-LPD-001 — Landing vinculada à Ativação

**Data:** 2026-03-06  
**Status:** aprovada  
**Contexto:** O PRD e as primeiras versões dos épicos tratavam a landing como vinculada apenas ao evento. O modelo de dados do NPBB já possui `Ativacao` e `AtivacaoLead`; a captação de leads ocorre em pontos de ativação dentro do evento (stands, promotores, totens). O participante já está no evento; a landing serve para captar o lead naquele ponto de contato.

**Decisão:** A landing page de captação é uma **ação de ativação**. A URL preferencial é `/landing/ativacoes/{ativacao_id}`. O endpoint `/landing/eventos/{evento_id}` permanece como fallback para compatibilidade. O lead captado é associado à ativação via `AtivacaoLead`. O evento fornece o contexto (template, categoria).

**Alternativas consideradas:**
- Manter apenas por evento: rejeitada porque não reflete o modelo real de captação em campo.
- Apenas por ativação, sem fallback: rejeitada para preservar compatibilidade e cenários com uma única ativação implícita.

**Consequências:** Endpoints e frontend devem suportar ambos os parâmetros. O payload de landing inclui `ativacao_id` quando aplicável. O submit de lead deve incluir `ativacao_id` e persistir via AtivacaoLead.

---

## DECISÃO-LPD-002 — QR Code e Acesso via Promotor

**Data:** 2026-03-06  
**Status:** aprovada  
**Contexto:** Cada ativação precisa de forma fácil de acesso: QR code para quem consegue escanear e alternativa para quem não consegue ler QR code (ex.: promotor digita/compartilha o link).

**Decisão:** O projeto prevê (1) geração de QR code por ativação, apontando para a URL da landing; (2) URL alternativa (`url_promotor`) para acesso via promotor — digitação ou compartilhamento. O backoffice exibe ambos para o operador.

**Alternativas consideradas:**
- Apenas QR code: rejeitada por questões de acessibilidade e inclusão.
- Short link obrigatório: pode ser fase futura; na F1, usar a própria `landing_url` como alternativa se short link não for viável.

**Consequências:** Ativação ganha campos `landing_url`, `qr_code_url` e `url_promotor`. EPIC-F1-05 cobre o serviço de geração de QR e a exposição no backoffice.

---

*Aprovado por: Produto / Engenharia*
