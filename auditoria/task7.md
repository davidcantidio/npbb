# Task 7 — Parser ETL: multi-aba, cabeçalho tardio, células mescladas e delimitadores

**Prioridade:** P2

## Problema

`extract.py` limita o processamento XLSX à **primeira aba**, usa `promote_merged_header=False`, procura cabeçalho nas **primeiras 40 linhas** apenas, e o delimitador CSV é inferido de forma simples (vírgula vs `;` na primeira linha). Planilhas reais com aba secundária, cabeçalho após linha 40, células mescladas no título, ou CSV com tab ou delimitador ambíguo geram **falsos negativos** ou dados mal alinhados.

## Escopo

- `backend/app/modules/leads_publicidade/application/etl_import/extract.py`
- API/UI para **seleção de aba** e/ou `header_row` forçada (se já existir parcialmente, estender)
- Heurísticas: `max_scan_rows` configurável, merged cells, sniffing de delimitador mais robusto

## Critérios de aceite

1. Suporte explícito a **escolha de aba** (ou convenção documentada quando multi-aba).
2. Cabeçalho detectável além da janela fixa de 40 linhas **ou** parâmetro operador com validação.
3. Comportamento definido para merged cells no cabeçalho (sem corromper colunas silenciosamente).
4. CSV com tab (`\t`) ou delimitador ambíguo tratado conforme matriz de casos acordada.
5. Fixtures e testes para: duas abas, cabeçalho > linha 40, merged cell no título, delimitador tab.

## Plano de verificação

- Testes unitários com ficheiros mínimos gerados em `backend/tests` ou `fixtures/`.
- Regressão nos casos já cobertos (header forçado, CSV `;`).

## Skills recomendadas (acionar na execução)

Antes de implementar, **ler** cada skill indicada (`SKILL.md` na pasta listada) e seguir as práticas descritas.

- [.claude/skills/python-pro/SKILL.md](.claude/skills/python-pro/SKILL.md) — `extract.py`, openpyxl/csv, edge cases de encoding e delimitadores.
- [.claude/skills/pandas-pro/SKILL.md](.claude/skills/pandas-pro/SKILL.md) — opcional, se usar DataFrames para sniffing/heurísticas de ficheiro.
- [.claude/skills/fastapi-expert/SKILL.md](.claude/skills/fastapi-expert/SKILL.md) — novos parâmetros de API (aba, linha de cabeçalho) e validação de input.
- [.claude/skills/test-master/SKILL.md](.claude/skills/test-master/SKILL.md) — fixtures XLSX/CSV e matriz de casos de teste.

## Subtarefa obrigatória: handoff ao concluir

Ao **terminar** esta tarefa (código, testes e revisão), criar o ficheiro **`auditoria/handoff-task7.md`** com:

1. **Resumo** das novas capacidades do parser e parâmetros expostos ao cliente.
2. **Lista de ficheiros** tocados e **fixtures** adicionadas (caminhos relativos).
3. **Diffs / revisão**: destacar alterações em `extract.py` e contratos de preview; comandos `git diff` sugeridos por área.

O handoff deve permitir continuidade sem reler toda a conversa.

## Referência

Relatório completo: [auditoria/deep-research-report.md](deep-research-report.md) — secção **Achados detalhados** → **O parser ETL tem limitações relevantes para casos reais de planilha**; **Lacunas de teste**.
