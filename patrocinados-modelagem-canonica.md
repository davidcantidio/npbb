# Patrocinios e Contrapartidas - Modelagem Canonica e Regras de Negocio

## Proposito e Precedencia

Este arquivo e a fonte de verdade de modelagem de banco e regras de negocio do modulo de patrocinios/contrapartidas.

Em caso de conflito, prevalece este documento sobre artefatos temporarios e sobre inferencias do codigo atual.

Fonte principal: `patrocinados-contrapartidas-intake.md`.

Objetivo: permitir que outro engenheiro ou outra IA modele, revise ou evolua o banco de dados e o fluxo operacional do modulo sem precisar reabrir o transcript original.

## Contexto e Objetivo do Modulo

O modulo existe para verificar a entrega das contrapartidas estabelecidas em contratos de patrocinio.

O patrocinador considerado neste contexto e unico e fixo: Banco do Brasil. Portanto, o modelo atual nao precisa de uma entidade dedicada de patrocinador para suportar a regra de negocio central.

O dominio precisa suportar:

- contratos de patrocinio com vigencia, numero e arquivo original;
- clausulas contratuais relevantes para obrigacoes;
- contrapartidas previstas em contrato;
- grupos de patrocinio que podem incluir pessoas e instituicoes;
- responsaveis especificos por cumprimento;
- recorrencia de obrigacoes ao longo do tempo;
- entregas e suas evidencias;
- validacao operacional das entregas;
- extracoes assistidas por IA com revisao humana obrigatoria.

## Glossario Canonico

### Contrato

Documento contratual de patrocinio que estabelece vigencia, numero, clausulas e obrigacoes. O contrato pode substituir outro contrato anterior por meio de `replaced_by_contract_id`, sem apagar o historico operacional.

### Clausula

Trecho contratual relevante para obrigacao. A clausula precisa ser persistida no banco para preservar rastreabilidade entre o texto contratual e a contrapartida que dele decorre. O identificador da clausula e textual e livre, porque a numeracao depende da redacao do contrato.

### Contrapartida

Obrigacao ou demanda prevista no contrato. Nao e a comprovacao do cumprimento. A contrapartida aponta para uma unica clausula do contrato e possui descricao, tipo livre e regra temporal propria.

### Ocorrencia da Contrapartida

Cada instancia esperada de execucao de uma contrapartida. E a peca central para lidar com recorrencia, prazo, responsabilidade e validacao. Toda entrega operacional cumpre uma ocorrencia, nunca a contrapartida abstrata diretamente.

### Entrega

O que o patrocinado devolve para cumprir uma ocorrencia de contrapartida. A entrega possui descricao e observacoes. Uma mesma ocorrencia pode receber uma ou mais entregas, e uma entrega pode possuir multiplas evidencias.

### Evidencia

Comprovacao da entrega. Pode assumir formatos diferentes, como link, arquivo, texto, post social, imagem ou outro formato equivalente.

### Grupo de Patrocinio

Entidade propria que representa o conjunto patrocinado em um contrato. Um grupo pode corresponder a um atleta isolado ou a um squad. O mesmo grupo pode conter pessoas e instituicoes.

### Membro do Grupo

Vinculo entre um grupo de patrocinio e uma entidade patrocinada. Um membro do grupo e exatamente uma pessoa ou exatamente uma instituicao, nunca ambos ao mesmo tempo.

### Pessoa

Pessoa fisica participante do escopo patrocinado. Pode ser atleta, medico, fisioterapeuta, fotografo, membro de comissao tecnica ou outro membro relevante da equipe.

### Instituicao

Instituicao parceira ou outro parceiro que tambem pode estar dentro do escopo patrocinado e assumir obrigacoes no contrato.

### Perfil Social

Cadastro flexivel de rede social para pessoa ou instituicao. O modelo nao deve usar campo fixo de Instagram; deve suportar plataforma, handler e URL de forma extensivel.

### Rascunho de Extracao por IA

Registro intermediario produzido a partir do PDF do contrato. Serve para pre-preenchimento, revisao e auditoria. Nao equivale ao contrato validado nem deve gravar diretamente nas tabelas finais sem revisao humana.

## Regras de Negocio Canonicas

### 1. Contratos

- O contrato e a entidade raiz do dominio de obrigacoes.
- O contrato deve possuir, no minimo, `contract_number`, `start_date`, `end_date` e referencia ao arquivo original.
- O arquivo original do contrato deve ficar preservado em file storage, com metadados suficientes para rastreabilidade.
- O modelo atual nao exige cadastro de valor financeiro do contrato.
- Um novo contrato pode substituir um contrato anterior por meio de `replaced_by_contract_id`.
- A substituicao de contrato nao deve apagar historico operacional anterior.
- Na pratica de negocio, o contrato novo passa a ser o vigente; o contrato anterior permanece auditavel.

### 2. Clausulas

- Clausulas que geram obrigacoes devem ser persistidas no banco.
- Nao e necessario representar juridicamente o contrato inteiro no banco.
- O sistema deve extrair ou cadastrar apenas as clausulas que geram obrigacao, mantendo referencia ao PDF completo em storage.
- A clausula deve ter identificador textual livre, por exemplo: `2`, `2.1`, `2.I`, `Clausula Quinta`.
- O modelo nao deve impor padrao fixo de numeracao.

### 3. Contrapartidas

- Contrapartida e a descricao da demanda que existe no contrato.
- Contrapartida nao e entrega.
- Cada contrapartida pertence a um contrato e a uma unica clausula.
- Cada contrapartida deve ter prazo proprio.
- Em contrapartidas recorrentes, o prazo operacional deve se materializar em cada ocorrencia.
- O tipo de contrapartida e arbitrario e preenchido manualmente.
- A obrigacao e do patrocinado entregar, nao do patrocinador.
- O responsavel pela contrapartida precisa ser membro do grupo associado ao contrato.

### 4. Recorrencia

- A contrapartida pode ser unica ou recorrente.
- Quando houver recorrencia, ela nao e livre no caos; ela esta relacionada a um periodo de referencia.
- Os periodos canonicos sao: `week`, `month`, `year`, `contract_term` e `custom`.
- O modelo deve registrar:
  - se a contrapartida e recorrente;
  - o tipo de periodo;
  - a descricao textual da regra contratual;
  - a quantidade esperada de ocorrencias, quando aplicavel;
  - datas de inicio e fim da recorrencia, quando aplicavel.
- Exemplos validos:
  - 1 entrega por mes;
  - 2 ativacoes por ano;
  - 1 publicacao por semana durante 3 meses;
  - 3 aparicoes ao longo da vigencia;
  - entregas em datas especificas previstas em contrato.

### 5. Ocorrencias

- A recorrencia nao deve ser modelada diretamente na entrega.
- Deve existir uma entidade propria de ocorrencia da contrapartida.
- Cada ocorrencia representa uma execucao esperada daquela obrigacao.
- Cada ocorrencia deve ter, no minimo, identificacao de periodo e prazo quando houver.
- Mesmo quando a contrapartida nao for recorrente, o cumprimento operacional deve acontecer por meio de uma ocorrencia rastreavel.
- A ocorrencia e a unidade operacional para:
  - prazo;
  - responsabilidade individual ou coletiva;
  - status;
  - validacao;
  - rejeicao;
  - reenvio ou nova entrega.

### 6. Responsabilidade Individual e Coletiva

- A responsabilidade pode ser `individual` ou `collective`.
- Se for `individual`, a ocorrencia deve ter exatamente 1 responsavel.
- Se for `collective`, a ocorrencia deve ter 2 ou mais corresponsaveis.
- Os responsaveis devem ser membros do grupo do contrato.
- O modelo deve suportar `is_primary` e uma descricao opcional do papel do responsavel.
- A responsabilidade deve ficar associada a ocorrencia, nao apenas a contrapartida abstrata, porque a composicao real pode variar por periodo.

### 7. Entregas

- Entrega e o que foi devolvido pelo patrocinado para cumprir uma ocorrencia.
- A entrega deve ter descricao.
- A entrega deve permitir observacoes livres.
- As observacoes citadas inicialmente como "observacoes do periodo" ficam canonizadas como observacoes da entrega, com possibilidade complementar de notas internas na validacao da ocorrencia.
- Uma ocorrencia pode ter multiplas entregas, se necessario.

### 8. Evidencias

- Uma entrega pode ter mais de uma forma de comprovacao.
- Tipos canonicos de evidencia:
  - `link`
  - `file`
  - `text`
  - `social_post`
  - `image`
  - `other`
- A evidencia deve suportar, quando fizer sentido:
  - URL;
  - referencia ao arquivo no storage;
  - descricao;
  - plataforma;
  - identificador externo;
  - data de postagem.

### 9. Status Operacionais

- O dominio precisa distinguir status da contrapartida e status da ocorrencia.
- No modelo canonico, o status operacional principal fica na ocorrencia; a entrega nao precisa ter status proprio obrigatorio.
- Status canonicos da contrapartida:
  - `planned`
  - `in_progress`
  - `fulfilled`
  - `expired`
- Semantica de negocio correspondente:
  - planejada;
  - em andamento;
  - cumprida;
  - vencida.
- Status canonicos da ocorrencia:
  - `pending`
  - `in_review`
  - `delivered`
  - `validated`
  - `rejected`
- Semantica de negocio correspondente:
  - pendente;
  - em analise;
  - entregue;
  - validada;
  - rejeitada.
- `atrasada` deve ser tratada como condicao temporal derivada de prazo vencido com status ainda nao final, e nao como etapa canonica obrigatoria persistida.

### 10. Validacao, Rejeicao e Reversao

- Qualquer usuario do sistema pode validar, rejeitar e reverter validacoes por enquanto.
- O modelo deve registrar quem validou e quando validou.
- Rejeicao exige motivo obrigatorio.
- O modelo deve permitir notas internas da validacao.
- O fluxo deve permitir revisao posterior e reversao de status quando necessario.

### 11. Pessoas, Instituicoes e Redes Sociais

- O grupo de patrocinio pode incluir atletas, membros de comissao tecnica, profissionais de apoio, instituicoes parceiras e outros parceiros.
- Um mesmo contrato pode patrocinar um atleta e, ao mesmo tempo, incluir instituicoes e outras pessoas no mesmo grupo.
- Redes sociais devem ser modeladas em tabela flexivel por pessoa ou instituicao.
- O modelo deve suportar ao menos `platform`, `handle`, `url` e um marcador de perfil principal.

### 12. Extracao por IA

- O upload do contrato em PDF seguido de extracao por IA e uma arquitetura valida.
- A IA deve extrair apenas clausulas que geram obrigacao.
- O resultado da IA deve ser salvo como rascunho de importacao.
- A IA nao deve gravar diretamente nas tabelas finais sem revisao humana.
- O usuario deve revisar, editar e aprovar antes da persistencia final.
- O rascunho deve preservar rastreabilidade de origem e confianca da extracao.

### 13. Patrocinador Fixo

- O patrocinador considerado no escopo atual e apenas o Banco do Brasil.
- Portanto, o modelo atual nao precisa abrir generalizacao para multiplos patrocinadores neste modulo.

## Modelo de Dados Canonico

### Entidades Principais

| Entidade canonica | Papel no dominio | Relacoes principais |
| --- | --- | --- |
| `sponsored_person` | Pessoa fisica patrocinada ou participante do grupo | participa de `group_member`, possui `social_profile` |
| `sponsored_institution` | Instituicao parceira participante do grupo | participa de `group_member`, possui `social_profile` |
| `social_profile` | Perfil social flexivel por owner | pertence a pessoa ou instituicao |
| `sponsorship_group` | Grupo ou squad patrocinado | possui membros e contratos |
| `group_member` | Vinculo entre grupo e pessoa/instituicao | pertence a um grupo e referencia exatamente um owner |
| `sponsorship_contract` | Contrato de patrocinio | pertence a um grupo, possui clausulas, contrapartidas e drafts |
| `contract_clause` | Clausula obrigacional persistida | pertence a um contrato, fundamenta contrapartidas |
| `counterpart_requirement` | Contrapartida prevista em contrato | pertence a contrato e clausula, gera ocorrencias |
| `requirement_occurrence` | Instancia esperada da contrapartida | pertence a contrapartida, possui responsaveis, entregas e validacao |
| `occurrence_responsible` | Responsavel por ocorrencia | vincula ocorrencia a membro do grupo |
| `delivery` | Entrega realizada para cumprir ocorrencia | pertence a ocorrencia, possui evidencias |
| `delivery_evidence` | Comprovacao da entrega | pertence a entrega |
| `contract_extraction_draft` | Rascunho de extracao por IA | pertence a contrato, aguarda revisao |

### Campos Canonicos por Entidade

### `sponsored_person`

- identificacao da pessoa;
- papel funcional livre, por exemplo atleta, medico, fisioterapeuta, fotografo ou outro;
- dados de contato opcionais;
- observacoes;
- timestamps de criacao e atualizacao.

### `sponsored_institution`

- identificacao da instituicao;
- dados cadastrais e de contato opcionais;
- observacoes;
- timestamps de criacao e atualizacao.

### `social_profile`

- `owner_type`;
- `owner_id`;
- `platform`;
- `handle`;
- `url`;
- `is_primary`;
- `created_at`.

### `sponsorship_group`

- nome e descricao;
- timestamps de criacao e atualizacao.

### `group_member`

- `group_id`;
- exatamente um entre `person_id` e `institution_id`;
- `role_in_group`;
- datas de entrada e saida;
- referencia para rastrear responsabilidades futuras.

### `sponsorship_contract`

- `contract_number`;
- `group_id`;
- `start_date`;
- `end_date`;
- `status`;
- `file_storage_key`;
- `original_filename`;
- `file_checksum`;
- `uploaded_at`;
- `replaced_by_contract_id`;
- `created_by_user_id`;
- timestamps de criacao e atualizacao.

### `contract_clause`

- `contract_id`;
- `clause_identifier` textual livre;
- `title` opcional;
- `clause_text`;
- `display_order`;
- `page_reference`;
- `created_at`.

### `counterpart_requirement`

- `contract_id`;
- `clause_id`;
- `requirement_type` livre;
- `description`;
- `is_recurring`;
- `period_type`;
- `period_rule_description`;
- `expected_occurrences`;
- `recurrence_start_date`;
- `recurrence_end_date`;
- `responsibility_type`;
- `status`;
- timestamps de criacao e atualizacao.

### `requirement_occurrence`

- `requirement_id`;
- `period_label`;
- `due_date`;
- `responsibility_type`;
- `status`;
- `validated_by_user_id`;
- `validated_at`;
- `rejection_reason`;
- `internal_notes`;
- timestamps de criacao e atualizacao.

### `occurrence_responsible`

- `occurrence_id`;
- `member_id`;
- `is_primary`;
- `role_description`.

### `delivery`

- `occurrence_id`;
- `description`;
- `observations`;
- `delivered_at`;
- `created_by_user_id`;
- timestamps de criacao e atualizacao.

### `delivery_evidence`

- `delivery_id`;
- `evidence_type`;
- `url`;
- `file_storage_key`;
- `description`;
- `platform`;
- `external_id`;
- `posted_at`;
- `created_at`.

### `contract_extraction_draft`

- `contract_id`;
- `extraction_run_id`;
- `source_page`;
- `source_text_excerpt`;
- `extracted_clause_identifier`;
- `extracted_clause_text`;
- `extracted_requirement_description`;
- `extracted_requirement_type`;
- `extracted_responsible_hint`;
- `extracted_due_date_hint`;
- `confidence_score`;
- `review_status`;
- `reviewed_by_user_id`;
- `reviewed_at`;
- `created_at`.

### Cardinalidades Canonicas

- Um grupo possui muitos membros.
- Um membro pertence a um unico grupo por registro de vinculo.
- Um grupo possui muitos contratos.
- Um contrato pertence a um unico grupo.
- Um contrato possui muitas clausulas.
- Um contrato possui muitas contrapartidas.
- Uma clausula pode fundamentar muitas contrapartidas, mas cada contrapartida aponta para uma unica clausula.
- Uma contrapartida possui uma ou muitas ocorrencias operacionais ao longo da vida util do requisito.
- Uma ocorrencia possui um ou muitos responsaveis, conforme `responsibility_type`.
- Uma ocorrencia pode possuir uma ou muitas entregas.
- Uma entrega pode possuir uma ou muitas evidencias.
- Um contrato pode possuir muitos rascunhos de extracao por IA.

### Enums Canonicos

### `ContractStatus`

- `active`
- `inactive`
- `archived`

### `PeriodType`

- `week`
- `month`
- `year`
- `contract_term`
- `custom`

### `ResponsibilityType`

- `individual`
- `collective`

### `RequirementStatus`

- `planned`
- `in_progress`
- `fulfilled`
- `expired`

### `OccurrenceStatus`

- `pending`
- `in_review`
- `delivered`
- `validated`
- `rejected`

### `EvidenceType`

- `link`
- `file`
- `text`
- `social_post`
- `image`
- `other`

### Campos Derivados e Leitura de Negocio

- `atrasada` e derivado de `due_date` vencida com status nao final.
- contagens como total de grupos, contratos, clausulas, contrapartidas e ocorrencias sao leituras derivadas, nao a fonte primaria da regra.

## Fluxos Canonicos

### Fluxo 1 - Cadastro Manual

1. Cadastrar pessoa e/ou instituicao.
2. Cadastrar perfis sociais flexiveis do owner.
3. Criar grupo de patrocinio.
4. Vincular membros ao grupo.
5. Criar contrato vinculado ao grupo.
6. Registrar metadados e arquivo do contrato.
7. Cadastrar clausulas obrigacionais relevantes.
8. Cadastrar contrapartidas, apontando cada uma para uma unica clausula.
9. Gerar ocorrencias conforme a regra temporal.
10. Vincular responsaveis por ocorrencia.
11. Registrar entregas.
12. Registrar evidencias.
13. Validar, rejeitar ou reverter conforme o caso.

### Fluxo 2 - Importacao Assistida por IA

1. Usuario sobe o PDF do contrato.
2. O arquivo e armazenado em file storage.
3. A IA extrai somente clausulas que geram obrigacao e metadados relevantes.
4. O sistema salva o resultado em `contract_extraction_draft`.
5. O usuario revisa, edita e aprova manualmente.
6. So apos aprovacao o sistema grava contrato, clausulas, contrapartidas, ocorrencias e vinculos operacionais finais.

## Regras de Integridade Canonicas

- `group_member` deve obedecer XOR: exatamente um entre pessoa e instituicao.
- O responsavel de uma ocorrencia deve ser membro do grupo do contrato ao qual a contrapartida pertence.
- Cada contrapartida deve apontar para uma unica clausula.
- Entrega sempre pertence a uma ocorrencia.
- Evidencia sempre pertence a uma entrega.
- Rejeicao exige `rejection_reason`.
- Se `responsibility_type = individual`, deve existir exatamente 1 responsavel.
- Se `responsibility_type = collective`, devem existir 2 ou mais responsaveis.
- Substituicao de contrato nao pode apagar o historico operacional do contrato anterior.
- O PDF original e sua referencia de storage devem ser preservados para auditoria.

## Aderencia com a Implementacao Atual

Referencias verificadas:

- `backend/app/models/sponsorship_models.py`
- `backend/app/routers/sponsorship.py`
- `frontend/src/types/sponsorship.ts`

### Ja Implementado

- Entidades centrais do dominio ja existem no modelo: pessoas, instituicoes, perfis sociais, grupos, membros, contratos, clausulas, contrapartidas, ocorrencias, responsaveis, entregas, evidencias e rascunho de extracao.
- Os enums principais de contrato, periodo, responsabilidade, contrapartida, ocorrencia e evidencia ja existem no backend e no frontend.
- O contrato ja possui `replaced_by_contract_id`.
- Clausula com identificador textual livre ja esta modelada.
- Redes sociais flexiveis por `owner_type` e `owner_id` ja estao modeladas.
- A entidade de ocorrencia ja existe e ocupa o papel operacional central entre contrapartida e entrega.
- O XOR de `group_member` entre pessoa e instituicao ja esta modelado no banco e reforcado no router.
- `delivery` pertence a `requirement_occurrence` e `delivery_evidence` pertence a `delivery`.
- O router ja exige autenticacao para o prefixo `/sponsorship`.

### Parcialmente Implementado

- O contrato ja possui campos de arquivo no modelo, mas o fluxo completo de upload e persistencia desses metadados nao esta fechado nas interfaces publicas atuais.
- O modelo ja possui `validated_by_user_id`, `validated_at`, `rejection_reason` e `internal_notes`, mas o fluxo de validacao/rejeicao/reversao nao esta especializado; hoje a API usa atualizacao generica de ocorrencia.
- A semantica de atraso como derivado esta alinhada ao documento, mas nao ha calculo ou exposicao dedicada desse estado.
- O tipo de responsabilidade existe tanto na contrapartida quanto na ocorrencia, mas a regra de cardinalidade "1 responsavel" versus "2 ou mais" nao esta automaticamente aplicada no backend.
- O rascunho de extracao por IA ja existe no banco, mas a jornada ponta a ponta de extracao, revisao e aprovacao ainda nao esta exposta via API publica.

### Ainda Nao Implementado

- Nao ha enforcement completo de que `rejection_reason` seja obrigatorio quando a ocorrencia ficar `rejected`.
- Nao ha enforcement completo de que o `member_id` usado em `occurrence_responsible` pertence ao mesmo grupo do contrato da ocorrencia.
- Nao ha enforcement completo de que ocorrencias `individual` tenham exatamente 1 responsavel e ocorrencias `collective` tenham 2 ou mais.
- Nao ha regra explicita no codigo para representar o patrocinador fixo Banco do Brasil como restricao documentada de dominio; hoje isso existe apenas como contexto de negocio.
- Nao ha tratamento dedicado no codigo para tornar obrigatoria a preservacao do historico operacional no momento de substituicao de contrato; o campo existe, mas a politica de transicao ainda depende de uso correto da aplicacao.

## Matriz Curta de Rastreabilidade do Intake

| Decisao de negocio capturada no intake | Secao desta spec |
| --- | --- |
| O modulo existe para verificar a entrega das contrapartidas do patrocinio | Contexto e Objetivo do Modulo |
| Precisa existir entidade contrato | Regras de Negocio Canonicas / Contratos |
| Contrato possui clausulas | Regras de Negocio Canonicas / Clausulas |
| Contrapartida deve se relacionar a clausula do contrato | Regras de Negocio Canonicas / Contrapartidas |
| Contrato pode estar ligado a pessoa ou grupo | Glossario Canonico / Grupo de Patrocinio; Modelo de Dados Canonico |
| Grupo pode conter pessoas e instituicoes | Regras de Negocio Canonicas / Pessoas, Instituicoes e Redes Sociais |
| Pessoas podem ser atleta, medico, fisioterapeuta, fotografo ou outros membros | Glossario Canonico / Pessoa |
| Obrigacao e do patrocinado entregar | Regras de Negocio Canonicas / Contrapartidas |
| Mesmo contrato pode incluir atleta, instituicoes e outras pessoas | Regras de Negocio Canonicas / Pessoas, Instituicoes e Redes Sociais |
| Numeracao de clausula nao tem padrao fixo | Regras de Negocio Canonicas / Clausulas |
| Tipo de contrapartida e arbitrario e manual | Regras de Negocio Canonicas / Contrapartidas |
| Patrocinio pode englobar atleta unico ou squad | Glossario Canonico / Grupo de Patrocinio |
| Prazo e por contrapartida | Regras de Negocio Canonicas / Contrapartidas |
| Observacoes sao sobre a entrega | Regras de Negocio Canonicas / Entregas |
| Contrato precisa de vigencia, data de inicio e numero | Regras de Negocio Canonicas / Contratos |
| Redes sociais devem ser flexiveis por pessoa e instituicao | Regras de Negocio Canonicas / Pessoas, Instituicoes e Redes Sociais |
| Patrocinador e fixo: Banco do Brasil | Regras de Negocio Canonicas / Patrocinador Fixo |
| Responsavel precisa ser especifico e membro do grupo | Regras de Negocio Canonicas / Contrapartidas; Regras de Integridade Canonicas |
| Contrapartida e obrigacao; entrega e devolutiva | Glossario Canonico / Contrapartida; Glossario Canonico / Entrega |
| Uma entrega pode ter multiplas comprovacoes | Regras de Negocio Canonicas / Evidencias |
| Status operacionais foram aprovados | Regras de Negocio Canonicas / Status Operacionais |
| Nao guardar valor financeiro do contrato neste modulo | Regras de Negocio Canonicas / Contratos |
| Contrato precisa de upload ou link do original | Regras de Negocio Canonicas / Contratos |
| Clausulas devem ser extraidas para o banco | Regras de Negocio Canonicas / Clausulas |
| So clausulas obrigacionais devem ser extraidas | Regras de Negocio Canonicas / Clausulas; Extracao por IA |
| PDF completo deve permanecer referenciado em storage | Regras de Negocio Canonicas / Contratos; Extracao por IA |
| Extracao por IA deve passar por revisao humana | Regras de Negocio Canonicas / Extracao por IA |
| Contrapartida pode ser recorrente | Regras de Negocio Canonicas / Recorrencia |
| Contrapartida aponta para uma unica clausula | Regras de Negocio Canonicas / Contrapartidas |
| Novo contrato substitui o anterior com `replaced_by_contract_id` | Regras de Negocio Canonicas / Contratos |
| Historico operacional nao deve ser apagado | Regras de Negocio Canonicas / Contratos; Regras de Integridade Canonicas |
| Qualquer usuario pode validar, rejeitar e reverter | Regras de Negocio Canonicas / Validacao, Rejeicao e Reversao |
| Rejeicao exige motivo | Regras de Negocio Canonicas / Validacao, Rejeicao e Reversao; Regras de Integridade Canonicas |
| A responsabilidade pode ser individual ou coletiva | Regras de Negocio Canonicas / Responsabilidade Individual e Coletiva |
| Responsabilidade coletiva exige corresponsaveis | Regras de Negocio Canonicas / Responsabilidade Individual e Coletiva |
| Deve existir ocorrencia entre contrapartida e entrega | Glossario Canonico / Ocorrencia da Contrapartida; Regras de Negocio Canonicas / Ocorrencias |
| Tipos de evidencia definidos como link, file, text, social_post, image, other | Regras de Negocio Canonicas / Evidencias |
| `atrasada` deve ser derivado e nao necessariamente persistido | Regras de Negocio Canonicas / Status Operacionais |
| Recorrencia e parametrizada por periodo base | Regras de Negocio Canonicas / Recorrencia |
