# Prompt para investigação técnica profunda de inconsistências de datas

## Contexto consolidado

Os artefatos de trabalho são [`LEADS-v4.csv`](sandbox:/mnt/data/LEADS-v4.csv), [`notebook_origem1 1(1).ipynb`](sandbox:/mnt/data/notebook_origem1%201(1).ipynb) e [`notebook-run(1).docx`](sandbox:/mnt/data/notebook-run(1).docx).

Pelos artefatos, já existe um sinal concreto de incompatibilidade entre a forma como as datas chegam e a forma como o notebook as interpreta. O notebook usa `LEAD_DATE_STYLE = "AUTO_SAFE"` e a função de parsing trata datas com barras como ambíguas quando os dois primeiros componentes são menores ou iguais a 12. Na execução registrada, o próprio notebook reporta 57.793 leads de entrada e apenas 44.392 linhas com `data_evento` válida. Ao mesmo tempo, a planilha local expõe datas em formato com barras como `3/25/2026` e `9/10/1999`, o que aponta para um cenário clássico de conflito entre `MDY`, `DMY`, string formatada por localidade e contrato implícito entre sistemas. O notebook também lê os leads de `main.main.leads_coluna_origem`, não diretamente do arquivo local, então a investigação precisa validar a linhagem entre planilha, pipeline Gold e tabela efetivamente consumida no cruzamento.

## Prompt pronto para o Codex

```text
Você é um investigador técnico sênior operando no repositório/local workspace deste projeto. Sua missão é conduzir uma investigação profunda, estruturada e baseada em evidências sobre inconsistências no tratamento de datas do fluxo de leads.

Objetivo principal
Descobrir por que datas de leads estão sendo rejeitadas como inválidas durante a execução do notebook de cruzamento/enriquecimento, mesmo havendo a expectativa de que a planilha de leads já esteja tratada, e validar se a causa está nos dados, no parsing do notebook, na configuração, no pipeline Gold, no contrato entre sistemas, ou em uma combinação desses fatores.

Artefatos obrigatórios para a investigação
1. Planilha local de leads: `LEADS-v4.csv`
2. Notebook de cruzamento/enriquecimento: `notebook_origem1 1(1).ipynb`
3. Execução real do notebook: `notebook-run(1).docx`
4. Código do projeto relacionado ao pipeline Gold de leads e qualquer configuração/orquestração associada
5. Se aplicável, queries/tabelas/views relacionadas à etapa de cruzamento com a base do banco

Contexto inicial que você deve confirmar ou refutar com evidências
- O notebook define `LEAD_DATE_STYLE = "AUTO_SAFE"`.
- A função de parsing `add_date_parse_columns(...)` trata datas com barras como ambíguas quando os dois primeiros tokens são <= 12.
- Na execução registrada, o notebook reporta aproximadamente 57.793 leads de entrada e apenas 44.392 linhas com `data_evento` válida.
- O notebook lê leads de `main.main.leads_coluna_origem` e cruza com a base BB `corporativos_pd.db2mci.cliente`.
- A planilha local contém datas como `3/25/2026` e `9/10/1999`, o que sugere forte possibilidade de origem `MDY` ou serialização locale-dependent.
- Há indícios de que datas de evento como `2/4/2026`, `2/9/2026`, `3/4/2026`, `3/9/2026` e `3/11/2026` caiam exatamente na zona de ambiguidade do `AUTO_SAFE` e estejam sendo rejeitadas por desenho do parser, não necessariamente por serem inválidas.
- Também pode existir problema de contrato: o produtor pode estar emitindo datas como string ambígua e o consumidor pode estar exigindo formato tipado ou convenção explicitamente diferente.
Não assuma que qualquer um destes pontos seja verdade sem validar. Use-os como hipóteses iniciais.

Princípios obrigatórios da investigação
- Não faça análise superficial.
- Não conclua nada sem evidência concreta.
- Separe claramente: sintoma, causa provável e causa raiz.
- Trate ambiguidade de data como possível falha de contrato entre sistemas.
- Considere a possibilidade de que o notebook esteja lendo uma tabela que não corresponde ao Gold final, ou que o Gold esteja serializando datas de modo inadequado.
- Diferencie “data impossível”, “data ambígua”, “data válida em outro locale”, “data corrompida”, “data convertida para string”, “data truncada”, “data deslocada por timezone”, “sentinel date/min date”, e “data rejeitada por regra conservadora”.
- Sempre compare schema/tipo físico + representação textual + semântica esperada.
- Se houver incerteza, explicite precisamente o que falta para fechar a causa raiz.

Use as skills do ambiente de forma deliberada e explique o porquê
Você deve usar as skills abaixo com propósito claro, não apenas citá-las. Em cada etapa, diga qual skill foi usada e o que ela acrescentou.

- `debugging-wizard`
  Use para estruturar a árvore de sintomas, hipóteses, contradições e caminhos de reprodução do bug. Deve ajudar a evitar conclusões precipitadas e a organizar a investigação em ordem de maior valor diagnóstico.

- `pandas-pro`
  Use para inspecionar a planilha local em profundidade: padrões de datas, frequências, perfis de formato, nulos, valores extremos, exemplos representativos, detecção de strings ambíguas, comparação entre parsing `MDY`, `DMY`, ISO e typed date.

- `python-pro`
  Use para analisar o notebook `.ipynb`, extrair as funções relevantes, reproduzir localmente a lógica de parsing, abrir/ler o `.docx`, comparar cells, parâmetros, regexes, regras de classificação e possíveis casts para string/date/timestamp.

- `senior-data-scientist`
  Use para quantificar distribuição de erros por tipo, por coluna, por evento, por origem, por faixa temporal, por padrão de formato e por estágio do pipeline. Quero entender a magnitude e não apenas a existência do problema.

- `ml-pipeline`
  Use para avaliar o pipeline Gold end-to-end: ingestão, transforms, casts, serialização, contratos de saída, ordem das etapas, persistência em tabela, efeitos de config, e se o Gold de fato produz o dataset consumido pelo notebook.

- `sql-pro` e/ou `postgres-pro`
  Use para validar a etapa de cruzamento e as estruturas no banco/tabelas: tipos de colunas, casts implícitos, filtros, views intermediárias, sentinelas, min/max dates, possíveis conversões automáticas e diferenças entre schema esperado e schema real.

- `code-reviewer`
  Use para revisão crítica do notebook e do pipeline: pressupostos frágeis, heurísticas perigosas, dependência em locale implícito, casts silenciosos, inconsistências de naming, defaults arriscados e violações de contrato.

- `architecture-designer`
  Use para mapear o fluxo ponta a ponta: planilha local -> ingestão -> pipeline Gold -> tabela final -> notebook de enriquecimento -> cruzamento com banco -> saída final. Quero um mapa explícito do fluxo e dos pontos onde a semântica de data pode se perder.

- `spec-miner`
  Use para inferir contratos implícitos de dados a partir do comportamento real do código e dos dados. Exemplo: “o produtor parece emitir MDY em string”, “o consumidor assume AUTO_SAFE”, “o contrato implícito é incompatível”.

- `test-master`
  Use para definir testes de validação e regressão para cada hipótese relevante. Os testes devem ser executáveis e não abstratos.

- `monitoring-expert`
  Use para sugerir instrumentação, métricas e alertas que impeçam recorrência: taxa de ambiguidade, taxa de parse inválido por coluna, percentuais por formato, drift de schema, quebra de contrato.

- `spark-engineer`
  Use se o pipeline Gold ou a ingestão envolver Spark/Databricks ou transformações em escala, especialmente para revisar parsing distribuído, inferência de schema, comportamento de `to_date`, `to_timestamp`, locale e cast em tabelas persistidas.

Escopo obrigatório da análise
Você deve investigar, no mínimo, os seguintes eixos:

Eixo de dados brutos
- Ler a planilha local e perfilar `data_evento` e `data_nascimento`.
- Identificar padrões reais de representação: `M/d/yyyy`, `d/M/yyyy`, ISO, timestamps, vazios, sentinelas, datas extremas, strings inválidas.
- Quantificar:
  - quantas datas parseiam como `MDY`;
  - quantas parseiam como `DMY`;
  - quantas parseiam em ambos com valores diferentes;
  - quantas não parseiam;
  - quantas se tornam inválidas por regra de negócio (`BEFORE_MIN`, `FUTURE`, sentinel etc.).
- Produzir exemplos concretos de cada classe.
- Verificar se existe evidência de que a planilha “já tratada” continua armazenando datas em formato textual ambíguo.

Eixo do notebook
- Inspecionar o `.ipynb` e localizar toda a lógica que toca datas, especialmente:
  - `LEAD_DATE_STYLE`
  - `add_date_parse_columns`
  - regex/padrões aceitos
  - classificação em `VALID`, `MISSING`, `AMBIGUOUS`, `UNPARSEABLE`, `BEFORE_MIN`, `FUTURE`
  - qualquer cast para `string`, `date`, `timestamp`
  - uso de `MIN_VALID_DATE`, `SENTINEL_DATE`, `current_date`
  - regras diferentes para `data_evento` vs `data_nascimento`
- Reproduzir a lógica do notebook em uma amostra real do CSV.
- Medir se a rejeição observada no `.docx` pode ser explicada pela combinação `AUTO_SAFE` + strings em `MDY`.
- Verificar se a lógica está correta mas incompatível com o contrato de entrada, ou se a própria lógica é inadequada.

Eixo da execução real
- Abrir `notebook-run(1).docx`.
- Extrair prints, logs, outputs, schemas e qualquer evidência da execução.
- Conciliar o que foi executado com o código atual do notebook:
  - o código no `.ipynb` corresponde ao que gerou o `.docx`?
  - os parâmetros/configurações eram os mesmos?
  - os números batem?
  - houve edição posterior no notebook?
- Se houver divergência entre notebook atual e execução registrada, trate isso como hipótese formal e comprove.

Eixo do pipeline Gold
- Localizar no projeto o pipeline Gold de leads e mapear sua linhagem.
- Descobrir qual artefato o notebook realmente consome e se isso corresponde ao output Gold esperado.
- Verificar se o Gold:
  - recebe datas tipadas ou strings;
  - converte datas para texto em algum ponto;
  - formata datas dependentes de locale;
  - salva `date`/`timestamp` como `string`;
  - altera timezone;
  - faz `cast` silencioso;
  - tem regras próprias de padronização que entram em conflito com o notebook;
  - produz a tabela `main.main.leads_coluna_origem` ou se o notebook está apontando para um estágio diferente.
- Validar se o Gold é confiável frente ao problema relatado, incluindo aderência a contrato, tipos, serialização e uso pelo consumidor.

Eixo do banco/cruzamento
- Investigar o papel das datas na etapa de cruzamento com a base BB.
- Verificar se a rejeição das datas de leads ocorre antes do join, durante o staging, ou no matching com a base.
- Confirmar tipos das colunas na base BB e qualquer regra de saneamento adicional.
- Avaliar se o banco recebe datas tipadas enquanto os leads chegam como strings, criando assimetria de contrato.

Hipóteses mínimas que você deve testar
Você deve considerar explicitamente, pelo menos, as hipóteses abaixo:

H1. A planilha local usa predominantemente `MDY`, mas o notebook em `AUTO_SAFE` rejeita o subconjunto ambíguo por precaução.
H2. O pipeline Gold deveria normalizar para `DATE`/ISO, mas está persistindo datas como string ambígua.
H3. O notebook não está lendo o output Gold correto; ele está apontando para uma tabela de estágio/origem ainda não padronizada.
H4. O Gold normaliza corretamente, mas em alguma etapa posterior a data é re-serializada como string.
H5. Há diferenças de configuração entre a execução real e o notebook atual, incluindo parâmetros de parsing.
H6. A lógica do notebook está correta do ponto de vista defensivo, mas o contrato entre produtor e consumidor está ausente ou implícito demais.
H7. Existem casos reais de dados ruins além da ambiguidade de locale, como sentinelas, datas muito antigas, futuras, corrompidas ou fora do range.
H8. O problema é misto: parte dados, parte parser, parte pipeline e parte configuração.

Validações obrigatórias
Faça, no mínimo, as seguintes validações concretas:

1. Perfil detalhado de formatos
- Matriz de formatos encontrados em `data_evento` e `data_nascimento`.
- Frequência absoluta e relativa por padrão.
- Amostras reais.

2. Matriz de parsing
Para cada coluna de data, gere uma matriz de decisão que mostre o resultado de parsing sob:
- ISO
- `MDY`
- `DMY`
- lógica `AUTO_SAFE` atual do notebook
- tipo persistido no Gold/tabela, se disponível
A matriz deve mostrar onde há perda de informação, ambiguidade ou rejeição indevida.

3. Reconciliação linha a linha
Escolha amostras representativas de:
- aceitas pelo notebook;
- ambíguas;
- inválidas por regra;
- extremas/sentinelas;
- datas de nascimento estranhas.
Para cada amostra, rastreie:
- valor bruto na planilha;
- valor após pipeline Gold;
- valor na tabela lida pelo notebook;
- valor após limpeza/parsing no notebook;
- status final;
- impacto no cruzamento.

4. Contrato de dados
Inferir e documentar o contrato real e o contrato desejado para as colunas de data:
- tipo físico esperado;
- formato textual permitido, se houver;
- locale permitido;
- timezone, se aplicável;
- regras de rejeição;
- responsabilidade do produtor e do consumidor.

5. Verificação de configuração/linhagem
Comprove com código/config se:
- `main.main.leads_coluna_origem` é ou não o output Gold;
- o notebook usa a fonte certa;
- existe desvio entre nomenclatura “Gold” e dataset realmente consumido.

6. Reprodução do sintoma
Monte uma reprodução mínima do problema com exemplos reais do dataset, demonstrando exatamente por que uma data “aparentemente válida” é rejeitada.

Saída obrigatória
Sua resposta final deve ser uma análise estruturada e profunda, com as seções abaixo:

1. Resumo executivo
- O que está acontecendo
- Onde provavelmente nasce o problema
- Qual o impacto

2. Achados
- Lista de achados objetivos, cada um com severidade e escopo

3. Evidências
- Para cada achado, cite evidências concretas:
  - arquivo/caminho/cell/linha
  - amostras de dados
  - contagens
  - schema
  - outputs reproduzidos
Não use opinião sem evidência.

4. Hipóteses
- Para cada hipótese:
  - descrição
  - evidências a favor
  - evidências contra
  - status: confirmada / refutada / inconclusiva

5. Testes de validação
- Descreva os testes executados ou propostos
- Inclua dados de entrada, resultado esperado e resultado observado
- Priorize testes que distingam causas concorrentes

6. Causa raiz provável
- Diferencie claramente:
  - sintoma
  - causa provável
  - causa raiz
- Se a causa raiz for composta, explicite a cadeia causal completa

7. Plano de correção priorizado
Separe correções por camada:
- dados/planilha
- notebook/parsing
- pipeline Gold
- banco/crossing
Para cada correção, informe:
- prioridade
- benefício esperado
- risco de regressão
- esforço estimado
- dependências
- como validar a correção

8. Plano de prevenção
- testes automatizados
- contrato de dados explícito
- monitoração e alertas
- métricas recomendadas

Requisitos de qualidade da resposta
- Não entregue uma resposta genérica.
- Não limite a análise a “trocar o parser para MDY”; primeiro prove se isso resolve o sintoma e se é a correção certa no desenho do sistema.
- A resposta deve deixar claro se o problema principal está:
  - no dado,
  - no notebook,
  - no pipeline Gold,
  - na configuração,
  - no contrato entre sistemas,
  - ou em múltiplas camadas.
- Sempre que possível, forneça exemplos concretos com valores reais.
- Se concluir que o principal problema é de contrato, documente explicitamente qual contrato deveria existir.
- Se identificar múltiplas falhas, ordene-as por impacto e probabilidade.
- Se faltar acesso a algum componente do projeto, diga exatamente qual componente faltou e como isso limita a conclusão.

Entregáveis extras desejáveis
- Um quadro-resumo no formato:
  `Sintoma | Evidência | Hipótese | Teste | Resultado | Causa provável | Causa raiz | Correção`
- Trechos de código/SQL mínimos para reproduzir e corrigir
- Sugestão de suite de regressão para impedir a volta do problema
```

## Racional da investigação

Esse prompt foi calibrado para forçar o Codex a tratar o problema como uma possível falha de contrato de dados, e não apenas como um bug local de parser. Isso é importante porque os sinais apontam para um cenário em que a planilha e possivelmente a tabela de entrada carregam datas em string com semântica `MDY`, enquanto o notebook usa uma política conservadora (`AUTO_SAFE`) que rejeita exatamente o subconjunto ambíguo. Se isso for verdade, a data não está “inválida” em si; ela está inválida apenas dentro de um contrato mal definido ou conflitante.

Ao mesmo tempo, o prompt não deixa o Codex cair na explicação fácil. Ele obriga a confirmar se o notebook realmente consome o output do Gold, se o Gold não reserializa datas para string, se houve divergência entre o notebook atual e a execução documentada, e se existem também casos genuínos de sujeira de dados, como datas extremas, sentinelas ou out-of-range.

## Critérios de qualidade esperados do resultado

Uma boa resposta do Codex, seguindo esse prompt, deve conseguir demonstrar pelo menos uma cadeia causal reproduzível, linha a linha, desde o valor bruto até o status final no notebook. Ela também deve deixar claro se a correção correta é mudar o dado, mudar o notebook, corrigir o pipeline Gold, corrigir o apontamento da tabela, ou explicitar o contrato de datas entre produtor e consumidor.

O resultado ideal não termina em “ajuste `LEAD_DATE_STYLE` para `MDY`”. Ele mostra quando isso seria apenas um paliativo, quando seria a correção certa, e quando seria perigoso porque mascararia uma violação estrutural no pipeline. Além disso, ele precisa produzir testes e monitoração que impeçam a recorrência do mesmo problema em execuções futuras.