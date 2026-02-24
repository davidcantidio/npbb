# Backlog (Epicos)

Este backlog descreve os epicos para implementar o fluxo completo: fontes -> ETL -> banco -> Word, usando o DOCX como contrato e eliminando lacunas (especialmente shows por dia).

## Epico: DOCX como Spec de Dados

- Objetivo:
  - Tratar o documento modelo como "contrato de dados" versionado, com checklist de secoes/metricas e mapeamento para schema.
- Escopo:
  - Extrair secoes, figuras e tabelas do DOCX.
  - Manter checklist com status (OK/GAP/INCONSISTENTE).
  - Gerar mapeamento DOCX -> tabelas/campos -> queries do relatorio.
- Fora de escopo:
  - Extracao completa de todas as fontes (fica em epicos de extractors).
- Entregaveis:
  - Checklist "DOCX como spec" atualizado e rastreavel.
  - Mapeamento "DOCX -> schema" e views `mart_report_*` definidas.
- DoD:
  - Cada metrica do DOCX aponta para tabela/campo e regra de calculo.
  - Itens obrigatorios do DOCX com status definido e justificativa.
- Dependencias:
  - Acesso ao DOCX final e feedback consolidado.
- Riscos:
  - Mudancas frequentes no template podem quebrar geracao sem uma camada de compatibilidade.

## Sprints

### Sprint 1 - Checklist do DOCX como contrato
Fonte: npbb/docs/analises/eventos/tamo_junto_2025/planning/06_backlog_epics.md | local: Epico "DOCX como Spec de Dados" | evidencia: numeracao interna de sprint (planejamento)
**Objetivo:** Consolidar o template DOCX como checklist versionado de secoes, figuras e tabelas, servindo como contrato de dados.
**Entregaveis:**
- Checklist estruturado de secoes/metricas/figuras/tabelas com granularidade (evento, dia, sessao).
- Regras de status por item (OK/GAP/INCONSISTENTE) padronizadas e auditaveis.
- Glossario inicial com definicoes de metricas e limitacoes metodologicas do fechamento.
**Criterios de aceite:**
- Toda secao do template DOCX aparece no checklist com expectativa clara de dados.
- Itens obrigatorios do template possuem status e justificativa quando nao estiverem OK.
- O checklist pode ser usado como criterio de pronto para iniciar a carga e os marts.
**Dependencias:**
- Acesso ao DOCX modelo e ao feedback consolidado.

### Sprint 2 - Mapeamento DOCX para schema e marts
Fonte: npbb/docs/analises/eventos/tamo_junto_2025/planning/06_backlog_epics.md | local: Epico "DOCX como Spec de Dados" | evidencia: numeracao interna de sprint (planejamento)
**Objetivo:** Traduzir cada item do checklist do DOCX em campos/tabelas e contratos de views para o relatorio.
**Entregaveis:**
- Matriz de mapeamento "item do DOCX -> tabela.campo -> regra de calculo -> fonte(s) -> validacoes".
- Contratos de marts/views por secao do relatorio (o que cada secao precisa consultar).
- Definicoes de metrica que obrigam separar reguas de publico (entradas validadas, opt-in, vendidos, publico unico quando existir).
**Criterios de aceite:**
- Cada item do checklist aponta para pelo menos um campo/tabela ou view responsavel.
- As definicoes deixam explicito qual metrica de publico esta sendo usada em cada secao.
- Existem validacoes previstas para derivados criticos (percentuais e reconciliacoes).
**Dependencias:**
- Modelo canonico minimo e dimensoes de sessao alinhados (Epico "Normalizacao e Regras de Metrica": Sprint "Catalogo de sessoes e dimensoes").

### Sprint 3 - Spec executavel e governanca do template
Fonte: npbb/docs/analises/eventos/tamo_junto_2025/planning/06_backlog_epics.md | local: Epico "DOCX como Spec de Dados" | evidencia: numeracao interna de sprint (planejamento)
**Objetivo:** Transformar o spec do DOCX em algo testavel, para evitar omissoes e regressao de cobertura entre versoes.
**Entregaveis:**
- Conjunto de checks de completude do spec (itens obrigatorios, nomes padrao, ordem de secoes).
- Politica de versionamento do template e do spec (compatibilidade e mudancas controladas).
- Gate de "pronto para gerar relatorio" baseado no checklist (OK/GAP/INCONSISTENTE).
**Criterios de aceite:**
- Mudancas no template geram diffs claros no spec e exigem revisao de impacto.
- Itens marcados como obrigatorios geram falha quando ausentes no spec.
- O spec vira referencia unica para o que o gerador Word precisa renderizar.
**Dependencias:**
- Registro de fontes e execucoes de ingestao para referenciar linhagem (Epico "Ingestion Registry / Catalogo de fontes": Sprint "Linhagem de metricas").

## Epico: Ingestion Registry / Catalogo de fontes

- Objetivo:
  - Centralizar registro de fontes, execucoes de ingestao e linhagem de metricas.
- Escopo:
  - Criar `sources`, `ingestions` e padrao de `source_id`.
  - Hash de arquivo e versionamento por execucao.
- Fora de escopo:
  - Transformacoes complexas (fica em normalizacao).
- Entregaveis:
  - Tabelas e endpoints internos para consultar ingestao/linhagem.
- DoD:
  - Qualquer carga de dados gera registro de ingestao com status e logs.
- Dependencias:
  - Banco com migrations.
- Riscos:
  - Falta de disciplina operacional gera "dados sem fonte".

## Sprints

### Sprint 1 - Registry de sources e ingestions
Fonte: npbb/docs/analises/eventos/tamo_junto_2025/planning/06_backlog_epics.md | local: Epico "Ingestion Registry / Catalogo de fontes" | evidencia: numeracao interna de sprint (planejamento)
**Objetivo:** Criar a fundacao para rastrear arquivos, versoes e execucoes de ingestao no banco.
**Entregaveis:**
- Tabelas `sources` e `ingestions` com campos minimos para auditoria.
- Utilitario padrao de hash de arquivo e captura de metadados (nome, caminho, tamanho).
- Fluxo de registro de ingestao com status (success, failed, partial) e notas de execucao.
**Criterios de aceite:**
- Cada arquivo ingerido gera um registro unico em `sources` e uma execucao em `ingestions`.
- E possivel listar historico de ingestoes por fonte e identificar a ultima execucao.
- Falhas de ingestao ficam registradas com motivo e sem sobrescrever execucoes anteriores.
**Dependencias:**
- Banco com migrations.

### Sprint 2 - Linhagem de metricas (fonte e localizacao)
Fonte: npbb/docs/analises/eventos/tamo_junto_2025/planning/06_backlog_epics.md | local: Epico "Ingestion Registry / Catalogo de fontes" | evidencia: numeracao interna de sprint (planejamento)
**Objetivo:** Garantir que qualquer metrica carregada consiga apontar para arquivo e local (pagina/slide/aba/range).
**Entregaveis:**
- Estrutura padrao de linhagem (ex.: `location_type`, `location_value`, `evidence_text`) persistida no banco.
- Helpers para registrar linhagem junto com dados extraidos (staging e canonical).
- Convencao de `source_id` e formatos de referencia para PDF/PPTX/XLSX.
**Criterios de aceite:**
- Para metricas extraidas, e possivel consultar `source_id` e localizacao sem ambiguidades.
- O padrao de referencia cobre pagina de PDF, slide de PPTX e aba/range de XLSX.
- Qualquer carga sem linhagem e tratada como falha ou parcial (conforme severidade).
**Dependencias:**
- Sprint "Registry de sources e ingestions".

### Sprint 3 - Catalogo operacional e consultas de auditoria
Fonte: npbb/docs/analises/eventos/tamo_junto_2025/planning/06_backlog_epics.md | local: Epico "Ingestion Registry / Catalogo de fontes" | evidencia: numeracao interna de sprint (planejamento)
**Objetivo:** Expor consultas padrao para saber o que foi ingerido, com que qualidade e para que sessoes.
**Entregaveis:**
- Consultas/views para listar fontes, execucoes, status e cobertura por tipo de dado.
- Relatorio operacional de ingestao (contagens por fonte e por execucao).
- Base para auditoria de gaps: "fonte existe, mas nao foi carregada" vs "fonte nao existe".
**Criterios de aceite:**
- E possivel responder rapidamente quais fontes suportam cada secao do relatorio.
- E possivel identificar ingestoes parciais e suas causas.
- O catalogo vira dependencia padrao de qualquer extractor.
**Dependencias:**
- Sprint "Linhagem de metricas (fonte e localizacao)".

## Epico: Extractors por tipo (PDF/XLSX/PPTX)

- Objetivo:
  - Automatizar extracao de dados de arquivos heterogeneos para staging com minima perda.
- Escopo:
  - XLSX: leitura de abas, headers mesclados, normalizacao inicial.
  - PPTX: extracao por slide e mapeamento slide->metrica.
  - PDF: extracao de tabelas (controle de acesso) e quadros (DIMAC/MTC), com fallback assistido.
- Fora de escopo:
  - Enriquecimento e reconciliacao (fica em canonical/marts).
- Entregaveis:
  - Scripts/servicos `extract_xlsx_*`, `extract_pptx_*`, `extract_pdf_*`.
  - Artefatos staging (`stg_*`) com log de evidencias.
- DoD:
  - Para cada fonte do inventario, existe um extractor executavel que gera staging consistente.
- Dependencias:
  - Bibliotecas e ambiente de execucao; padrao de pastas raw/staging.
- Riscos:
  - PDFs com layout instavel exigem estrategia de resiliencia (spec de extracao por versao).

## Sprints

### Sprint 1 - Extractor XLSX (opt-in e leads)
Fonte: npbb/docs/analises/eventos/tamo_junto_2025/planning/06_backlog_epics.md | local: Epico "Extractors por tipo (PDF/XLSX/PPTX)" | evidencia: numeracao interna de sprint (planejamento)
**Objetivo:** Extrair XLSX para staging/canonical com colunas padronizadas e registro de linhagem.
**Entregaveis:**
- Extractor de XLSX para opt-in (Eventim) com normalizacao de header e campos de compra/sessao.
- Extractor de XLSX para leads e ativacoes com dedupe e normalizacao de CPF/email.
- Registro de linhagem por aba e referencia de colunas/ranges usados na extracao.
**Criterios de aceite:**
- A ingestao dos XLSX gera dados em staging e canonical com chaves consistentes (evento e sessao).
- Campos criticos de compra/sessao/quantidade estao preenchidos quando presentes na fonte.
- Duplicidades evidentes sao detectadas e tratadas conforme regra de dedupe.
**Dependencias:**
- Epico "Ingestion Registry / Catalogo de fontes": Sprint "Registry de sources e ingestions".
- Epico "Ingestion Registry / Catalogo de fontes": Sprint "Linhagem de metricas (fonte e localizacao)".

### Sprint 2 - Extractor PPTX (midias e social listening)
Fonte: npbb/docs/analises/eventos/tamo_junto_2025/planning/06_backlog_epics.md | local: Epico "Extractors por tipo (PDF/XLSX/PPTX)" | evidencia: numeracao interna de sprint (planejamento)
**Objetivo:** Extrair metricas de PPTX por slide, com mapeamento explicito slide -> metrica e evidencia.
**Entregaveis:**
- Parser de PPTX (shapes/textos/tabelas) com fallback via leitura de XML do arquivo.
- Configuracao de mapeamento slide -> metrica (nome, plataforma, periodo, regra de captura).
- Registro de linhagem com slide, titulo e trecho de evidencia associado a cada metrica.
**Criterios de aceite:**
- As metricas extraidas trazem identificacao de plataforma e periodo quando existirem na fonte.
- E possivel rastrear cada numero extraido ate um slide especifico e seu label.
- Mudanca de layout (ex.: texto sumiu ou mudou) gera ingestao parcial com aviso.
**Dependencias:**
- Epico "Ingestion Registry / Catalogo de fontes": Sprint "Linhagem de metricas (fonte e localizacao)".

### Sprint 3 - Extractor PDF (controle de acesso e relatorios)
Fonte: npbb/docs/analises/eventos/tamo_junto_2025/planning/06_backlog_epics.md | local: Epico "Extractors por tipo (PDF/XLSX/PPTX)" | evidencia: numeracao interna de sprint (planejamento)
**Objetivo:** Extrair tabelas e quadros de PDF com estrategia resiliente (automatico quando possivel, assistido quando necessario).
**Entregaveis:**
- Pipeline de extracao de PDF com deteccao de PDF texto vs imagem e estrategia correspondente.
- Extractor para controle de acesso (tabela por sessao) com padronizacao de colunas.
- Modo assistido: especificacao de extracao (marcacao) para casos em que a tabela nao e capturavel automaticamente.
**Criterios de aceite:**
- Para controle de acesso, o pipeline produz uma tabela por sessao com colunas esperadas.
- Cada valor extraido registra pagina e evidencia (titulo/linha) para auditoria.
- Quando nao for possivel extrair, o sistema registra falha/parcial com orientacao objetiva do que faltou.
**Dependencias:**
- Epico "Ingestion Registry / Catalogo de fontes": Sprint "Registry de sources e ingestions".
- Epico "Ingestion Registry / Catalogo de fontes": Sprint "Linhagem de metricas (fonte e localizacao)".

## Epico: Normalizacao e Regras de Metrica

- Objetivo:
  - Padronizar chaves (evento/sessao), dominios e regras para gerar metricas do relatorio.
- Escopo:
  - Catalogo de sessoes (`event_sessions`) e regra de classificacao (diurno gratuito vs noturno show).
  - Mapeamento de segmentos (proxy relacionamento BB) auditavel.
  - Regua de publico: separar entradas validadas, opt-in, vendidos e publico unico.
- Fora de escopo:
  - Visualizacao e layout do Word (fica no gerador).
- Entregaveis:
  - Tabelas canonicas populadas e views `mart_report_*`.
- DoD:
  - Metric definitions documentadas e implementadas em views.
  - Reconciliacoes basicas rodando (somas, percentuais, consistencia).
- Dependencias:
  - Extractors entregando staging.
- Riscos:
  - Ambiguidade de definicoes entre areas gera metricas conflitantes.

## Sprints

### Sprint 1 - Catalogo de sessoes e dimensoes
Fonte: npbb/docs/analises/eventos/tamo_junto_2025/planning/06_backlog_epics.md | local: Epico "Normalizacao e Regras de Metrica" | evidencia: numeracao interna de sprint (planejamento)
**Objetivo:** Criar o catalogo de sessoes do evento e a dimensao minima para sustentar fatos por sessao/dia.
**Entregaveis:**
- Tabela `event_sessions` com tipo de sessao e chaves de data/horario.
- Convencao de nomes de sessao e regra de classificacao (diurno gratuito vs noturno show).
- Ligacao entre sessoes e fontes (qual fonte define existencia e cobertura).
**Criterios de aceite:**
- Todo fato carregado consegue apontar para um `session_id` coerente.
- O tipo de sessao fica consistente e auditavel (nao depende de texto livre na analise).
- E possivel identificar sessoes esperadas versus sessoes com dados carregados.
**Dependencias:**
- Epico "Ingestion Registry / Catalogo de fontes": Sprint "Registry de sources e ingestions".

### Sprint 2 - Regua de publico e mapeamento de segmentos
Fonte: npbb/docs/analises/eventos/tamo_junto_2025/planning/06_backlog_epics.md | local: Epico "Normalizacao e Regras de Metrica" | evidencia: numeracao interna de sprint (planejamento)
**Objetivo:** Padronizar definicoes e regras para metricas de publico e relacionamento BB (proxy por categoria).
**Entregaveis:**
- Definicoes formais de metricas: entradas validadas, opt-in aceitos, vendidos total, publico unico quando houver chave.
- Tabela de mapeamento de categorias de ingresso para segmentos canonicos (cliente/cartao/funcionario/outros).
- Regras de reconciliacao para derivados (comparecimento, shares e percentuais).
**Criterios de aceite:**
- O pipeline nao mistura reguas de publico sem declaracao explicita.
- Segmentos usados no relatorio saem de dominio controlado e mapeamento auditavel.
- Derivados criticos tem validacao de consistencia antes de ir para marts.
**Dependencias:**
- Epico "Extractors por tipo (PDF/XLSX/PPTX)": Sprint "Extractor XLSX (opt-in e leads)".
- Epico "Extractors por tipo (PDF/XLSX/PPTX)": Sprint "Extractor PDF (controle de acesso e relatorios)".

### Sprint 3 - Marts do relatorio (views por secao)
Fonte: npbb/docs/analises/eventos/tamo_junto_2025/planning/06_backlog_epics.md | local: Epico "Normalizacao e Regras de Metrica" | evidencia: numeracao interna de sprint (planejamento)
**Objetivo:** Publicar views/marts que alimentam o Word por secao e reduzem logica no gerador.
**Entregaveis:**
- Views `mart_report_*` para publico por sessao, pre-venda, relacionamento, perfil, redes, imprensa e leads.
- Contratos de saida por secao (campos e ordenacao) alinhados ao spec do DOCX.
- Rotina de validacao de marts (somas, percentuais e consistencia temporal).
**Criterios de aceite:**
- O gerador Word precisa apenas consultar `mart_report_*` para renderizar secoes e figuras.
- Os marts deixam claro qual regua de publico esta sendo usada em cada agregado.
- Inconsistencias basicas bloqueiam a publicacao dos marts (ou geram status parcial).
**Dependencias:**
- Epico "DOCX como Spec de Dados": Sprint "Mapeamento DOCX para schema e marts".
- Epico "Extractors por tipo (PDF/XLSX/PPTX)": Sprint "Extractor PPTX (midias e social listening)".

## Epico: Data Quality + Observabilidade

- Objetivo:
  - Detectar falhas, inconsistencias e mudancas de layout antes de publicar relatorio.
- Escopo:
  - Checks de esquema, nulos criticos, duplicidade, reconciliacao de derivados.
  - Alertas de ingestao parcial e drift de layout.
  - Painel interno de saude de dados por fonte e por sessao.
- Fora de escopo:
  - Monitoramento corporativo completo (integracoes externas).
- Entregaveis:
  - Suite de validacoes + relatorio de qualidade por execucao.
- DoD:
  - Falhas criticas bloqueiam geracao do relatorio.
  - Logs e evidencias acessiveis para auditoria.
- Dependencias:
  - Ingestion registry implementado.
- Riscos:
  - Excesso de checks sem priorizacao pode travar o fluxo; definir severidades.

## Sprints

### Sprint 1 - Framework de checks e relatorio de qualidade
Fonte: npbb/docs/analises/eventos/tamo_junto_2025/planning/06_backlog_epics.md | local: Epico "Data Quality + Observabilidade" | evidencia: numeracao interna de sprint (planejamento)
**Objetivo:** Criar um mecanismo padrao para rodar validacoes e registrar resultados por execucao.
**Entregaveis:**
- Runner de checks com severidade (warn, error) e escopo (staging, canonical, marts).
- Persistencia de resultados de qualidade por `ingestion_id`.
- Checks base: esquema, nulos criticos, duplicidade e tipos de dados.
**Criterios de aceite:**
- E possivel rodar checks em lote e obter um relatorio por execucao de ingestao.
- Falhas criticas bloqueiam a promocao de staging para canonical (ou canonical para marts).
- O relatorio de qualidade referencia fonte e execucao para auditoria.
**Dependencias:**
- Epico "Ingestion Registry / Catalogo de fontes": Sprint "Registry de sources e ingestions".

### Sprint 2 - Reconciliacoes e inconsistencias entre fontes
Fonte: npbb/docs/analises/eventos/tamo_junto_2025/planning/06_backlog_epics.md | local: Epico "Data Quality + Observabilidade" | evidencia: numeracao interna de sprint (planejamento)
**Objetivo:** Implementar validacoes de reconciliacao e detectar inconsistencias numericas entre fontes.
**Entregaveis:**
- Regras de reconciliacao para controle de acesso (validos, presentes, ausentes e comparecimento).
- Regras para percentuais (somas e limites) em survey, redes e imprensa quando aplicavel.
- Identificacao de divergencias entre fontes para a mesma metrica (marcar como INCONSISTENTE).
**Criterios de aceite:**
- Derivados criticos batem com seus numeradores/denominadores quando a fonte permite.
- Diferencas relevantes entre fontes geram registro de inconsistencias com evidencia.
- Os checks conseguem explicar o motivo (campo faltante, layout mudou, regra violada).
**Dependencias:**
- Epico "Normalizacao e Regras de Metrica": Sprint "Regua de publico e mapeamento de segmentos".

### Sprint 3 - Observabilidade e painel de saude
Fonte: npbb/docs/analises/eventos/tamo_junto_2025/planning/06_backlog_epics.md | local: Epico "Data Quality + Observabilidade" | evidencia: numeracao interna de sprint (planejamento)
**Objetivo:** Expor visao operacional do pipeline por fonte/sessao, com alertas de gaps e drift.
**Entregaveis:**
- Consultas/views de saude por fonte (status, ultima execucao, linhas carregadas, falhas).
- Alertas de ingestao parcial e drift de layout para fontes criticas.
- Sumario de cobertura por sessao/dia para apoiar auditoria antes do fechamento.
**Criterios de aceite:**
- E possivel ver rapidamente quais fontes estao incompletas e por que.
- Drift de layout e detectado antes de contaminar canonical/marts.
- O painel suporta a decisao de "publicar" ou "segurar" o relatorio.
**Dependencias:**
- Epico "Extractors por tipo (PDF/XLSX/PPTX)": Sprint "Extractor PDF (controle de acesso e relatorios)".

## Epico: Report Generator (Word) a partir do banco

- Objetivo:
  - Gerar automaticamente o DOCX final a partir das views/marts, preservando o template.
- Escopo:
  - Template DOCX com placeholders por secao e figura.
  - Render de tabelas e graficos a partir de queries.
  - Insercao de notas metodologicas e definicoes padrao.
- Fora de escopo:
  - Edicao manual do texto final (exceto ajustes pontuais).
- Entregaveis:
  - Motor de render e comando de geracao por evento/versao.
- DoD:
  - Relatorio gerado reproduz secoes e ordem do template.
  - Cada numero exibido aponta para linhagem (fonte + local).
- Dependencias:
  - Marts/views prontos.
- Riscos:
  - Mudanca no template quebra placeholders; exigir testes de snapshot do DOCX.

## Sprints

### Sprint 1 - Template e placeholders alinhados ao spec
Fonte: npbb/docs/analises/eventos/tamo_junto_2025/planning/06_backlog_epics.md | local: Epico "Report Generator (Word) a partir do banco" | evidencia: numeracao interna de sprint (planejamento)
**Objetivo:** Definir o template renderizavel e a convencao de placeholders por secao, amarrada ao spec do DOCX.
**Entregaveis:**
- Convencao de placeholders por secao e por bloco (texto, tabela, figura).
- Esqueleto do gerador Word (comando de geracao por evento e versao).
- Render minimo de secoes com dados vindos de uma view/mart (sem formatacao avancada).
**Criterios de aceite:**
- O gerador produz um DOCX com a ordem de secoes do template preservada.
- Cada placeholder do template tem uma origem clara em `mart_report_*`.
- Mudancas no template geram falha clara (placeholder desconhecido) em vez de silenciosa.
**Dependencias:**
- Epico "DOCX como Spec de Dados": Sprint "Checklist do DOCX como contrato".
- Epico "Normalizacao e Regras de Metrica": Sprint "Marts do relatorio (views por secao)".

### Sprint 2 - Render de tabelas e figuras a partir dos marts
Fonte: npbb/docs/analises/eventos/tamo_junto_2025/planning/06_backlog_epics.md | local: Epico "Report Generator (Word) a partir do banco" | evidencia: numeracao interna de sprint (planejamento)
**Objetivo:** Renderizar tabelas e graficos previstos no template usando marts e padroes de layout.
**Entregaveis:**
- Render de tabelas do relatorio (controle de acesso por sessao, leads e ativacoes, etc).
- Geracao de figuras (graficos) com padrao visual e legenda para insercao no DOCX.
- Lista de figuras e mapeamento figura -> query/view -> output.
**Criterios de aceite:**
- As tabelas renderizadas batem com o contrato de colunas e ordenacao definido nos marts.
- As figuras geradas sao reproduziveis (mesmas entradas geram a mesma saida) e possuem legenda.
- O relatorio resultante fica "layout-ready" sem necessidade de edicao estrutural manual.
**Dependencias:**
- Epico "Normalizacao e Regras de Metrica": Sprint "Marts do relatorio (views por secao)".

### Sprint 3 - Linhagem no relatorio e tratamento de GAP
Fonte: npbb/docs/analises/eventos/tamo_junto_2025/planning/06_backlog_epics.md | local: Epico "Report Generator (Word) a partir do banco" | evidencia: numeracao interna de sprint (planejamento)
**Objetivo:** Garantir rastreabilidade e evitar omissoes: cada numero exibido aponta para fonte e local, e gaps aparecem explicitamente.
**Entregaveis:**
- Insercao de referencias de fonte/local por secao/figura (rodape interno, apendice ou metadados).
- Secao padrao de GAP/INCONSISTENTE gerada a partir de checks e auditorias.
- Regras de bloqueio/aviso para publicacao do relatorio quando houver lacunas criticas.
**Criterios de aceite:**
- Todo numero renderizado possui linhagem consultavel (fonte e localizacao).
- Quando a fonte nao existe ou nao foi extraida, o relatorio registra GAP com evidencias.
- O fluxo impede publicar um fechamento com omissoes silenciosas.
**Dependencias:**
- Epico "Ingestion Registry / Catalogo de fontes": Sprint "Linhagem de metricas (fonte e localizacao)".
- Epico "Data Quality + Observabilidade": Sprint "Reconciliacoes e inconsistencias entre fontes".

## Epico: Cobertura de shows por dia

- Objetivo:
  - Evitar repeticao do bug de omissao por dia, garantindo que sessoes de show existam e tenham fontes para cada dia previsto.
- Escopo:
  - Auditoria automatica de cobertura por dia/sessao (show) antes de fechar relatorio.
  - Checklist de fontes minimas por sessao: controle de acesso, vendas total, opt-in (quando aplicavel).
  - Mecanismo de "GAP formal" no relatorio quando a fonte nao existe.
- Fora de escopo:
  - Criar dados ausentes; o foco e detectar e registrar lacunas.
- Entregaveis:
  - View `mart_report_show_day_summary` + alerta de gaps.
  - Secao do relatorio com status por dia (OK/GAP/INCONSISTENTE).
- DoD:
  - Para cada sessao de show prevista, o pipeline sinaliza se ha (ou nao) as fontes necessarias.
- Dependencias:
  - Catalogo de sessoes e sources/ingestions.
- Riscos:
  - Agenda de sessoes sem fonte oficial; exigir "agenda master" como input.

## Sprints

### Sprint 1 - Agenda master e catalogo de shows
Fonte: npbb/docs/analises/eventos/tamo_junto_2025/planning/06_backlog_epics.md | local: Epico "Cobertura de shows por dia" | evidencia: numeracao interna de sprint (planejamento)
**Objetivo:** Formalizar a lista de sessoes esperadas de show por dia, separando diurno gratuito de noturno show.
**Entregaveis:**
- Registro de sessoes esperadas (calendario de show por dia) como input controlado.
- Regras para associar fontes a sessoes (quando a fonte define existencia vs quando apenas cobre dados).
- Contrato de cobertura minima por sessao (controle de acesso, vendas total, opt-in quando aplicavel).
**Criterios de aceite:**
- Existe uma lista unica e versionada de sessoes de show esperadas por dia.
- O pipeline consegue comparar "esperado" vs "observado" e gerar status por sessao.
- A cobertura minima por sessao fica explicita e verificavel.
**Dependencias:**
- Epico "Normalizacao e Regras de Metrica": Sprint "Catalogo de sessoes e dimensoes".

### Sprint 2 - Cobertura de shows por dia (12/12 e 14/12)
Fonte: npbb/docs/analises/eventos/tamo_junto_2025/planning/06_backlog_epics.md | local: Epico "Cobertura de shows por dia" | evidencia: sprint dedicada a lacunas doze e quatorze de dezembro
**Objetivo:** Implementar auditoria automatica focada em identificar e registrar gaps de show nos dias criticos, sem permitir omissao no fechamento.
**Entregaveis:**
- Check de cobertura por dia/sessao para show (OK/GAP/INCONSISTENTE) com evidencias.
- Lista objetiva do que falta pedir para fechar lacunas (qual arquivo, qual sessao, qual metrica).
- View `mart_report_show_day_summary` com status por dia e por tipo de metrica (acesso, vendas, opt-in).
**Criterios de aceite:**
- O sistema sinaliza explicitamente quando falta controle de acesso de show para um dia.
- O sistema sinaliza explicitamente quando falta base de opt-in para um dia de show esperado.
- A saida da auditoria e consumivel pelo gerador do relatorio sem interpretacao manual.
**Dependencias:**
- Epico "Ingestion Registry / Catalogo de fontes": Sprint "Catalogo operacional e consultas de auditoria".
- Epico "Extractors por tipo (PDF/XLSX/PPTX)": Sprint "Extractor PDF (controle de acesso e relatorios)".
- Epico "Extractors por tipo (PDF/XLSX/PPTX)": Sprint "Extractor XLSX (opt-in e leads)".

### Sprint 3 - Integracao no relatorio e gates de publicacao
Fonte: npbb/docs/analises/eventos/tamo_junto_2025/planning/06_backlog_epics.md | local: Epico "Cobertura de shows por dia" | evidencia: numeracao interna de sprint (planejamento)
**Objetivo:** Integrar a cobertura de shows no Word e criar gates que impedem fechar sem declarar gaps.
**Entregaveis:**
- Secao do relatorio "cobertura por dia de show" renderizada a partir do `mart_report_show_day_summary`.
- Regras para incluir automaticamente texto de GAP/INCONSISTENTE quando aplicavel.
- Gate de publicacao para impedir relatorio final com omissoes silenciosas de show.
**Criterios de aceite:**
- O Word sempre inclui o status por dia de show, mesmo quando houver GAP.
- O relatorio deixa explicito o que faltou e qual fonte seria necessaria para completar.
- O pipeline bloqueia ou marca como parcial quando houver lacunas criticas de show.
**Dependencias:**
- Epico "Report Generator (Word) a partir do banco": Sprint "Linhagem no relatorio e tratamento de GAP".

