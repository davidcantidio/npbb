# Prompt base - Ledger de indicadores (PT-BR)

Objetivo:
Organizar os indicadores em um ledger estruturado, sem texto narrativo.

Regras:
- Use apenas os dados fornecidos no input.
- Nao invente numeros nem datas.
- Nao cite arquivos, colunas, campos ou detalhes tecnicos do dataset.
- Se uma secao nao tiver dados validos ou estiver marcada para omissao no QA, retorne null.
- Preserve os valores exatamente como fornecidos.
- other_is_reposts deve ser true quando other_posts > 0.

Saida:
- Responda apenas no formato exigido pelo schema.
