Task 1: modelos de domínio e migrações (ativos/ingressos operação)

Contexto no código





Enums estáveis e modelos core: secção inicial de backend/app/models/models.py (ex.: SolicitacaoIngressoStatus, TipoPergunta como str, Enum).



Legado de cortesias: backend/app/models/event_support_models.py (CotaCortesia, SolicitacaoIngresso) — não alterar comportamento; o novo desenho convive em tabelas novas.



Metadados Alembic: backend/alembic/env.py importa app.models.models; qualquer módulo novo precisa ser importado a partir de backend/app/models/models.py (padrão já usado com event_support_models).



Padrão de migração com sa.Enum(..., name='...'): backend/alembic/versions/c0d63429d56d_add_lead_evento_table_for_issue_f1_01_.py.



Head Alembic: há ramificações no histórico; antes de fixar down_revision, executar cd backend && alembic heads e anexar a nova revisão ao head atual (ou criar merge se existir mais de um head).

1. Enums Python (TODO explícito)

Declarar em backend/app/models/models.py (bloco “ENUMS DE DOMÍNIO”), com valores string iguais aos identificadores do intake (snake_case, sem acentos), e nomes de membros em UPPER_SNAKE:







Classe



Valores (.value)





TipoIngresso



pista, pista_premium, camarote





ModoFornecimento



interno_emitido_com_qr, externo_recebido





StatusInventario



planejado, recebido_confirmado, bloqueado_por_recebimento, disponivel, distribuido





StatusDestinatario



enviado, confirmado, utilizado, cancelado





TipoOcorrencia



entrega_errada, quantidade_divergente, destinatario_invalido, outro





TipoAjuste



aumento, reducao, remanejamento

Nomes dos tipos Postgres na migração (alinhados ao estilo existente, minúsculos): por exemplo tipoingresso, modofornecimento, statusinventario, statusdestinatario, tipoocorrencia, tipoajuste — os literais do ENUM devem coincidir com os .value acima para o ORM e o DDL ficarem alinhados.

2. Modelos de tabela (novo módulo)

Criar um ficheiro dedicado, por exemplo backend/app/models/ingressos_operacao_models.py, importando SQLModel de app.db.metadata, now_utc e os novos enums de app.models.models, espelhando o estilo de backend/app/models/event_support_models.py.

Proposta mínima que usa todos os enums e cobre o texto da Task 1 / intake (sem implementar ainda regras de negócio):

erDiagram
  Evento ||--o| EventoModoFornecimento : config
  Evento ||--o{ EventoTipoIngresso : catalogo
  Evento ||--o{ IngressoEstoqueLinha : saldo_por_diretoria_tipo
  Diretoria ||--o{ IngressoEstoqueLinha : saldo_por_diretoria_tipo
  IngressoEstoqueLinha ||--o{ IngressoUnidade : unidades
  IngressoUnidade ||--o| IngressoDestinatario : atribuicao
  Evento ||--o{ IngressoAjuste : ajustes
  Evento ||--o{ IngressoOcorrencia : ocorrencias





evento_modo_fornecimento: uma linha por evento_id (unique), campo modo: ModoFornecimento, created_at / updated_at (e opcional updated_by_usuario_id FK usuario.id para suportar auditoria futura).



evento_tipo_ingresso: catálogo por evento — evento_id, tipo: TipoIngresso, ativo: bool, ordem: int; UniqueConstraint(evento_id, tipo).



ingresso_estoque_linha: grão evento + diretoria + tipo — quantidade_planejada, quantidade_recebida_confirmada (default 0); UniqueConstraint(evento_id, diretoria_id, tipo_ingresso); FKs para evento, diretoria.



ingresso_unidade: ingresso unitário — FK estoque_linha_id, status: StatusInventario, qr_token opcional (UUID ou String(36)), timestamps.



ingresso_destinatario: ciclo de vida do destinatário — FK unidade_id com unique (1:1), nome, email, status: StatusDestinatario, timestamps.



ingresso_ajuste: evento_id, tipo: TipoAjuste, FKs opcionais estoque_linha_origem_id / estoque_linha_destino_id, quantidade: int (semântica documentada num comentário curto: valor absoluto da movimentação; sinal inferido pelo TipoAjuste na camada de aplicação), created_at, usuario_id opcional, correlation_id opcional (String, index).



ingresso_ocorrencia: evento_id, tipo: TipoOcorrencia, descricao (Text), FKs opcionais a ingresso_estoque_linha / ingresso_unidade, created_at, usuario_id opcional.

Relações Relationship apenas onde forem úteis e consistentes com o resto do projeto; índices em evento_id nas tabelas filhas.

No final de backend/app/models/models.py, reexportar as classes novas (como já é feito para CotaCortesia, etc.) para manter um único ponto de import para código existente.

3. Migração Alembic





Nova revisão em backend/alembic/versions/ com upgrade() que:





Cria os seis tipos ENUM no Postgres (via sa.Enum(...).create(op.get_bind()) ou op.create_table com colunas sa.Enum, seguindo o padrão do ficheiro c0d63429d56d citado).



Cria as tabelas na ordem correta de FKs.



Cria índices/uniques nomeados (o metadata já usa NAMING_CONVENTION).



downgrade(): eliminar tabelas na ordem inversa; eliminar tipos ENUM (DROP TYPE) onde o dialect for Postgres.

4. Verificação





alembic upgrade head contra uma base Postgres de desenvolvimento (com DATABASE_URL / DIRECT_URL conforme docs/SETUP.md).



cd backend && PYTHONPATH=... SECRET_KEY=... TESTING=true python -m pytest backend/tests/test_ingressos_endpoints.py backend/tests/test_ativos_endpoints.py -q (regressão do legado).



Opcional: SQLModel.metadata.create_all num engine SQLite de teste (fixture em backend/tests/conftest.py) para confirmar que os novos modelos não quebram create_all — os enums existentes (SolicitacaoIngressoTipo) já funcionam assim.

Notas de escopo





Fora desta task: APIs, serviços de conciliação/bloqueio automático, PDF/QR, e-mail e dashboard — apenas persistência e tipos.



Transição: nenhuma FK obrigatória de ingresso_* para cota_cortesia no v1; ligação futura pode ser campo opcional ou camada de aplicação.

