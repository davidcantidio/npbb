Não.

~~Criar backend/app/models/sponsorship_models.py com todas as 13 entidades, enums, relationships e check constraints~~

~~Registrar sponsorship_models nos imports de models.py e alembic/env.py~~

~~Gerar migration Alembic com autogenerate e revisar o resultado~~

~~Rodar testes existentes para garantir que nada quebrou~~

Agora vou registrar o módulo nos imports.

Agora vou gerar a migration Alembic. Preciso verificar o ambiente Python primeiro.

Os imports funcionam. Vou gerar a migration agora.

Agora vou escrever a migration completa com todas as 13 tabelas.

Vou verificar se a migration compila sem erros.

Migration gerada e verificada com sucesso. A cadeia de revisões está correta (`f5e6d7c8b9a0` -> `2a9cfc2167a4`).

Agora vou rodar os testes existentes para garantir que nada quebrou.

536 testes passaram. Os 18 que falharam são todos pré-existentes (backup, lead pipeline, CSV smoke, ETL usecases) -- nenhum relacionado ao módulo de patrocínio. O `AGENTS.md` já documenta falhas pré-existentes em `test_leads_import_etl_usecases.py` e outros.

Tudo concluído. Aqui está o resumo do que foi feito:

---

**Arquivo criado:**

- `backend/app/models/sponsorship_models.py` -- 13 entidades + 8 enums + relationships + check constraints

**Arquivos modificados:**

- `backend/app/models/models.py` -- import do novo módulo no final (mesmo padrão dos outros)
- `backend/alembic/env.py` -- import para autogenerate registrar as tabelas
- `backend/alembic/versions/2a9cfc2167a4_add_sponsorship_contract_module.py` -- migration com CREATE TABLE das 13 tabelas e DROP TABLE no downgrade

**Entidades criadas (na ordem de dependência):**


| **#** | **Tabela**                  | **Propósito**                                                  |
| ----- | --------------------------- | -------------------------------------------------------------- |
| 1     | `sponsored_person`          | Pessoa física (atleta, fisio, médico, etc.)                    |
| 2     | `sponsored_institution`     | Instituição parceira                                           |
| 3     | `social_profile`            | Perfis sociais flexíveis (polimórfico por owner_type)          |
| 4     | `sponsorship_group`         | Squad / grupo de patrocínio                                    |
| 5     | `group_member`              | Membro do grupo (pessoa XOR instituição, com check constraint) |
| 6     | `sponsorship_contract`      | Contrato com PDF, vigência, `replaced_by_contract_id`          |
| 7     | `contract_clause`           | Cláusula com identificador textual livre                       |
| 8     | `counterpart_requirement`   | Contrapartida/obrigação com recorrência parametrizada          |
| 9     | `requirement_occurrence`    | Instância/parcela de cada contrapartida                        |
| 10    | `occurrence_responsible`    | Responsáveis por ocorrência (individual/coletivo)              |
| 11    | `delivery`                  | Entrega feita pelo patrocinado                                 |
| 12    | `delivery_evidence`         | Comprovações da entrega (link, arquivo, post, etc.)            |
| 13    | `contract_extraction_draft` | Rascunho de extração por IA com revisão humana                 |


**Testes:** 536 passaram, 18 falharam (todos pré-existentes, zero regressões).

Para aplicar a migration no banco, basta rodar `alembic upgrade head`.