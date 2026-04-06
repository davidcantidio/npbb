# Prompt base - Texto executivo (PT-BR)

Objetivo:
Gerar um texto executivo corrido, em portugues do Brasil (PT-BR), com base no ledger estruturado.

Publico-alvo:
Diretoria e leitores leigos, sem familiaridade tecnica.

Restricoes:
- Sem vies ou julgamento; manter tom neutro e descritivo.
- Nao emitir recomendacao explicita (ex.: "renova", "nao renova", "deve").
- Evitar jargao; quando inevitavel, explicar em linguagem simples.
- Nao inventar dados; usar apenas o que vier no ledger.
- Nao incluir tabelas nem listas.
- Evitar ingles e abreviacoes sem explicacao.
- Mencionar "Banco do Brasil (BB)" na primeira ocorrencia de BB.
- Nao mencionar arquivos, colunas, campos ou detalhes tecnicos do dataset.

Regras de linguagem e tom:
- Linguagem leiga e direta.
- Explicar "mediana" como "intervalo mais tipico" e "media" como "media geral".
- Preferir frases curtas e claras, com 1-2 frases por paragrafo.
- Usar acentuacao correta e caracteres especiais do pt-BR.
- Evitar adjetivos de julgamento e recomendacoes.
- Preferir termos simples: "percentual" em vez de "share"; "curtidas e comentarios" em vez de "engajamento".
- Quando citar percentuais, medianas ou medias, indicar a base ("com base em X posts").
- Se mencionar reels, explicar como "videos curtos do Instagram" na primeira ocorrencia.
- Ao mencionar percentual, explicar em termos simples (ex.: "X% do total, ou seja, X em cada 100 posts").
- Sempre que possivel, mostrar contagem + percentual + razao (ex.: "31 posts (32,0% do total, 31/97)").
- Evitar repeticoes e frases muito longas.
- Preferir sujeito direto e reduzir redundancias.

Formato de datas e numeros:
- Preferir datas em DD/MM/AAAA no texto. Se nao conseguir converter, manter YYYY-MM-DD.
- Para meses, usar abreviacoes pt-BR: jan, fev, mar, abr, mai, jun, jul, ago, set, out, nov, dez (ex.: "jun/2024").
- Arredondar percentuais para 1 casa decimal quando possivel.

Tratamento de incerteza e neutralidade:
- Manter postura neutra; descrever o que os dados mostram sem prescrever acoes.
- Evitar conclusoes prescritivas ou valorativas.
- Nao atribuir causa/efeito.

Saida e formato:
- Texto corrido, sem tabelas ou listas.
- Tamanho aproximado: 5 a 8 paragrafos.

Estrutura do texto final (ordem sugerida):
Bloco A - Base e recorte:
- Total de publicacoes e periodo analisado.
- Participacao do @principal vs outras contas (contagem, percentual e razao).
- Se houver outras contas, explicitar que sao reposts/republicacoes de outros perfis no proprio perfil principal.

Bloco B - Presenca do BB:
- Total e percentual de posts com mencao ao BB.
- Data da ultima mencao e dias desde a data de referencia.
- Resumo de mencoes por mes (faixa e picos; meses sem mencao quando houver).
- Intervalo medio e mediano entre mencoes, explicados em linguagem simples.
- Qualidade de marcacao: percentual de posts BB com @bancodobrasil explicitamente e quantos ficam sem marcacao direta.
- Se houver distribuicao por tipo de conexao (mention/hashtag), resumir em linguagem simples.

Bloco C - Patrocinados:
- Explicar o criterio de patrocinio em linguagem simples (marcacao de parceria paga/colaboracao), sem citar colunas.
- Total de posts patrocinados e percentual no total.
- Total de posts BB dentro de patrocinados e seu percentual.
- BB organico vs patrocinado, destacando quantos BB estao fora de patrocinados.

Bloco D - Comparacao de marcas:
- Ranking de marcas em posts patrocinados (mencoes), com contagem por handle.
- Destacar lider(es) e "segundo pelotao" quando houver empate.
- Posicao do BB no ranking e razao vs marca mais citada.
- Se houver indicador de "BB sozinho vs multimarca", mencionar se o BB aparece sozinho ou junto de outras marcas.
- Se houver lista de marcas que mais aparecem junto do BB, citar as principais.

Bloco E - Formato e resposta do publico:
- Participacao de reels no total e dentro dos posts BB (e em patrocinados, se houver).
- Considerando apenas reels patrocinados, indicar o percentual que menciona BB (se houver indicador).
- Medianas de curtidas/comentarios (BB vs nao-BB em patrocinados), com base de posts utilizada.
- Se a amostra nao-BB for pequena, incluir ressalva de tamanho de base.

Bloco F - Origem das mencoes BB:
- Quantos posts BB sao do @principal vs outras contas, com percentual.
- Se houver, mencionar quais outras contas mais contribuem (top 1-3).

Ressalva final:
- Indicar que nao ha metas ou referencias registradas e o texto apenas descreve os dados.
- Se houver avisos de QA (cobertura baixa ou base pequena), incluir a ressalva ao final.
