# Prompt base - Texto executivo (PT-BR)

Objetivo:
Gerar um texto executivo corrido, em portugues do Brasil (PT-BR), que traduza os indicadores em evidencias claras e observaveis para apoiar decisao, sem recomendacoes explicitas.

Publico-alvo:
Diretoria e leitores leigos, sem familiaridade tecnica.

Restricoes:
- Sem vies ou julgamento; manter tom neutro e descritivo.
- Nao emitir recomendacao explicita (ex.: "renova", "nao renova", "deve").
- Evitar jargao; quando inevitavel, explicar em linguagem simples.
- Nao inventar dados; usar apenas o que for fornecido.
- Nao incluir tabelas no texto principal.
- Evitar ingles e abreviacoes sem explicacao (ex.: "KPI", "benchmark", "share").
- Mencionar "Banco do Brasil (BB)" na primeira ocorrencia de BB.
- Evitar especular sobre origem de outras contas; use linguagem generica quando necessario.
- Nao mencionar nomes de arquivos, caminhos ou "indicadores.json". Se a origem indicar arquivo, omitir essa parte.
- Nao mencionar colunas, campos, mapeamentos ou detalhes tecnicos do dataset. Use apenas linguagem de negocio.

Regras de linguagem e tom:
- Linguagem leiga e direta, sem termos tecnicos nao explicados.
- Explicar "mediana" como "intervalo mais tipico" e "media" como "media geral".
- Preferir frases curtas e claras, com 1-2 frases por paragrafo.
- Usar acentua??o correta e caracteres especiais do pt-BR (ex.: per?odo, publica??es, men??o, frequ?ncia, m?dia, ?ltimo, n?o).
- Evitar adjetivos de julgamento (ex.: "excelente", "fraco") e recomendacoes.
- Preferir termos simples: "percentual" em vez de "share"; "curtidas e comentarios" em vez de "engajamento"; "comparacao" em vez de "benchmark".
- Quando citar percentuais, medianas ou medias, indicar a base ("com base em X posts com dados disponiveis").
- Se mencionar reels, explicar como "videos curtos do Instagram" na primeira ocorrencia.
- Ao mencionar percentual, explicar em termos simples (ex.: "X% do total, ou seja, X em cada 100 posts").
- Sempre que possivel, mostrar contagem + percentual + razao (ex.: "31 posts (32,0% do total, 31/97)").
- Se fizer sentido, traduzir razoes em linguagem simples (ex.: "cerca de 3 em cada 4 publicacoes").
- Evitar repeticoes e frases muito longas.
- Preferir sujeito direto e reduzir redundancias (ex.: "54 publicacoes mencionam o BB" em vez de "Em relacao ao BB, foram identificadas 54 publicacoes...").

Formato de datas e numeros:
- Preferir datas em DD/MM/AAAA no texto. Se nao conseguir converter, manter YYYY-MM-DD.
- Para meses, usar abreviacoes pt-BR: jan, fev, mar, abr, mai, jun, jul, ago, set, out, nov, dez (ex.: "jun/2024").
- Arredondar percentuais para 1 casa decimal quando possivel.

Tratamento de incerteza e neutralidade:
- Manter postura neutra; descrever o que os dados mostram sem prescrever acoes.
- Evitar conclusoes prescritivas ou valorativas.
- Frases proibidas (exemplos): "recomenda-se", "deve renovar", "nao deve renovar", "indica sucesso", "fracasso".
- Nao atribuir causa/efeito (ex.: "por causa de", "isso prova que").

Saida e formato:
- Saida em texto corrido, sem tabelas ou listas.
- Tamanho aproximado: 5 a 8 paragrafos (um bloco por paragrafo).
- Manter linguagem simples e objetiva, sem marcacao adicional.

Exemplo curto (entrada -> saida):
Entrada:
indicadores_json: { "base": { "posts_total": 20, "date_min": "2024-01-01", "date_max": "2024-03-31" }, "bb": { "bb_posts_total": 2, "bb_share_pct": 10.0 }, "sponsored": { "sponsored_posts_total": 5, "sponsored_share_pct": 25.0 } }
user: "@exemplo"
periodo: "2024-01-01 a 2024-03-31"
origem: "posts do Instagram do atleta X"

Saida (trecho):
"O periodo analisado vai de 2024-01-01 a 2024-03-31, com 20 publicacoes no recorte. Em relacao ao Banco do Brasil (BB), houve 2 posts com mencao (10,0% do total). Sobre posts patrocinados, foram 5 publicacoes (25,0% do total)."

Exemplos curtos:
- "A mediana indica o intervalo mais tipico entre mencoes, enquanto a media mostra o intervalo geral."
- "Com base em 12 posts com dados de curtidas, a mediana de curtidas foi X."
- "O percentual de 10% significa que, em media, 10 a cada 100 posts tem a caracteristica descrita."

Regras de omissao e condicionais:
- Se um indicador estiver null, omitir o trecho correspondente.
- Se a cobertura de uma metrica for 0% ou inexistente, nao mencionar essa metrica.
- Se a cobertura de uma metrica estiver abaixo do minimo definido no QA, omitir essa metrica.
- Se nao houver posts no recorte, gerar apenas um paragrafo curto informando isso + ressalva final.
- Se nao houver mencoes ao BB, registrar explicitamente e omitir subtitulos de intervalos e ranking.
- Se nao houver dados de patrocinio, omitir o bloco de patrocinados.
- Para "meses sem mencao", considerar apenas meses com posts_total > 0 e posts_bb = 0.

Estrutura do texto final (ordem e conteudo minimo):
Bloco A - Base e recorte:
- Total de publicacoes no recorte e periodo analisado (date_min e date_max).
- Participacao do @principal vs outras contas (contagem, percentual e razao).
- Se houver outras contas, explicitar que sao reposts/republicacoes de outros perfis no proprio perfil principal e por isso entram no recorte.

Bloco B - Presenca do BB:
- Total e percentual de posts com mencao ao BB.
- Data da ultima mencao e dias desde a data de referencia (use date_max; se existir data de coleta/ref no indicadores_json, preferir ela).
- Resumo de mencoes por mes (use monthly.summary para faixa e picos; liste meses sem mencao quando houver).
- Intervalo medio e mediano entre mencoes, explicados em linguagem simples.
- Qualidade de marcacao: percentual de posts BB com @bancodobrasil explicitamente e quantos ficam sem marcacao direta.
- Se houver distribuicao por tipo de conexao (mention/hashtag), resumir em linguagem simples.

Bloco C - Patrocinados:
- Explicar o criterio de patrocinio em linguagem simples (marcacao de parceria paga/colaboracao), sem citar colunas ou arquivos.
- Total de posts patrocinados e percentual no total, com razao (n/total).
- Total de posts BB dentro de patrocinados e seu percentual.
- BB organico vs patrocinado (contagem e percentual dentro dos posts BB), destacando quantos BB estao fora de patrocinados.

Bloco D - Comparacao de marcas:
- Ranking de marcas em posts patrocinados (mencoes), com contagem por handle.
- Destacar lider(es) e "segundo pelotao" quando houver empate, com contagem e percentual sobre patrocinados.
- Posicao do BB no ranking e razao vs marca mais citada.
- Se houver indicador de "BB sozinho vs multimarca", mencionar se o BB aparece sozinho ou sempre junto de outras marcas.
- Se houver lista de marcas que mais aparecem junto do BB, citar as principais.

Bloco E - Formato e resposta do publico:
- Participacao de reels no total e dentro dos posts BB (e em patrocinados, se houver indicador).
- Considerando apenas reels patrocinados, indicar o percentual que menciona BB (se houver indicador).
- Medianas de curtidas/comentarios (BB vs nao-BB em patrocinados), com base de posts utilizada.
- Se a amostra nao-BB for pequena, incluir ressalva de tamanho de base.

Bloco F - Origem das mencoes BB:
- Quantos posts BB sao do @principal vs outras contas, com percentual.
- Se houver, mencionar quais outras contas mais contribuem (top 1-3).

Ressalva final:
- Indicar que nao ha metas ou referencias registradas e o texto apenas descreve os dados.

Entradas obrigatorias:
- indicadores_json: objeto com os indicadores calculados.
- user: handle principal (ex: "@tainahinckel").
- periodo: texto com data inicial e data final (ex: "2024-01-01 a 2024-12-31").
- origem: breve contexto da base (ex: "posts do Instagram do atleta X").

Exemplo de formato de entrada:
indicadores_json: { "base": { "posts_total": 120, "date_min": "2024-01-01", "date_max": "2024-12-31" }, "bb": { "bb_posts_total": 8, "bb_share_pct": 6.7 } }
user: "@exemplo"
periodo: "2024-01-01 a 2024-12-31"
origem: "posts do Instagram do atleta X"
