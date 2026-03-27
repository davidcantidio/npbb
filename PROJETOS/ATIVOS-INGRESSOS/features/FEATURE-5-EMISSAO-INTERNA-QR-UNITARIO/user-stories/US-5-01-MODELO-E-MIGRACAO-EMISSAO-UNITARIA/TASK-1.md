---
doc_id: "TASK-1.md"
user_story_id: "US-5-01-MODELO-E-MIGRACAO-EMISSAO-UNITARIA"
task_id: "T1"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on: []
parallel_safe: false
write_scope:
  - "PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-5-EMISSAO-INTERNA-QR-UNITARIO/user-stories/US-5-01-MODELO-E-MIGRACAO-EMISSAO-UNITARIA/ADR-US-5-01-DOMINIO-EMISSAO-UNITARIA.md"
tdd_aplicavel: false
---

# T1 - ADR de dominio: unicidade, identidade canonica e FK destinatario

## objetivo

Fechar as ambiguidades dos criterios 2 e 3 da US (politica ante duplicidade e politica de identidade auditavel) e **nomear explicitamente** a entidade de destinatario e a FK que a migration T2 deve usar, com citacao minima ao [PRD-ATIVOS-INGRESSOS.md](../../../../PRD-ATIVOS-INGRESSOS.md) e ao codigo existente em `backend/app/models/event_support_models.py`, **sem** escrever migracao nem modelos SQLModel.

## precondicoes

- `README.md` desta US lido na integra.
- [FEATURE-5.md](../../FEATURE-5.md) sec. 6 (estrategia 1) e sec. 4 (criterios) revisados.
- Modelos `Convidado`, `SolicitacaoIngresso`, `Convite`, `CotaCortesia` revistos em `backend/app/models/event_support_models.py` e tabela `convidado` / `solicitacao_ingresso` confirmadas no repositorio.

## orquestracao

- `depends_on`: nenhuma task anterior nesta US.
- `parallel_safe`: false (decisoes bloqueiam T2).
- `write_scope`: apenas o ficheiro ADR listado no frontmatter (criar ou substituir rascunho por versao `1.0` aprovada internamente).

## arquivos_a_ler_ou_tocar

- [README.md](./README.md) desta US
- [FEATURE-5.md](../../FEATURE-5.md)
- [PRD-ATIVOS-INGRESSOS.md](../../../../PRD-ATIVOS-INGRESSOS.md) *(trechos 2.3–2.4, glossario `qr_emitido`, hipoteses sobre identidade para validador futuro)*
- `backend/app/models/event_support_models.py`
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-3-CATEGORIAS-E-MODOS-FORNECIMENTO/user-stories/US-3-01-MODELAGEM-PERSISTENCIA-E-DEFAULTS-LEGADO/README.md` *(nomes conceituais de categoria por evento; nomes fisicos de tabela vêm da migration mergeada, não deste README)*

## passos_atomicos

1. Criar `ADR-US-5-01-DOMINIO-EMISSAO-UNITARIA.md` na pasta desta US com estrutura minima: contexto; decisao; consequencias; referencias.
2. **Unicidade (criterio 2 da US)**: escolher **uma** politica fechada — recomendacao alinhada ao PRD (um registro inequivoco por destinatario): **rejeitar** segundo insert no mesmo escopo via `UNIQUE` no banco (ou equivalente documentado) em vez de versionamento multi-linha, salvo justificativa explícita em negocio. Documentar o **escopo exato** da unicidade (colunas que compõem o unique index / constraint), alinhado à categoria por evento entregue por FEATURE-3.
3. **Identidade canonica (criterio 3 da US)**: escolher **uma** politica fechada — recomendacao: coluna **`public_id` (UUID)** gerada na criacao, **imutavel** (nunca atualizada pela aplicacao; PK surrogate `id` int mantida). Documentar que alteracao de “identidade de negocio” exige nova US/fluxo (fora deste corte).
4. **Destinatario**: declarar qual FK materializa “destinatario” na tabela de emissao (ex.: `convidado_id` NOT NULL como pessoa destino, com `solicitacao_ingresso_id` opcional para linhagem operacional, **ou** outra escolha desde que citada ao PRD e ao modelo existente). Proibir deixar o termo “destinatario” sem coluna nomeada.
5. **FEATURE-3**: no ADR, referenciar que a FK de categoria deve apontar para a **PK real** criada pela migration da US-3-01 (ou cadeia equivalente), e listar o nome da tabela/coluna **após** inspecionar o ficheiro em `backend/alembic/versions/` no branch — não inventar nome de tabela se a migration ainda nao existir (nesse caso documentar “pendente merge US-3-01” e bloquear T2 até existir revisao observavel).
6. **Artefatos / storage (PRD sec. 7)**: uma linha no ADR a confirmar que campos de referencia externa ou metadados são **opcionais** na tabela de emissao, sem politica de retencao nesta US.

## comandos_permitidos

- *(nenhum obrigatorio; leitura de ficheiros e grep local permitidos fora desta lista)*

## resultado_esperado

Ficheiro `ADR-US-5-01-DOMINIO-EMISSAO-UNITARIA.md` completo, com decisoes unicas e rastreaveis, desbloqueando T2 com nomes de FK/PK e escopo de `UNIQUE` definidos.

## testes_ou_validacoes_obrigatorias

- Revisao humana: outro membro da equipa consegue implementar T2 apenas lendo o ADR + migrations FEATURE-3, sem reinterpretar a US.

## stop_conditions

- Parar e reportar **BLOQUEADO** se nao for possivel nomear a FK de categoria FEATURE-3 por ausencia de migration no branch.
- Parar se o PRD e o modelo existente nao sustentarem a FK de destinatario escolhida — escalar a PM antes de alterar escopo da US.
