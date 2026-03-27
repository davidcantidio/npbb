---
doc_id: "TASK-1.md"
user_story_id: "US-5-02-SERVICO-E-API-EMISSAO"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on: []
parallel_safe: false
write_scope:
  - "backend/app/services/"
  - "backend/tests/test_emissao_interna_unitario_service.py"
tdd_aplicavel: true
---

# TASK-1 - Servico de dominio de emissao unitaria interna

## objetivo

Implementar o caso de uso de **emissao interna unitaria** (uma persistencia por operacao de negocio) sobre o modelo entregue pela US-5-01, garantindo regras de elegibilidade alinhadas a categoria em modo interno com QR e retorno de identificador unico coerente com o persistido.

## precondicoes

- [US-5-01](../US-5-01-MODELO-E-MIGRACAO-EMISSAO-UNITARIA/README.md) concluida (`done`): tabelas/entidades de emissao unitaria, migracoes aplicadas e nomes de modelo estabilizados no codigo.
- Ler entidades e relacionamentos introduzidos pela US-5-01 (`backend/app/models/models.py` ou modulos extraidos) antes de implementar.

## orquestracao

- `depends_on`: nenhuma task anterior na mesma US.
- `parallel_safe`: `false` (base para todas as tasks seguintes).
- `write_scope`: conforme frontmatter; o ficheiro de servico pode ser criado com nome final acordado na implementacao (ex. `backend/app/services/emissao_interna_unitario.py`) desde que permaneca sob `backend/app/services/`.

## arquivos_a_ler_ou_tocar

- `backend/app/models/models.py` *(entidades US-5-01)*
- `backend/app/db/database.py`, `backend/app/db/session.py` *(padrao de sessao)*
- `backend/app/services/` *(padroes de outros servicos)*
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-5-EMISSAO-INTERNA-QR-UNITARIO/FEATURE-5.md` *(sec. 2, 6, 7)*
- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` *(trechos 2.3–2.4, LGPD 2.6 — sem alargar escopo)*

## testes_red

- testes_a_escrever_primeiro:
  - Teste de servico (sessao SQLite em memoria como em `tests/test_ingressos_endpoints.py`) que, dado evento/diretoria/categoria em modo interno com QR e destinatario elegivel, **cria exatamente um** registro de emissao e retorna o identificador unico esperado.
  - Teste que reproduz tentativa de violar unicidade ou regra de negocio documentada na US-5-01 e espera falha controlada (excecao ou resultado de rejeicao), sem duplicata indevida.
- comando_para_rodar:
  - `cd backend && PYTHONPATH="${PWD}/..:${PWD}" SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_emissao_interna_unitario_service.py -q`
- criterio_red:
  - Os testes acima devem falhar antes da implementacao do servico; se passarem sem implementacao, parar e revisar a task.

## passos_atomicos

1. Escrever os testes listados em `testes_red`.
2. Rodar os testes e confirmar falha inicial (red).
3. Implementar servico de dominio (funcoes ou classe) que receba `Session` e parametros de negocio, valide precondicoes (categoria/modalidade interna+QR conforme FEATURE-3), persista **uma** emissao e devolva o identificador unico.
4. Rodar os testes e confirmar sucesso (green).
5. Refatorar se necessario mantendo a suite green.

## comandos_permitidos

- `cd backend && PYTHONPATH="${PWD}/..:${PWD}" SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_emissao_interna_unitario_service.py -q`
- `cd backend && ruff check app/services/ app/models/models.py`

## resultado_esperado

- Servico utilizavel pela camada API (TASK-2) com contrato Python claro (tipos, excecoes de negocio).
- Criterio **Given/When/Then** da US sobre persistencia unitaria verificavel por testes de servico.

## testes_ou_validacoes_obrigatorias

- Suite `tests/test_emissao_interna_unitario_service.py` verde.
- Nenhum dado sensivel (payload de QR completo, PII em claro) escrito em logs dentro do servico nesta task — detalhamento de auditoria fica para TASK-5.

## stop_conditions

- Parar e reportar `BLOQUEADO` se o modelo da US-5-01 nao estiver merged ou nomes de tabela/campo ainda instaveis.
- Parar se o PRD ou FEATURE-5 exigirem regra de negocio nao descrita na US-5-02 (escopo novo).
