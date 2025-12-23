# Gamificacao (MVP) - Decisao de contrato

## Decisao
- **Gamificacao e vinculada a Ativacao (opcao B)**.
- Relacao no backend:
  - `gamificacao.ativacao_id` e **obrigatorio** e **UNIQUE** (1:1 por ativacao)
  - `ativacao.evento_id` define o evento
  - Logo, um evento pode ter **multiplas** gamificacoes (1:N) indiretamente, via suas ativacoes.

## Racional
- O modelo/migration atual ja suportam essa relacao (tabela `gamificacao` existe e tem `ativacao_id` UNIQUE).
- Mantem compatibilidade com o desenho de dominio (Ativacao como unidade operacional do evento).
- Permite listar "Gamificacoes adicionadas" no contexto do evento via join `evento -> ativacao -> gamificacao`.

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
- Para **criar** uma gamificacao, a API precisa receber `ativacao_id` (e validar que a ativacao pertence ao evento e nao possui gamificacao ainda).
- A UI precisa permitir escolher a ativacao (ou derivar de alguma selecao de ativacao no fluxo).
