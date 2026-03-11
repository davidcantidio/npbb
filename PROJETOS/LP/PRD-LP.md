# PRD - LP
**Correcao do Preview e UX do Formulario de Leads**

| Campo | Valor |
|---|---|
| Produto | LP |
| Versao | 1.0 |
| Data | Marco 2026 |
| Status | draft |
| Tipo | remediacao controlada |
| Origem do Intake | [INTAKE-LP.md](./INTAKE-LP.md) |
| Log de Auditoria | [AUDIT-LOG.md](./AUDIT-LOG.md) |

---

## Historico de Revisoes

| Versao | Descricao |
|---|---|
| 1.0 | Rascunho inicial a partir de `INTAKE-LP.md` |

## 1. Objetivo e Contexto

Este PRD define uma remediacao controlada para a pagina `/eventos/:id/formulario-lead`, com foco em tornar o preview da landing page confiavel, mobile-first e visualmente legivel em todos os `template_overrides` homologados.

Problema a resolver:

- o preview nao reflete em tempo real mudancas de `template_id` feitas no dropdown de tema
- o preview nao reflete em tempo real a selecao de campos do formulario
- o preview atualiza `template_override`, mas ainda apresenta problemas de responsividade e contraste em parte dos templates
- o operador pode salvar uma configuracao sem conseguir validar com fidelidade o resultado final

Resultado esperado:

- preview WYSIWYG confiavel em menos de 500 ms apos mudancas de tema, contexto e campos
- landing e preview legiveis em mobile e desktop, sem scroll horizontal
- thresholds de contraste atendendo WCAG AA para texto nos templates homologados
- mesma configuracao vista no preview antes do save reaparece apos persistencia e recarga

## 2. Escopo

### Dentro

- sincronizacao imediata do preview com `template_id`, `template_override` e campos selecionados
- definicao de uma fonte canonica de estado local para o preview antes do save
- endurecimento mobile-first do preview e da landing associada
- correcao de contraste nos `template_overrides` homologados impactados
- validacao automatizada e manual do fluxo de preview, save e renderizacao responsiva

### Fora

- mudanca do contrato publico atual da API de landing
- novos templates, novos campos de customizacao ou redesign amplo do sistema de templates
- alteracao do fluxo de salvamento para auto-save
- refatoracao estrutural ampla fora do modulo de configuracao e renderizacao de landing

## 3. Decisoes Estruturais

### 3.1 Fonte de verdade do preview

O preview usara como base o payload persistido ja retornado pelo fluxo atual e aplicara, no frontend, um conjunto de overrides locais ainda nao salvos para:

- `template_id`
- `template_override`
- conjunto de campos ativos e obrigatorios

Precedencia obrigatoria:

1. estado local nao salvo
2. payload persistido carregado da API
3. defaults internos ja existentes do renderer

Essa decisao preserva o contrato atual da API e reduz escopo de remediacao.

### 3.2 Relacao entre tema e contexto

- `template_id` passa a ser a fonte de verdade do tema visual
- `template_override` continua representando o contexto da landing
- preview e landing devem aceitar a combinacao de ambos de forma deterministica
- qualquer dependencia oculta entre os dois deve ser resolvida na camada de normalizacao do frontend, sem alterar a API publica nesta versao

### 3.3 Contratos e interfaces

Nao ha mudanca de API publica nesta versao.

Passa a existir internamente um modelo normalizado de preview capaz de representar:

- tema efetivo
- contexto efetivo
- lista de campos visiveis
- flags de obrigatoriedade
- tokens visuais finais necessarios para renderizacao

Esse modelo deve ser o unico insumo da view de preview para evitar divergencia entre controles da tela e renderer.

### 3.4 Mobile-first e contraste

- breakpoint base de desenho: 375 px
- ausencia de scroll horizontal e obrigatoria
- contraste minimo WCAG AA para texto em todos os templates homologados
- quando um template nao atingir contraste com a paleta atual, a correcao deve ocorrer em tokens ou estilos do proprio template, sem abrir novo template

### 3.5 Persistencia e rollback

- o save continua explicito
- apos save com sucesso, a tela deve recarregar a configuracao persistida e comparar implicitamente o resultado com o preview visto antes do save
- como nao ha migracao nem alteracao de contrato externo, rollback operacional e feito por reversao do fluxo de preview local e dos tokens visuais alterados em um deploy unico

## 4. Requisitos Funcionais

- **RF-01**: alterar o dropdown de tema atualiza o preview imediatamente, sem salvar
- **RF-02**: alterar `template_override` continua atualizando o preview imediatamente
- **RF-03**: selecionar ou desmarcar campos atualiza o preview imediatamente, refletindo visibilidade e obrigatoriedade conforme a configuracao local
- **RF-04**: o preview deve refletir exatamente a combinacao atual de tema, contexto e campos exibida no formulario de configuracao
- **RF-05**: apos salvar, a configuracao persistida recarregada deve corresponder ao ultimo estado visualizado no preview
- **RF-06**: landing publica e preview compartilham a mesma logica de composicao visual para evitar drift
- **RF-07**: layouts dos templates homologados devem funcionar em 375 px, 768 px e 1280 px sem quebra estrutural
- **RF-08**: nenhum `template_override` homologado pode permanecer com contraste insuficiente para texto principal
- **RF-09**: em caso de combinacao invalida ou dado incompleto, o preview deve degradar para um estado seguro e legivel, nunca para uma tela quebrada

## 5. Requisitos Nao Funcionais e Validacao

- **RNF-01**: tempo alvo de atualizacao visual do preview menor que 500 ms por interacao local
- **RNF-02**: nenhuma mudanca de contrato publico em `getLandingByEvento` nesta versao
- **RNF-03**: a logica de preview deve ser testavel de forma isolada, sem depender de persistencia para validar tema ou campos
- **RNF-04**: correcoes de contraste devem ser centralizadas para evitar ajustes manuais dispersos por componente
- **RNF-05**: a remediacao deve produzir evidencias suficientes para auditoria funcional e visual da fase

## 6. Arquitetura Afetada

| Camada | Diretriz |
|---|---|
| Configurador de formulario | passa a manter um estado local canonico com tema, contexto e campos |
| Adaptador de preview | normaliza payload persistido + overrides locais em um unico modelo renderizavel |
| Renderer da landing | consome apenas o modelo normalizado, sem buscar estado indireto fora dele |
| Templates/estilos | centralizam tokens de contraste e responsividade por override homologado |
| Backend | permanece compativel e sem mudanca obrigatoria nesta versao |

## 7. Fases Propostas

### F1 - Preview Canonico e Sincronizacao Local

Objetivo: eliminar a divergencia entre controles da tela e preview.

Entregas:

- estado local canonico para tema, contexto e campos
- adaptador interno que combina payload persistido com overrides locais
- preview reagindo sem save para tema, contexto e campos
- cobertura de testes para a composicao do preview

Gate de saida:

- operador altera tema, contexto e campos e ve reflexo imediato no preview
- nao ha dependencia de mudanca de API para validar a experiencia principal

### F2 - Hardening Visual Mobile-First e Contraste

Objetivo: garantir legibilidade e comportamento responsivo consistente.

Entregas:

- auditoria dos `template_overrides` homologados usados no modulo
- correcao de tokens, cores e estilos com foco em WCAG AA
- ajustes de layout mobile-first no preview e na landing renderizada
- validacao em larguras 375 px, 768 px e 1280 px

Gate de saida:

- nenhum template homologado avaliado apresenta contraste insuficiente para texto principal
- nao ha overflow horizontal nem quebra estrutural nos breakpoints definidos

### F3 - Consistencia de Save, Regressao e Prontidao para Auditoria

Objetivo: fechar o ciclo operacional e deixar evidencias auditaveis.

Entregas:

- save seguido de recarga consistente com o ultimo preview exibido
- testes de regressao dos cenarios principais
- checklist de validacao manual com foco em preview, responsividade e contraste
- evidencias consolidadas para a auditoria da fase

Gate de saida:

- o que foi salvo e recarregado corresponde ao que o operador viu antes de confirmar
- suite de validacao cobre fluxo principal e nao regressa cenarios existentes

## 8. Riscos e Mitigacoes

| Risco | Mitigacao |
|---|---|
| divergencia entre estado local e payload persistido | normalizacao unica com precedencia explicita e recarga apos save |
| impacto visual nao intencional em templates existentes | limitar ajuste aos overrides homologados e validar visualmente por breakpoint |
| acoplamento excessivo entre configurador e renderer | introduzir modelo normalizado unico em vez de props dispersas |
| descoberta tardia de dependencia real de backend | tratar como excecao e abrir decisao documentada antes de expandir escopo |

## 9. Criterios de Aceitacao do Projeto

- o preview responde a alteracoes de tema, contexto e campos sem depender de save
- o preview representa a mesma configuracao que sera persistida
- a landing e o preview atendem mobile-first com breakpoints definidos neste PRD
- os templates homologados avaliados atendem contraste minimo WCAG AA para texto
- nao houve mudanca de contrato publico da API de landing
- existe evidencia de teste automatizado e roteiro manual suficiente para auditoria

## 10. Testes e Cenarios Obrigatorios

- teste de composicao do modelo de preview com precedencia `estado local > payload persistido > default`
- teste de UI cobrindo mudanca de tema e atualizacao imediata do preview
- teste de UI cobrindo selecao e desselecao de campos sem save
- teste de integracao cobrindo save seguido de recarga consistente
- validacao responsiva em 375 px, 768 px e 1280 px
- checklist visual de contraste por `template_override` homologado impactado

## 11. Observabilidade, Rollout e Auditoria

- rollout esperado: deploy de frontend, sem migracao
- observabilidade minima: evidencias de teste automatizado e checklist manual anexavel a auditoria
- rollback: reversao do adaptador de preview local e dos ajustes de tokens visuais, sem impacto de schema
- auditoria da fase deve verificar funcionalidade, contraste, responsividade e ausencia de drift entre preview e landing

## 12. Hipoteses Declaradas

1. o contrato atual de `getLandingByEvento` e suficiente como base para o preview, desde que o frontend aplique overrides locais
2. o renderer atual da landing consegue consumir um modelo normalizado sem necessidade de novo endpoint publico
3. os problemas de contraste estao restritos aos templates homologados hoje ativos no modulo e podem ser corrigidos por tokens/estilos
4. nao existe dependencia de negocio para manter comportamento diferente entre preview do backoffice e landing publicada no que diz respeito a tema, contexto e campos
