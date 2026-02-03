# Roadmap Consolidado (Dashboard + Import Batch)

Este documento lista **apenas o que falta implementar**, organizado por milestone -> sprint -> issues.

---

## Milestone: Implementacao de Bulk Insert/Upsert

### Sprint: Compatibilidade CSV/XLSX
- **Issue 1 - Teste cross-format**  
  Descricao: Mesmo arquivo em CSV e XLSX.  
  Entregaveis: Teste de equivalencia.  
  Criterios: Resultados iguais.

---

## Milestone: Observabilidade e Resumo de Importacao

### Sprint: Metricas e logs
- **Issue 1 - Log por lote**  
  Descricao: Registrar tempo e contagem por batch.  
  Entregaveis: Log com batch_id, created/updated/skipped.  
  Criterios: Rastreio minimo.

### Sprint: Relatorio final da importacao
- **Issue 2 - Persistir historico do import**  
  Descricao: (Opcional) registrar import em tabela/log.  
  Entregaveis: Registro com usuario, data, totals.  
  Criterios: Historico consultavel.

- **Issue 3 - Retorno amigavel para UI**  
  Descricao: Mensagens legiveis.  
  Entregaveis: Texto final (ex.: "Importacao concluida com X erros").  
  Criterios: UX clara.

---

## Milestone: Performance e Ajustes Finais

### Sprint: Otimizacao de queries e indices
- **Issue 1 - Indice para dedupe**  
  Descricao: Garantir indice eficiente para chave de dedupe.  
  Entregaveis: Indice em (email, cpf, evento_nome, sessao).  
  Criterios: Upsert mais rapido.

- **Issue 2 - Indices para filtros comuns**  
  Descricao: Adicionar indices usados por import.  
  Entregaveis: Indices em data_compra, estado, cidade, fonte_origem.  
  Criterios: Consultas mais rapidas.

- **Issue 3 - Plano de queries**  
  Descricao: Revisar planos de execucao.  
  Entregaveis: Log/nota de EXPLAIN para queries principais.  
  Criterios: Sem full scan desnecessario.

- **Issue 4 - Documentar indices**  
  Descricao: Atualizar docs tecnicas.  
  Entregaveis: Lista de indices e motivo.  
  Criterios: Documentacao clara.

### Sprint: Controle de memoria e streaming
- **Issue 1 - Log de uso de memoria (opcional)**  
  Descricao: Registrar consumo durante import.  
  Entregaveis: Log simples.  
  Criterios: Diagnostico possivel.

### Sprint: Testes de carga e validacao final
- **Issue 1 - Dataset sintetico grande**  
  Descricao: Criar arquivo de teste com 10k+ linhas.  
  Entregaveis: Fixture CSV/XLSX grande.  
  Criterios: Reprodutivel.

- **Issue 2 - Teste de performance**  
  Descricao: Medir tempo de import.  
  Entregaveis: Benchmark simples.  
  Criterios: Tempo abaixo do limite definido.

- **Issue 3 - Teste de stress de memoria**  
  Descricao: Validar consumo de memoria.  
  Entregaveis: Log de memoria.  
  Criterios: Sem OOM.

- **Issue 4 - Checklist final de validacao**  
  Descricao: Lista final de QA.  
  Entregaveis: Checklist completo.  
  Criterios: Aprovado antes de release.

---

## Milestone: Dashboard (Dados & API & UI & Export)

### Sprint: KPIs e Big Numbers
- **Issue 1 - Definir KPIs do dashboard**  
  Descricao: Formalizar o conjunto de KPIs do MVP.  
  Entregaveis: Publico total, leads unicos, conversoes compra/acao, interacoes.  
  Criterios: Lista documentada e aprovada no PRD.

- **Issue 2 - Query publico total**  
  Descricao: Somar ingresso_qtd por evento.  
  Entregaveis: Funcao publico_total.  
  Criterios: Soma correta.

- **Issue 3 - Query leads unicos**  
  Descricao: Distinct por email/CPF.  
  Entregaveis: Funcao leads_unicos.  
  Criterios: Sem duplicidade.

- **Issue 4 - Conversoes compra**  
  Descricao: Contar LeadConversao COMPRA_INGRESSO.  
  Entregaveis: Funcao conversoes_compra.  
  Criterios: Filtra por evento/periodo.

- **Issue 5 - Conversoes acao**  
  Descricao: Contar LeadConversao ACAO_EVENTO.  
  Entregaveis: Funcao conversoes_acao.  
  Criterios: Filtra por evento/periodo.

- **Issue 6 - Interacoes**  
  Descricao: Contar AtivacaoLead por evento.  
  Entregaveis: Funcao interacoes_total.  
  Criterios: Filtra por evento/periodo.

- **Issue 7 - Agregacao KPIs**  
  Descricao: Consolidar metricas em payload unico.  
  Entregaveis: Objeto kpis_dashboard.  
  Criterios: Payload completo.

- **Issue 8 - Teste KPIs**  
  Descricao: Cobrir metricas com seed minimo.  
  Entregaveis: Teste unitario.  
  Criterios: Testes passam.

### Sprint: Perfil do Publico
- **Issue 1 - Buckets de idade**  
  Descricao: Fixar faixas etarias.  
  Entregaveis: Lista de buckets.  
  Criterios: Documentado.

- **Issue 2 - Calculo de idade**  
  Descricao: Funcao idade_atual.  
  Entregaveis: Util implementado.  
  Criterios: Ignora sem data.

- **Issue 3 - Distribuicao por faixa**  
  Descricao: Agregar por bucket.  
  Entregaveis: Query perfil_idade.  
  Criterios: Contagens corretas.

- **Issue 4 - Normalizacao de genero**  
  Descricao: M/F/masc/fem.  
  Entregaveis: Funcao normalizar_genero.  
  Criterios: Unknown -> NA.

- **Issue 5 - Distribuicao por genero**  
  Descricao: Agregar genero normalizado.  
  Entregaveis: Query perfil_genero.  
  Criterios: Contagens corretas.

- **Issue 6 - Distribuicao por origem**  
  Descricao: Agregar fonte_origem.  
  Entregaveis: Query perfil_origem.  
  Criterios: Contagens corretas.

- **Issue 7 - Agregacao perfil**  
  Descricao: Consolidar no payload.  
  Entregaveis: Objeto perfil_publico.  
  Criterios: Estrutura consistente.

### Sprint: Compras e Pre-venda
- **Issue 1 - Janela de pre-venda**  
  Descricao: Definir intervalo.  
  Entregaveis: Regra no PRD.  
  Criterios: Documentado.

- **Issue 2 - Serie de compras**  
  Descricao: Agregar compras por dia.  
  Entregaveis: Query compras_por_dia.  
  Criterios: Serie ordenada.

- **Issue 3 - Pre-venda vs geral**  
  Descricao: Classificar periodo.  
  Entregaveis: Funcao is_pre_venda.  
  Criterios: Consistente.

- **Issue 4 - KPIs pre-venda**  
  Descricao: volume + pct.  
  Entregaveis: pre_venda_total, pre_venda_pct.  
  Criterios: Valores corretos.

- **Issue 5 - Tickets por tipo**  
  Descricao: Agregar ingresso_tipo.  
  Entregaveis: Query tickets_por_tipo.  
  Criterios: Contagem correta.

- **Issue 6 - Payload compras/pre-venda**  
  Descricao: Consolidar serie + KPIs.  
  Entregaveis: bloco compras_pre_venda.  
  Criterios: Pronto para graficos.

### Sprint: Geografia e Rankings
- **Issue 1 - Normalizacao cidade/estado**  
  Descricao: Padronizar textos.  
  Entregaveis: Funcoes normalizar_cidade/estado.  
  Criterios: Sem acento/caixa.

- **Issue 2 - Ranking por estado**  
  Descricao: Agregar leads por UF.  
  Entregaveis: Query leads_por_estado.  
  Criterios: Top estados correto.

- **Issue 3 - Ranking por cidade**  
  Descricao: Agregar leads por cidade.  
  Entregaveis: Query leads_por_cidade.  
  Criterios: Top cidades correto.

- **Issue 4 - Ranking por origem**  
  Descricao: Agregar fonte_origem.  
  Entregaveis: Query ranking_origem.  
  Criterios: Ordenado por volume.

- **Issue 5 - Top eventos por conversao**  
  Descricao: Agregar conversoes por evento.  
  Entregaveis: Query top_eventos_conversao.  
  Criterios: Top N correto.

- **Issue 6 - Payload rankings**  
  Descricao: Consolidar rankings no retorno.  
  Entregaveis: bloco rankings.  
  Criterios: Pronto para tabelas.

### Sprint: Contrato e parametros do endpoint
- **Issue 1 - Definir endpoint principal**  
  Descricao: GET /dashboard/leads.  
  Entregaveis: Rota definida no PRD.  
  Criterios: Documentado.

- **Issue 2 - Parametros obrigatorios**  
  Descricao: evento_id obrigatorio.  
  Entregaveis: Regra definida.  
  Criterios: Documentado.

- **Issue 3 - Parametros opcionais**  
  Descricao: data_inicio, data_fim, fonte_origem, sessao, estado, cidade.  
  Entregaveis: Tipos definidos.  
  Criterios: Documentado.

- **Issue 4 - Contrato de resposta**  
  Descricao: Estrutura JSON final.  
  Entregaveis: kpis, perfil, compras_pre_venda, rankings, series.  
  Criterios: Completo no PRD.

- **Issue 5 - Erros padrao**  
  Descricao: Mapear erros/mensagens.  
  Entregaveis: 400 filtros invalidos, 404 evento nao existe.  
  Criterios: Padronizado.

- **Issue 6 - Exemplos de chamada**  
  Descricao: exemplos request/response.  
  Entregaveis: 2 exemplos.  
  Criterios: Claro.

### Sprint: Agregacoes por periodo e filtros
- **Issue 1 - Filtro por periodo (compras)**  
  Descricao: data_inicio/data_fim em Lead.data_compra.  
  Entregaveis: Range aplicado.  
  Criterios: Serie respeita periodo.

- **Issue 2 - Filtro por periodo (conversoes)**  
  Descricao: data_inicio/data_fim em LeadConversao.created_at.  
  Entregaveis: Range aplicado.  
  Criterios: Contagens corretas.

- **Issue 3 - Filtro por evento**  
  Descricao: evento_id em todas agregacoes.  
  Entregaveis: Join/where consistente.  
  Criterios: Sem vazamento.

- **Issue 4 - Filtro por sessao**  
  Descricao: filtrar por sessao.  
  Entregaveis: Where aplicado.  
  Criterios: Segmentacao correta.

- **Issue 5 - Filtro por fonte**  
  Descricao: filtrar por fonte_origem.  
  Entregaveis: Where aplicado.  
  Criterios: Totais coerentes.

- **Issue 6 - Filtro por estado/cidade**  
  Descricao: filtros geograficos.  
  Entregaveis: Normalizacao + where.  
  Criterios: Sem divergencias.

### Sprint: Performance e paginacao
- **Issue 1 - Paginacao rankings**  
  Descricao: skip/limit.  
  Entregaveis: Params no endpoint.  
  Criterios: Rankings paginados.

- **Issue 2 - Limitar top N**  
  Descricao: limit default=10.  
  Entregaveis: Payload leve.  
  Criterios: Resposta leve.

- **Issue 3 - Indices recomendados**  
  Descricao: indices para consultas.  
  Entregaveis: lista em doc.  
  Criterios: Documentado.

- **Issue 4 - Cache leve (opcional)**  
  Descricao: cache in-memory com TTL.  
  Entregaveis: cache por filtros.  
  Criterios: Sem quebra consistencia.

### Sprint: Validacao e seguranca
- **Issue 1 - Validar parametros**  
  Descricao: tipos e formatos.  
  Entregaveis: 400 para invalidos.  
  Criterios: Padronizado.

- **Issue 2 - Permissoes**  
  Descricao: restringir acesso.  
  Entregaveis: 403 para nao autorizados.  
  Criterios: Seguro.

- **Issue 3 - Evento obrigatorio**  
  Descricao: bloquear payload vazio.  
  Entregaveis: 400 sem evento_id.  
  Criterios: Evita consultas pesadas.

- **Issue 4 - Sanitizacao filtros**  
  Descricao: normalizar cidade/estado/sessao.  
  Entregaveis: funcao aplicada.  
  Criterios: Sem inconsistencias.

### Sprint: Layout base + filtros
- **Issue 1 - Rota /dashboard/leads**  
  Descricao: registrar rota e pagina.  
  Entregaveis: componente DashboardLeads.  
  Criterios: Renderiza sem erro.

- **Issue 2 - Header da pagina**  
  Descricao: titulo + subtitulo.  
  Entregaveis: textos.  
  Criterios: Consistente.

- **Issue 3 - Filtro por evento**  
  Descricao: select obrigatorio.  
  Entregaveis: dropdown.  
  Criterios: bloqueia sem evento.

- **Issue 4 - Filtro por periodo**  
  Descricao: data_inicio/data_fim.  
  Entregaveis: datepickers.  
  Criterios: intervalo valido.

- **Issue 5 - Filtros extras**  
  Descricao: sessao, fonte, cidade, estado.  
  Entregaveis: inputs opcionais.  
  Criterios: aplicaveis.

- **Issue 6 - Aplicar/limpar**  
  Descricao: botoes filtro.  
  Entregaveis: aplicar e limpar.  
  Criterios: reset funciona.

### Sprint: Cards de KPIs
- **Issue 1 - Componente KPI card**  
  Descricao: componente reutilizavel.  
  Entregaveis: card com titulo/valor.  
  Criterios: responsivo.

- **Issue 2 - Render KPIs**  
  Descricao: publico, leads, conversoes, interacoes.  
  Entregaveis: grid com 5 cards.  
  Criterios: valores da API.

- **Issue 3 - Loading KPIs**  
  Descricao: skeleton.  
  Entregaveis: placeholder.  
  Criterios: sem flicker.

- **Issue 4 - Estado vazio/erro**  
  Descricao: mensagem clara.  
  Entregaveis: alerta + retry.  
  Criterios: sem mensagens tecnicas.

### Sprint: Graficos principais
- **Issue 1 - Serie temporal compras**  
  Descricao: line chart.  
  Entregaveis: grafico com datas.  
  Criterios: serie ordenada.

- **Issue 2 - Distribuicao genero**  
  Descricao: pizza/barra.  
  Entregaveis: grafico percentuais.  
  Criterios: soma 100%.

- **Issue 3 - Distribuicao idade**  
  Descricao: barras por faixa.  
  Entregaveis: grafico buckets.  
  Criterios: valores coerentes.

- **Issue 4 - Conversoes por tipo**  
  Descricao: comparativo compra x acao.  
  Entregaveis: chart simples.  
  Criterios: totais corretos.

### Sprint: Tabelas e rankings
- **Issue 1 - Top estados**  
  Descricao: tabela por volume.  
  Entregaveis: tabela ordenada.  
  Criterios: desc.

- **Issue 2 - Top cidades**  
  Descricao: tabela por volume.  
  Entregaveis: tabela ordenada.  
  Criterios: desc.

- **Issue 3 - Ranking por origem**  
  Descricao: tabela por fonte.  
  Entregaveis: contagem.  
  Criterios: coerente.

- **Issue 4 - Top ativacoes**  
  Descricao: tabela com interacoes.  
  Entregaveis: ativacao + total.  
  Criterios: desc.

### Sprint: UX e responsividade
- **Issue 1 - Layout responsivo**  
  Descricao: grid em mobile/tablet.  
  Entregaveis: breakpoints.  
  Criterios: sem quebra.

- **Issue 2 - Estados globais**  
  Descricao: loading geral.  
  Entregaveis: skeletons.  
  Criterios: UX consistente.

- **Issue 3 - Mensagens e microcopy**  
  Descricao: textos PT-BR.  
  Entregaveis: labels ajustados.  
  Criterios: sem tecnicismo.

- **Issue 4 - Acessibilidade basica**  
  Descricao: contraste e foco.  
  Entregaveis: ajustes.  
  Criterios: navegavel via teclado.

### Sprint: Template e estrutura do DOCX
- **Issue 1 - Estrutura do relatorio**  
  Descricao: secoes e ordem.  
  Entregaveis: sumario.  
  Criterios: documentado.

- **Issue 2 - Biblioteca DOCX**  
  Descricao: decidir stack.  
  Entregaveis: python-docx (ou equivalente).  
  Criterios: aprovado.

- **Issue 3 - Template base**  
  Descricao: layout basico.  
  Entregaveis: template com placeholders.  
  Criterios: abre no Word.

- **Issue 4 - Estilos padrao**  
  Descricao: titulos/subtitulos/tabelas.  
  Entregaveis: styles aplicados.  
  Criterios: consistencia.

- **Issue 5 - Placeholder graficos**  
  Descricao: areas para imagens.  
  Entregaveis: blocos de imagem.  
  Criterios: espaco adequado.

- **Issue 6 - Checklist compatibilidade**  
  Descricao: validar Word/Docs.  
  Entregaveis: checklist.  
  Criterios: validado.

### Sprint: Geracao de dados e graficos
- **Issue 1 - Exportar KPIs**  
  Descricao: inserir big numbers no DOCX.  
  Entregaveis: bloco KPIs.  
  Criterios: valores corretos.

- **Issue 2 - Grafico compras**  
  Descricao: linha de compras.  
  Entregaveis: PNG inserido.  
  Criterios: legivel.

- **Issue 3 - Grafico genero**  
  Descricao: pizza/barra.  
  Entregaveis: imagem.  
  Criterios: percentuais corretos.

- **Issue 4 - Grafico idade**  
  Descricao: barras por faixa.  
  Entregaveis: imagem.  
  Criterios: buckets corretos.

- **Issue 5 - Tabelas rankings**  
  Descricao: estados/cidades/fontes.  
  Entregaveis: tabelas formatadas.  
  Criterios: desc.

- **Issue 6 - Secao pre-venda**  
  Descricao: resumo pre-venda.  
  Entregaveis: texto/grafico.  
  Criterios: coerente.

- **Issue 7 - Secao interacoes**  
  Descricao: top ativacoes.  
  Entregaveis: tabela + resumo.  
  Criterios: dados corretos.

### Sprint: Download e validacao do arquivo
- **Issue 1 - Endpoint exportacao**  
  Descricao: GET /dashboard/leads/export.  
  Entregaveis: DOCX.  
  Criterios: download ok.

- **Issue 2 - Nome do arquivo**  
  Descricao: padrao relatorio_leads_{evento}_{data}.docx.  
  Entregaveis: nome claro.  
  Criterios: unico.

- **Issue 3 - Validar DOCX**  
  Descricao: verificar integridade.  
  Entregaveis: check basico.  
  Criterios: abre sem erro.

- **Issue 4 - Mensagens de erro**  
  Descricao: erros amigaveis.  
  Entregaveis: feedback UI.  
  Criterios: sem tecnicos.

- **Issue 5 - Log exportacao**  
  Descricao: registrar export.  
  Entregaveis: log simples.  
  Criterios: rastreavel.

