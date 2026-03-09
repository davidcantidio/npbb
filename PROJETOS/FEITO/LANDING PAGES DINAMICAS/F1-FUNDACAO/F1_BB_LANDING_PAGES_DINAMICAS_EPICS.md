# Épicos — BB Landing Pages Dinâmicas / F1 — Fundação
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** BB-LANDING-PAGES-DINAMICAS | **fase:** F1
**prd:** ../PRD-BB-Landing-Pages-Dinamicas.md
**status:** aprovado

---
## Objetivo da Fase
Estabelecer a base funcional e técnica das landing pages dinâmicas de captação usadas
em ativações presenciais do Banco do Brasil dentro dos eventos: contrato de dados,
resolução de categoria/template, experiência base da página e guard-rails mínimos de
marca, acessibilidade e performance.

Ao final da fase, o sistema já deve conseguir renderizar uma landing page de ativação
com os templates `generico` e `corporativo`, usando dados reais do backend e
respeitando os invariantes de marca BB definidos no PRD para captação de leads no
local do evento.

## Épicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F1-01 | Modelo de Dados e Contratos de API | Estender o domínio de eventos e expor os contratos mínimos para landing e template-config. | nenhuma | 🔲 | `EPIC-F1-01-MODELO-DE-DADOS-E-CONTRATOS-DE-API.md` |
| EPIC-F1-02 | Resolução de Template e Tokens Visuais | Implementar a engine de categorização e o registro central de tokens por template. | EPIC-F1-01 | 🔲 | `EPIC-F1-02-RESOLUCAO-DE-TEMPLATE-E-TOKENS-VISUAIS.md` |
| EPIC-F1-03 | Experiência Base e Templates Iniciais | Entregar a página de landing com orquestração frontend, template genérico e template corporativo. | EPIC-F1-02 | 🔲 | `EPIC-F1-03-EXPERIENCIA-BASE-E-TEMPLATES-INICIAIS.md` |
| EPIC-F1-04 | Qualidade Base e Conformidade BB | Garantir acessibilidade, LGPD, performance inicial e checklist de marca no template base. | EPIC-F1-03 | 🔲 | `EPIC-F1-04-QUALIDADE-BASE-E-CONFORMIDADE-BB.md` |
| EPIC-F1-05 | QR Code e Acesso via Promotor | Gerar QR codes por ativação e prever alternativa para quem não lê QR (acesso via promotor). | EPIC-F1-01 | 🔲 | `EPIC-F1-05-QR-CODE-E-ACESSO-VIA-PROMOTOR.md` |

## Dependências entre Épicos
`EPIC-F1-01` -> `EPIC-F1-02` -> `EPIC-F1-03` -> `EPIC-F1-04`
`EPIC-F1-01` -> `EPIC-F1-05` (paralelo a F1-02)

## Definition of Done da Fase
- [ ] Modelo de dados do evento e ativação estendidos com os campos previstos no PRD
- [ ] Landing vinculada à ativação; lead associado via AtivacaoLead
- [ ] `GET /ativacoes/{id}/landing` e `GET /eventos/{id}/landing` (fallback) definidos e testados
- [ ] Engine de resolução cobre override, subtipo, tipo, keywords e fallback
- [ ] Landing page renderiza com template `generico` e `corporativo`
- [ ] Formulário envia lead com `event_id` e `ativacao_id` (quando em contexto de ativação) e apresenta tela de sucesso contextual
- [ ] Baseline de acessibilidade, LGPD e performance documentada e validada
- [ ] QR code gerado por ativação; URL alternativa (via promotor) disponível

## Notas e Restrições
- Não introduzir CMS ou editor visual nesta fase
- Aprovação visual de marca BB é gate obrigatório para encerrar a fase
- SSR/SSG pode ser entregue como estratégia implementada ou decisão técnica aprovada,
  desde que o caminho adotado fique explícito nos artefatos da fase
