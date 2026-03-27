---
doc_id: "TASK-3.md"
user_story_id: "US-5-03-CONTRATO-MINIMO-PAYLOAD-QR"
task_id: "T3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "backend/tests/test_qr_emissao_unitario_payload.py"
  - "backend/tests/fixtures/qr_payload_min_v1.json"
  - "PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-5-EMISSAO-INTERNA-QR-UNITARIO/CONTRATO-PAYLOAD-QR.md"
tdd_aplicavel: true
---

# TASK-3 - Golden file e validacao de contrato na resposta de emissao

## objetivo

Fechar a US com evidencia automatizada de **forma** do payload (golden file nao sensivel) e, quando aplicavel, assercao na resposta HTTP da API de emissao, garantindo que o segundo e terceiro criterios Given/When/Then permanecem verificaveis em CI.

## precondicoes

- **T2** concluida: builder integrado e testes unitarios base em verde.
- Endpoint de emissao da US-5-02 disponivel em ambiente de teste (SQLite com `TESTING=true`).

## orquestracao

- `depends_on`: `T2` deve estar `done`.
- `parallel_safe`: `false`.
- `write_scope`: ficheiros de teste e fixture; ajustar nome do ficheiro de teste se a suite for fundida com a criada em T2, mantendo um unico modulo de teste coerente.

## arquivos_a_ler_ou_tocar

- [CONTRATO-PAYLOAD-QR.md](../../CONTRATO-PAYLOAD-QR.md)
- [TASK-2.md](./TASK-2.md)
- `backend/tests/test_qr_emissao_unitario_payload.py`
- `backend/tests/fixtures/qr_payload_min_v1.json` *(criar — conteudo com IDs ficticios)*
- Rotas e clientes de teste existentes para chamadas autenticadas a API de emissao *(caminho a confirmar na US-5-02)*

## testes_red

- testes_a_escrever_primeiro:
  - teste que carrega `qr_payload_min_v1.json` e valida que o payload normalizado da emissao (ou do builder) coincide com a forma esperada (chaves obrigatorias, tipos, ausencia de campos proibidos pelo contrato).
  - opcional se a US-5-02 expuser emissao via API em teste: teste HTTP que conclui emissao e assegura que o corpo contem o payload conforme contrato, sem dados sensiveis em excesso ao definido no doc.
- comando_para_rodar:
  - `cd /Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend && PYTHONPATH=/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb:/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_qr_emissao_unitario_payload.py`
- criterio_red:
  - os cenarios novos devem falhar ate a fixture e a implementacao estarem alinhados; se falharem por motivo externo (auth, migracao), parar e corrigir precondicoes de teste antes de mudar o contrato.

## passos_atomicos

1. Criar `backend/tests/fixtures/qr_payload_min_v1.json` alinhado ao exemplo nao sensivel de `CONTRATO-PAYLOAD-QR.md`.
2. Escrever os testes listados em `testes_red` (extensao do ficheiro de teste de T2 ou modulo dedicado, sem duplicar assercoes redundantes).
3. Rodar o comando red e confirmar falha inicial esperada.
4. Ajustar normalizacao ou ordem de chaves na serializacao apenas se necessario para compatibilidade estavel com o golden file, documentando no contrato se a ordem for significativa.
5. Rodar o comando e confirmar green.
6. Atualizar `CONTRATO-PAYLOAD-QR.md` se o golden file oficializar um detalhe antes apenas implicito (ex.: formato de encoding), sem alargar semantica.

## comandos_permitidos

- `cd /Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend && PYTHONPATH=/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb:/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_qr_emissao_unitario_payload.py`

## resultado_esperado

- Golden file versionado e testes verdes que impedem regressao de forma do payload; documento de contrato referenciando o fixture quando fizer sentido.

## testes_ou_validacoes_obrigatorias

- `cd /Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend && PYTHONPATH=/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb:/Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_qr_emissao_unitario_payload.py`
- Confirmar que nenhum segredo ou PII real foi commitado na fixture.

## stop_conditions

- Parar se a emissao via API nao for testavel sem US-5-02 completa — limitar escopo a validacao do builder + golden file e registar a limitacao no handoff da US.
- Parar se a normalizacao JSON exigir semantica nao descrita no contrato.
