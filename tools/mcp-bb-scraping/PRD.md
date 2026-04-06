# PRD - Pipeline de Scrape e Analise (Instagram BB)

## Contexto e objetivo
Criar um fluxo unico que receba um handle de Instagram, execute o scraping via Playwright (MCP), gere planilhas de indicadores, de acordo com o modelo em C:\Users\NPBB\OneDrive - Banco do Brasil S.A\Documentos\MCP\data\indicadores_tainahinckel.csv e C:\Users\NPBB\OneDrive - Banco do Brasil S.A\Documentos\MCP\data\indicadores_bb_por_mes_tainahinckel.csv. Com base nos dados dessas planilhas geradas, produzir um texto executivo em PT-BR interpretando a qualidade da entrega do perfil patrocinado pelo Banco do Brasil, tomando como referencia o modelo em C:\Users\NPBB\OneDrive - Banco do Brasil S.A\Documentos\MCP\data\analise BI Instagram taina hinkel.docx.

O texto deve ser corrido, coeso, sem vies e sem recomendacao explicita (ex.: "renova/nao renova").
O texto considera todos os posts publicados ou republicados pelo patrocinado (perfil principal).
A interpretacao deve incluir uma leitura qualitativa (subjetiva) sobre o quanto os posts promovem a marca patrocinada e o quanto geram storytelling, com ressalva de que se trata de uma leitura interpretativa.

## Problema
Hoje ha passos separados: scraping, indicadores e analise. O objetivo e organizar em um pipeline simples, repetivel e audivel, com saidas padronizadas e logs claros.

## Metas
- Um unico fluxo de ponta a ponta: `handle -> scrape -> indicadores -> texto executivo`.
- Indicadores tabulados em CSV (1 linha por handler) + tabela mensal separada.
- Texto executivo claro para leigos, com explicacao dos numeros e ressalvas.
- Reprodutibilidade: logs e arquivos nomeados por `<handle>`.

## Nao metas
- Nao criar dashboard ou UI.
- Nao fazer benchmark externo ou recomendacao de renovacao.
- Nao contornar login/captcha/anti-bot.

## Personas
- Analista: roda o pipeline e compartilha outputs.
- Diretoria: consome o texto executivo.

## Estado atual (baseline)
- Scraping multi-plataforma em Node + Playwright.
- Outputs com sufixo `<handle>` (ex.: `data/instagram_posts_enriched_<handle>.csv`).
- Indicadores gerados por `report/append_indicator.py` (CSV tabulado + mensal).
- Script `generate_report.py` gera texto a partir de planilha de posts.

## Visao do produto (pipeline)
1) Input: usuario informa o handle do Instagram.
2) Scrape: agente executa Playwright via MCP e coleta dados.
3) Indicadores: script Python gera indicadores tabulados a partir do CSV enriquecido.
4) Interpretacao: agente de IA interpreta os indicadores e produz texto executivo.

## Requisitos funcionais
### RF1 - Entrada por handle
- Aceitar `--profile <handle>` (ou `--perfil`) no scraping.
- Normalizar handle (remove @, lowercase).

### RF2 - Scraping via Playwright (MCP)
- Executar scraping do Instagram (X/TikTok opcionais).
- Respeitar regras de login manual e sem bypass.
- Registrar logs por execucao em `data/run_<handle>.log`.

### RF3 - Indicadores tabulados
- Gerar `data/indicadores_<handle>.csv` (1 linha, colunas por metrica).
- Gerar `data/indicadores_bb_por_mes_<handle>.csv` (handler, month, posts_bb, posts_total).
- Incluir `handler` como chave de join.

### RF4 - Interpretacao por IA
- Entradas: `indicadores_<handle>.csv` + `indicadores_bb_por_mes_<handle>.csv`.
- Saida: texto executivo em `out/texto_relatorio.md`.
- Linguagem PT-BR, sem jargao, sem recomendacao explicita.
- Escopo: considerar apenas posts publicados/republicados pelo patrocinado (owner principal ou `is_owner_profile=true`).
- A leitura deve incluir criterio subjetivo sobre promocao da marca e storytelling, deixando claro que e interpretativo.
- Incluir ressalva final sobre ausencia de metas/benchmarks.
- Se algum indicador estiver ausente, omitir o trecho correspondente e registrar `null` no JSON de saida.

### RF5 - Saidas e rastreabilidade
- `out/indicadores.json` com todos os numeros e metadados.
- `out/texto_relatorio.md` apenas texto corrido.
- `out/tabelas.md` opcional com tabelas de suporte.

## Requisitos nao funcionais
- **Reprodutibilidade:** resultados baseados apenas nos dados do CSV.
- **Privacidade:** nao logar dados sensiveis; guardar chaves de API via env.
- **Observabilidade:** logs claros com mapeamento de colunas e etapa do pipeline.
- **Compatibilidade:** CSV com `;` e BOM; suporte a XLSX.

## Escopo da analise
- O texto e os indicadores principais consideram apenas posts publicados ou republicados pelo patrocinado.
- Posts de outras contas podem existir no dataset; devem ser excluidos dos calculos principais e, se necessario, apenas contextualizados.
- Republicados: quando o owner/autor corresponde ao handle principal ou quando `is_owner_profile=true` estiver disponivel.

## Heuristicas e regras
- Mapeamento de colunas via palavras-chave (data, url, caption, mentions, hashtags, owner, media_type, likes, comments, views).
- Patrocinado:
  - Preferir coluna dedicada (is_collab/sponsored/etc).
  - Caso ausente, usar paid_partnership/branded_content.
  - Caso ausente, usar proxy por mencoes de marcas (deduplicado por post).
- BB:
  - Aliases editaveis (`@bancodobrasil`, `banco do brasil`, `#bancodobrasil`).
  - Campanhas editaveis (`#tamojuntobb`, `#squadbb`, etc).
  - Token `bb` sozinho so vale se houver `banco` ou `brasil`.

## Experiencia de uso (CLI)
### Scrape + indicadores (existente)
```
npm run scrape -- --profile <handle> --since YYYY-MM-DD --out data
```

### Interpretacao por IA (novo)
Exemplo de script a definir:
```
python report/interpret_indicators.py --handle <handle> --indicators data/indicadores_<handle>.csv --monthly data/indicadores_bb_por_mes_<handle>.csv --out out
```

## Arquitetura (alto nivel)
- Node (Playwright) -> CSVs em `data/`.
- Python (indicadores) -> `data/indicadores_<handle>.csv` + `data/indicadores_bb_por_mes_<handle>.csv`.
- IA (interpretacao) -> `out/texto_relatorio.md` + `out/indicadores.json`.

## Indicadores obrigatorios no texto
- Base: total e periodo min/max considerando posts do @principal; se houver outras contas na base, citar participacao apenas como contexto.
- Presenca BB: volume, share, ultima mencao, dias desde ultima, mensalidade (com meses zero), regularidade (mediana/media).
- Patrocinados: total, share, BB dentro dos patrocinados, BB organico vs patrocinado.
- Ranking de marcas (Top 10), posicao do BB e razao vs lider.
- Formato: share de reels no total e no BB (se existir).
- Performance: medianas BB vs nao-BB em patrocinados (se houver dados).
- Origem das mencoes BB: @principal vs outras contas (quando houver posts de terceiros no dataset).

## Telemetria e logs
- Logar mapeamento de colunas detectado.
- Logar quantidade de linhas filtradas por data.
- Logar quantos posts do owner entram no recorte e quantos foram excluidos.
- Logar metodo de patrocinio (coluna vs proxy).

## Riscos e mitigacoes
- Dados faltantes -> omitir trechos e registrar `null` no JSON.
- Dados inconsistentes -> validar formatos e informar no log.
- Dependencia de IA externa -> permitir modelo local ou fallback sem IA.

## Perguntas em aberto
- Qual provedor de IA? (OpenAI, Anthropic, modelo local)
- Qual limite minimo de dados para gerar texto?
- Onde armazenar o texto final (padrao: `out/`)? 

## Entregas e fases
1) Pipeline documentado (scrape + indicadores + interpretacao).
2) Implementacao da etapa de interpretacao por IA.
3) QA com datasets reais e ajustes de linguagem.
