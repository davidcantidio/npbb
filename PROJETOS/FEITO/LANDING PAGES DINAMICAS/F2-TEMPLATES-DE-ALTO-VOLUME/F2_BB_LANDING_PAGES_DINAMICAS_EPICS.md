# Épicos — BB Landing Pages Dinâmicas / F2 — Templates de Alto Volume
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** BB-LANDING-PAGES-DINAMICAS | **fase:** F2
**prd:** ../PRD-BB-Landing-Pages-Dinamicas.md
**status:** aprovado

---
## Objetivo da Fase
Expandir a cobertura visual do produto com os templates de maior recorrência
operacional no portfólio de eventos BB e habilitar ferramentas de preview e
documentação para os times internos que vão operar a solução.

Ao final da fase, os templates `esporte_convencional`, `evento_cultural` e
`tecnologia` devem estar funcionais, revisáveis no backoffice e acompanhados por
guia operacional para times de ativação e marketing.

## Épicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F2-01 | Template Esporte Convencional | Entregar a experiência esportiva de maior volume com ênfase em energia, orgulho e captação em campo. | F1 concluída | 🔲 | `EPIC-F2-01-TEMPLATE-ESPORTE-CONVENCIONAL.md` |
| EPIC-F2-02 | Template Evento Cultural | Entregar o template editorial para exposições, teatro e agenda CCBB. | EPIC-F2-01 | 🔲 | `EPIC-F2-02-TEMPLATE-EVENTO-CULTURAL.md` |
| EPIC-F2-03 | Template Tecnologia e Inovação | Entregar o template para hackathons, demo days e eventos de comunidade tech. | EPIC-F2-02 | 🔲 | `EPIC-F2-03-TEMPLATE-TECNOLOGIA-E-INOVACAO.md` |
| EPIC-F2-04 | Painel de Preview no Backoffice | Permitir visualização prévia do template resolvido antes do uso da landing na ativação. | EPIC-F2-03 | 🔲 | `EPIC-F2-04-PAINEL-DE-PREVIEW-NO-BACKOFFICE.md` |
| EPIC-F2-05 | Documentação Operacional para Marketing | Formalizar uso, limites e checklist operacional para equipes de eventos e marketing. | EPIC-F2-04 | 🔲 | `EPIC-F2-05-DOCUMENTACAO-OPERACIONAL-PARA-MARKETING.md` |

## Dependências entre Épicos
`EPIC-F2-01` -> `EPIC-F2-02` -> `EPIC-F2-03` -> `EPIC-F2-04` -> `EPIC-F2-05`

## Definition of Done da Fase
- [ ] Templates `esporte_convencional`, `evento_cultural` e `tecnologia` aprovados funcional e visualmente
- [ ] Painel de preview carrega configuração real por evento
- [ ] Equipes internas conseguem validar CTA, hero, cores e conteúdo antes do uso em campo
- [ ] Guia operacional cobre cadastro, override, preview e checklist de ativação

## Notas e Restrições
- Não incluir editor visual livre nesta fase
- Preview deve refletir o mesmo contrato usado pela landing final
- Cada template precisa reutilizar os componentes base da F1
