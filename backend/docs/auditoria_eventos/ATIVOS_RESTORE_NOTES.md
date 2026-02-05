# ATIVOS — Notas de Restore (inferências)

Data: 2026-02-05

## Itens não encontrados no histórico
Após varredura em commits/stashes (incluindo f59b8f7), não foram encontrados:
- UI com cards agrupando diretorias + barras empilhadas por estoque.
- Visualização de barras empilhadas (stacked) em Ativos.

## Inferências aplicadas (mínimo equivalente)
Para atender a demanda atual sem reescrever o domínio:
1) **Cards por diretoria** foram implementados no frontend usando os dados já entregues por `GET /ativos`.
   - Agrupamento: por `diretoria_id`.
   - Totais: soma de `total`, `usados`, `disponiveis`.
2) **Barras empilhadas** foram interpretadas como **múltiplas barras verticais (uma por evento) dentro do card da diretoria**, exibindo o uso por evento.

Justificativa:
- Não há referência explícita no repo a "stacked bars" (só há barras simples nos cards de Ativos).
- A interpretação adotada preserva o conceito de estoque por diretoria e torna o uso por evento visível sem alterar backend.

Observação:
- Caso exista um layout original fora do Git, ele deve substituir esta implementação.
