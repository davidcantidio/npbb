# Plano de Render (Relatorio Word a partir do Banco)

Objetivo: descrever como gerar o relatorio Word automaticamente a partir do banco, usando o template como contrato e garantindo que cada numero exibido tenha linhagem (fonte + local + evidencia).

## Estrutura do template (placeholders por secao)

Estrategia sugerida:

- Manter um template DOCX com marcadores estaveis por secao, por exemplo:
  - `{{section.contexto.text}}`
  - `{{table.controle_acesso_por_sessao}}`
  - `{{figure.presencas_por_sessao}}`
- Para cada marcador, existir uma query/view correspondente em `mart_report_*`.

Implementacao:

- Gerador em Python usando biblioteca de manipulacao de DOCX (ex.: `python-docx` ou `docxtpl`).
- Pipeline de render:
  - Carregar dados (views) do banco.
  - Montar objetos "layout-ready" (strings curtas, listas, tabelas).
  - Inserir tabelas e figuras (imagens geradas).
  - Incluir bloco de "metodologia/definicoes" padrao.

## Queries/Views por secao

- Contexto do evento:
  - View: `mart_report_event_context`
  - Campos: nome do evento, localidade, periodo, descricao curta.
- Fontes e limitacoes:
  - View: `mart_report_sources` + `mart_report_assumptions`
  - Campos: lista de fontes, limitacoes, recortes.
- Big numbers:
  - View: `mart_report_big_numbers`
  - Campos: highlights com metrica explicitada (entradas, opt-in, vendas, leads, imprensa, redes).
- Controle de acesso (entradas validadas):
  - View: `mart_report_attendance_by_session`
  - Tabelas: resumo por sessao (validos, presentes, ausentes, comparecimento).
- Pre-venda e opt-in:
  - Views: `mart_report_presale_curves`, `mart_report_presale_ops`
  - Campos: serie diaria, acumulado, achados e indicadores operacionais.
- Relacionamento BB (proxy):
  - View: `mart_report_bb_share`
  - Campos: distribuicao por segmento e share BB por sessao e agregado.
- Perfil e percepcao (DIMAC):
  - Views: `mart_report_audience_profile`, `mart_report_satisfaction`
  - Campos: distribuicoes e percentuais por pergunta/opcao.
- Redes e social listening:
  - View: `mart_report_social_summary`
  - Campos: metricas por plataforma, insights e comparativos do proprio material.
- Midia e imprensa:
  - View: `mart_report_press_summary`
  - Campos: distribuicao por canal, releases, insercoes, entrevistas, equivalencia.
- Leads e ativacoes:
  - Views: `mart_report_leads_by_day`, `mart_report_activation_rank`, `mart_report_leads_summary`
  - Campos: leads unicos, participacoes, ranking de ativacoes, aprendizados.
- Recomendacoes:
  - View: `mart_report_recommendations`
  - Campos: lista priorizada, com tags (alto impacto, baixo atrito).
- Apendice (definicoes):
  - View: `mart_report_glossary`
  - Campos: definicoes curtas e consistentes.

## Lista de figuras (o que gerar e de onde vem)

- Presencas por sessao (controle de acesso):
  - Fonte: `mart_report_attendance_by_session`
  - Grafico: barras por sessao (presentes).
- Comparecimento por sessao:
  - Fonte: `mart_report_attendance_by_session`
  - Grafico: barras/linha com comparecimento.
- Serie diaria de opt-in (por sessao de show):
  - Fonte: `mart_report_presale_curves`
  - Grafico: linha por dia (quantidade).
- Curva acumulada de opt-in:
  - Fonte: `mart_report_presale_curves`
  - Grafico: linha acumulada (percentual).
- Segmentos (proxy relacionamento):
  - Fonte: `mart_report_bb_share`
  - Grafico: pizza/barras empilhadas por segmento.
- Perfil (idade/genero):
  - Fonte: `mart_report_audience_profile`
  - Grafico: distribuicoes.
- Satisfacao e percepcao:
  - Fonte: `mart_report_satisfaction`
  - Grafico: barras por opcao de resposta.
- Redes:
  - Fonte: `mart_report_social_summary`
  - Grafico: cards de metricas e serie (quando existir).
- Imprensa:
  - Fonte: `mart_report_press_summary`
  - Grafico: distribuicao por canal.
- Leads:
  - Fonte: `mart_report_leads_by_day`
  - Grafico: barras por dia.
- Top ativacoes:
  - Fonte: `mart_report_activation_rank`
  - Grafico: barras horizontais.

## Conteudo "layout-ready"

Para evitar texto longo e "automatico demais", padronizar saidas por secao:

- Highlights:
  - Lista curta de achados, cada um com metrica explicitada (qual regua de publico).
- Aprendizados:
  - O que funcionou e o que nao funcionou, amarrado a dados.
- Recomendacoes:
  - Acao -> por que -> como medir -> dependencia.
- Notas metodologicas:
  - Recortes, amostra, e limitacoes (especialmente quando nao houver dedupe).

## Onde o template atual esta incompleto (e como corrigir na proxima versao)

- Shows por dia:
  - Incluir uma secao/mini-tabela "cobertura por dia de show" com status por dia (OK/GAP/INCONSISTENTE).
  - Regra: se nao existir controle de acesso do show para um dia, o relatorio precisa registrar o GAP explicitamente e listar o que falta pedir.
- Regua de publico:
  - Inserir bloco padrao com definicoes e reconciliacao entre metricas (entradas validadas, vendidos total, opt-in, publico unico quando houver).
- Linhagem:
  - Para cada figura/tabela, incluir referencia de fonte (arquivo + pagina/slide/aba) embutida no rodape interno do relatorio (nao necessariamente visivel ao leitor final, mas exportavel).

