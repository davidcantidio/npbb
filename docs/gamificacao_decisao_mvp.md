# Gamificacao (MVP) - Decisao de contrato

## Decisao
- **Gamificacao pertence ao Evento** e e **selecionada na Ativacao** (conforme tela de referencia).
- Relacao no backend (MVP):
  - `gamificacao.evento_id` e **obrigatorio** (1:N evento -> gamificacoes)
  - `ativacao.gamificacao_id` e **opcional** (uma ativacao pode apontar para uma gamificacao ou "Nenhuma")

## Racional
- A tela de referencia lista/cadastra gamificacoes antes das ativacoes e, no formulario de ativacao, o usuario escolhe a gamificacao correspondente (ou nenhuma).
- Simplifica o fluxo: nao exige `ativacao_id` para criar gamificacao.
- Permite reutilizar a mesma gamificacao em mais de uma ativacao (caso o negocio permita), sem limitar a 1:1.

## Campos do formulario (MVP)
Conforme tela de referencia, os campos sao **obrigatorios**:
- `nome` (string)
- `descricao` (string, **max 240** na UI de referencia)
- `premio` (string)
- `titulo_feedback` (string)
- `texto_feedback` (string, **max 240** na UI de referencia)

Observacao:
- A tela original exibe a coluna **Premio** na tabela; no MVP, manter `premio` como campo do contrato (obrigatorio).

## Impactos na API/UI
- Para **criar** uma gamificacao, a API usa o `evento_id` do path (`POST /evento/{id}/gamificacoes`).
- Para **vincular** uma gamificacao a uma ativacao, a ativacao precisa ter um campo opcional `gamificacao_id` (selecionado no formulario de ativacao, com opcao "Nenhuma"), validando que a gamificacao pertence ao evento.
