---
doc_id: "EPIC-F3-03-BANNERS-E-ESTADOS-DE-INTERFACE"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-06"
---

# EPIC-F3-03 - Banners e Estados de Interface

## Objetivo

Cobrir os estados de carregamento, vazio, erro, dados parciais e os banners de cobertura BB amarelo/vermelho previstos no PRD, garantindo transparencia operacional na leitura do dashboard.

## Resultado de Negocio Mensuravel

O usuario entende quando o dado esta incompleto, quando nao ha resultado para o filtro e qual acao operacional precisa tomar para completar o cruzamento BB.

## Definition of Done

- A pagina exibe loading com feedback visual antes da resposta da API.
- Existe empty state textual para filtros sem resultado.
- Erros de API mostram mensagem e opcao de retry.
- Banners de cobertura BB seguem a semantica amarela para 20%-80% e vermelha para abaixo de 20%.

## Issues

### DLE-F3-03-001 - Implementar loading, empty state e retry de erro
Status: todo

**User story**
Como pessoa usuaria do dashboard, quero estados claros de carregamento, vazio e erro para saber se devo aguardar, revisar filtros ou tentar novamente.

**Plano TDD**
1. `Red`: usar `frontend/src/test/setup.ts` e o padrao de `frontend/src/components/__tests__/ProtectedRoute.test.tsx` para falhar quando a pagina nao diferenciar loading, erro e ausencia de dados.
2. `Green`: reaproveitar os componentes de `Alert`, `CircularProgress` e botoes vistos em `frontend/src/pages/DashboardLeads.tsx` para exibir os estados previstos.
3. `Refactor`: concentrar o controle de estado assicrono em hooks locais da pagina para evitar condicionais duplicadas no JSX.

**Criterios de aceitacao**
- Given a requisicao em andamento, When a tela renderiza, Then o usuario ve um estado de loading antes do conteudo principal.
- Given resposta com `por_evento=[]` e `base_total=0`, When a tela finaliza o fetch, Then aparece a mensagem "Nenhum lead encontrado para os filtros aplicados".

### DLE-F3-03-002 - Exibir banners de cobertura BB por evento e no consolidado
Status: todo

**User story**
Como pessoa operadora, quero banners claros de cobertura BB para saber quando devo executar o cruzamento com a base do banco antes de interpretar os percentuais.

**Plano TDD**
1. `Red`: adaptar a pagina iniciada a partir de `frontend/src/pages/DashboardLeads.tsx` para falhar enquanto eventos com `cobertura_bb_pct` baixa nao mostrarem aviso proporcional.
2. `Green`: renderizar banner amarelo para cobertura entre 20% e 80% e banner vermelho para cobertura abaixo de 20%, tanto no consolidado quanto no detalhe por evento.
3. `Refactor`: extrair a politica visual de cobertura para um componente dedicado, reduzindo ramificacoes espalhadas na pagina.

**Criterios de aceitacao**
- Given `cobertura_bb_pct=55`, When o evento e exibido, Then aparece um banner amarelo com instrucao para realizar o cruzamento completo.
- Given `cobertura_bb_pct=10`, When o consolidado ou o evento e exibido, Then aparece um banner vermelho informando indisponibilidade de dados de vinculo BB.

### DLE-F3-03-003 - Marcar dados parciais e notas interpretativas
Status: todo

**User story**
Como pessoa usuaria do dashboard, quero notas explicativas sobre dados parciais, media e mediana para interpretar corretamente os indicadores sem depender de treinamento externo.

**Plano TDD**
1. `Red`: usar o setup de `frontend/src/test/setup.ts` para falhar enquanto a tela nao exibir nota de "dados parciais" quando as metricas BB vierem nulas por cobertura insuficiente.
2. `Green`: adicionar tooltips, captions ou helper texts com as definicoes de faixa dominante, media e mediana e a nota de dados parciais.
3. `Refactor`: concentrar os textos explicativos em constantes para reaproveitamento em cards, tabela e futuros dashboards.

**Criterios de aceitacao**
- Given `clientes_bb_pct=NULL` por baixa cobertura, When a metrica e mostrada, Then a interface sinaliza explicitamente que o dado esta parcial ou indisponivel.
- Given o bloco de resumo consolidado, When o usuario inspeciona media e mediana, Then a tela reproduz as definicoes do PRD sem contradizer os valores calculados.

## Artifact Minimo do Epico

- `artifacts/dashboard-leads-etaria/f3/epic-f3-03-banners-e-estados-de-interface.md`

## Dependencias

- [PRD](../PRD_Dashboard_Portfolio.md)
- [SCRUM-GOV](../../COMUM/SCRUM-GOV.md)
- [DECISION-PROTOCOL](../../COMUM/DECISION-PROTOCOL.md)
