# P1: Unificar a Orquestração do Passe de Indexação em `sync.py`

## Summary
- O P1 é só refatoração de orquestração e estratégia transacional.
- Não mexe em derivação, classificação, colunas `intake/prd` nem na função canônica que materializa um Markdown.
- O objetivo é eliminar os dois loops paralelos de passe completo e deixar uma única rotina de iteração sobre os arquivos, usada tanto no modo estrito quanto no modo tolerante.

## Implementation Changes
- Preservar a API pública vigente do branch em que o patch for aplicado. O plano não impõe nomes como `indexed_at`, `partial_errors`, `indexed_at_str`, `transaction_strategy` ou `index_errors`; ele impõe só a semântica.
- Manter uma única função canônica de indexação por arquivo, seja ela `_index_markdown_file`, `index_one_markdown_file` ou o nome atual do branch. Essa função continua sendo a única responsável por derivação/materialização.
- Introduzir um helper único de iteração do passe, responsável por:
  - receber a lista ordenada de `.md`;
  - chamar a função canônica de indexação por arquivo;
  - aplicar a estratégia transacional ativa;
  - acumular erros tolerados quando o modo parcial estiver ativo;
  - devolver o inteiro de retorno conforme o contrato vigente do branch.
- `run_index_pass()` passa a fazer apenas:
  - descoberta e ordenação dos arquivos;
  - bootstrap do estado compartilhado do passe;
  - delegação para o helper único de iteração.
- Remover o segundo caminho de passe completo hoje duplicado. O critério não é “remover uma função com nome X”, e sim “não existir mais uma segunda implementação do loop principal de indexação”.
- Preservar exatamente a ordenação atual dos arquivos no passe.

## Contract Clarifications
- O contrato de retorno deve ser preservado conforme o branch-alvo, não redefinido pelo P1.
- Se o branch-alvo atualmente devolve o total de ficheiros descobertos no passe, esse comportamento deve continuar, inclusive no modo tolerante.
- Se houver assimetria entre modos no checkout usado para implementar, o P1 não deve introduzir uma mudança silenciosa de contrato; qualquer ajuste de retorno só pode acontecer como mudança intencional e explícita fora deste P1.
- Em outras palavras: P1 não altera o significado observável do inteiro devolvido por `run_index_pass()`.

## Test Plan
- Cobrir o modo estrito e o modo tolerante com monkeypatch da função canônica atual de indexação por arquivo.
- Garantir que os dois modos usam a mesma função canônica e percorrem a mesma lista de arquivos na mesma ordem.
- Garantir que o modo tolerante continua a registrar erros no coletor vigente do branch e continua o passe após falhas toleradas.
- Adicionar uma regressão estrutural baseada em comportamento/forma, não em nome fixo:
  - deve existir um único sítio no passe que chama a função canônica de indexação por arquivo;
  - `run_index_pass()` não pode conter um segundo loop paralelo com regras próprias de materialização.
- Manter os testes focados em orquestração/transações; não revalidar derivação de intake/prd no P1.

## Assumptions
- O refactor recente de `index_derivation` e das colunas `intake/prd` permanece intacto.
- O P1 complementa esse trabalho; não compete com ele.
- A função canônica de indexação por arquivo já existe e deve ser reutilizada, não reescrita.
