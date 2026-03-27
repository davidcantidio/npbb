---
doc_id: "TASK-2.md"
user_story_id: "US-5-03-CONTRATO-MINIMO-PAYLOAD-QR"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-5-EMISSAO-INTERNA-QR-UNITARIO/CONTRATO-PAYLOAD-QR.md"
  - "backend/app/routers/ingressos.py"
  - "backend/app/schemas/ingressos.py"
  - "backend/app/services/qr_emissao_unitario_payload.py"
tdd_aplicavel: true
---

# TASK-2 - Implementar serializacao do payload QR conforme o contrato

## objetivo

Implementar no backend a geracao do payload (conteudo serializado associado ao QR) para emissao interna unitaria concluida, de forma que cumpra o [CONTRATO-PAYLOAD-QR.md](../../CONTRATO-PAYLOAD-QR.md) e seja reversivel para a entidade de emissao sem ambiguidade, integrando-se ao fluxo entregue pela **US-5-02**.

## precondicoes

- **T1** concluida: `CONTRATO-PAYLOAD-QR.md` publicado e aprovado para implementacao.
- **US-5-01** e **US-5-02** em estado `done` com ponto de emissao e modelo persistido disponiveis no codigo.
- Identificar o router, schemas e servico reais usados pela US-5-02; ajustar `write_scope` na descricao de handoff se os caminhos divergirem dos listados no frontmatter (mantendo um unico modulo coeso para a funcao de montagem do payload).

## orquestracao

- `depends_on`: `T1` deve estar `done`.
- `parallel_safe`: `false`.
- `write_scope`: superficies previstas — confirmar na execucao se a US-5-02 introduziu router dedicado em vez de `ingressos.py`; nesse caso, substituir o router listado mantendo o servico de payload desacoplado quando possivel.

## arquivos_a_ler_ou_tocar

- [CONTRATO-PAYLOAD-QR.md](../../CONTRATO-PAYLOAD-QR.md)
- [TASK-1.md](./TASK-1.md)
- `backend/app/routers/ingressos.py` *(ou router/servico de emissao introduzido pela US-5-02)*
- `backend/app/schemas/ingressos.py` *(ou schemas alinhados a emissao unitaria)*
- `backend/app/services/qr_emissao_unitario_payload.py` *(criar se nao existir modulo dedicado)*
- Documentacao OpenAPI gerada pelo FastAPI, se o payload for exposto na resposta da API

## testes_red

- testes_a_escrever_primeiro:
  - teste unitario que monta o payload a partir de uma emissao (ou estrutura de dominio equivalente) e falha enquanto o formato nao coincidir com o contrato documentado (campos obrigatorios e `contrato_versao` alinhados ao doc).
  - caso cobrindo reversibilidade: a partir do payload gerado, recuperar de forma inequivoca o identificador da emissao esperado pelo contrato.
- comando_para_rodar:
  - `cd /Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend && PYTHONPATH=/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb:/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_qr_emissao_unitario_payload.py`
- criterio_red:
  - os testes novos devem falhar antes da implementacao; se passarem sem alteracao de codigo, parar e rever o contrato ou o cenario de teste.

## passos_atomicos

1. Escrever os testes listados em `testes_red` no ficheiro de teste referido no comando (criar o ficheiro se necessario).
2. Executar o comando red e confirmar falha inicial coerente com o contrato.
3. Implementar `build_qr_payload` (ou nome alinhado ao projeto) em `backend/app/services/qr_emissao_unitario_payload.py` conforme `CONTRATO-PAYLOAD-QR.md`.
4. Integrar a chamada ao builder no fluxo de emissao concluida (servico ou router entregue pela US-5-02), sem registrar payload completo em claro em logs se a politica LGPD da US-5-02 exigir mascaramento.
5. Executar o comando red novamente e confirmar sucesso (green).
6. Refatorar apenas para clareza, mantendo a suite alvo verde.

## comandos_permitidos

- `cd /Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend && PYTHONPATH=/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb:/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_qr_emissao_unitario_payload.py`

## resultado_esperado

- Payload gerado na emissao conforme contrato minimo, com testes unitarios verdes e integracao no fluxo real da US-5-02.

## testes_ou_validacoes_obrigatorias

- `cd /Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend && PYTHONPATH=/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb:/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_qr_emissao_unitario_payload.py`
- Verificacao manual ou por revisao: comparacao campo a campo com `CONTRATO-PAYLOAD-QR.md`.

## stop_conditions

- Parar com `BLOQUEADO` se US-5-02 ainda nao tiver ponto de emissao implementado — nao simular endpoint ficticio.
- Parar se os testes red passarem antes da implementacao.
- Parar se o modelo persistido (US-5-01) nao permitir mapeamento inequivoco documentado no contrato.
