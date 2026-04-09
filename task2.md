Contexto no plan.md
Task 1 pede ConfiguracaoIngressoEvento com um registro por evento (unique em evento_id) e, noutro TODO, AuditoriaIngressoEvento só para mudanças de modo de fornecimento.
Task 2 confirma: alteração de modo via PATCH deve inserir linha em AuditoriaIngressoEvento (utilizador, modo antigo, modo novo).
O item que citaste junta “config + tipos ativos + modo + auditoria de modo”. No plano canónico, a auditoria não fica dentro da tabela de configuração: é tabela à parte, apenas para histórico de modo_fornecimento.

Dependências
Enums (TODO imediatamente anterior no plan.md): TipoIngresso, ModoFornecimento em models.py (ou enums.py), com valores snake_case iguais ao DDL Postgres (tipoingresso, modofornecimento, etc.), como em task1-modelos_dominio_migracoes.md.
Ficheiro de modelos: backend/app/models/ingressos_v2_models.py (nome no plan.md; o doc da task também menciona ingressos_operacao_models.py — escolher um e manter consistente com imports em models.py / alembic/env.py).
Modelagem proposta
1. ConfiguracaoIngressoEvento (cabeçalho por evento)
Campo	Notas
id
PK
evento_id
FK → evento.id, UniqueConstraint (um config por evento)
modo_fornecimento
ModoFornecimento (interno vs externo)
created_at / updated_at
default_factory=now_utc como em event_support_models.py
Relações SQLModel: Evento (opcional back_populates se adicionares lista em Evento); coleção para as linhas de tipos (abaixo).

Opcional para auditoria genérica de “quem alterou a config” (não substitui a auditoria de modo): updated_by_usuario_id FK → usuario.id. O plan.md da Task 2 foca AuditoriaIngressoEvento para mudança de modo; este campo é só se quiseres rastrear último editor da config completa.

2. Ligação a tipos de ingresso ativos
Um único registro de config não deve guardar tipos num JSON se quiseres FKs, unicidade e validação limpa. Padrão recomendado:

ConfiguracaoIngressoEventoTipo (ou nome equivalente), uma linha por (configuracao_id, tipo_ingresso):
configuracao_id FK → configuracao_ingresso_evento.id (cascade ao apagar config, ou restrict conforme regra de negócio)
tipo_ingresso → enum TipoIngresso
ativo bool (default True se só guardares os “ativos”; ou todos os tipos elegíveis com flag)
ordem int (ordem de apresentação)
UniqueConstraint(configuracao_id, tipo_ingresso)
Assim cumpres: “links evento to its active ticket types” via 1 config → N tipos, sem duplicar evento_id nas linhas de tipo (fica derivado pela config).

Alternativa do doc interno (task1): tabelas evento_modo_fornecimento + evento_tipo_ingresso com evento_id em ambas. É equivalente; a variante com FK à config evita inconsistência (tipos sem linha de config).

3. AuditoriaIngressoEvento (trilha só para mudanças de modo)
Campo	Notas
id
PK
evento_id
FK → evento.id (index) — permite listar histórico por evento sem join obrigatório à config
modo_anterior
ModoFornecimento (nullable na primeira definição de modo, se quiseres registar “bootstrap”; senão só escreves auditoria em transições)
modo_novo
ModoFornecimento
usuario_id
FK → usuario.id (quem fez a alteração)
created_at
timestamp do evento (só created_at costuma bastar; não precisa updated_at se for append-only)
Regra de produto (para alinhar com Task 2): em POST inicial da config, podes não criar auditoria ou criar uma linha com modo_anterior=None e modo_novo=.... Em PATCH de modo, sempre uma linha nova com old/new + user.

Migração Alembic
Criar tabelas com sa.Enum(..., name='modofornecimento') e tipoingresso alinhados aos .value Python.
Índices: evento_id na config (unique já indexa); evento_id na auditoria; FKs com índice onde o ORM filtrar por FK.
Não alterar cota_cortesia / solicitacao_ingresso (requisito global da Task 1).
Verificação (do próprio plan.md + este item)
Migração sobe/desce sem tocar no legado.
Impossível ter duas configs para o mesmo evento_id.
Tipos por evento respeitam unicidade (config, tipo).
Modelos importados onde o Alembic carrega metadata (padrão atual do repo).
Escopo fora deste item (só referência)
Endpoints e PATCH com escrita na auditoria → Task 2.
Validação “só tipos declarados na config são válidos” → Task 2 / serviços posteriores.
Resumo: implementa ConfiguracaoIngressoEvento (modo + 1:1 com evento), tabela filha para tipos ativos com UniqueConstraint, e AuditoriaIngressoEvento como trilha append-only de mudanças de modo_fornecimento, tal como o plan.md separa nos TODOs mas a Task 2 trata como um fluxo único na API.