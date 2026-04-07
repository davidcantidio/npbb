# Alinhar `framework_*` do `npbb` ao padrão canônico da Fabrica (`is_current` nos filhos)

## Resumo
Migrar o backend `framework_*` do `npbb` para o mesmo modelo limpo já adotado na Fabrica: a noção de “corrente” fica somente nas tabelas filhas `framework_intake` e `framework_prd` via `is_current`; `framework_project` deixa de persistir `current_intake_id` e `current_prd_id`.

A mudança é **quebra limpa de contrato**: remover `current_*_id` do modelo/API e parar de usá-los em serviço, schema e migração. O estado corrente passa a ser sempre derivado por consulta às filhas.

## Mudanças de implementação
- Modelo relacional:
  - Remover `current_intake_id` e `current_prd_id` de `FrameworkProject`.
  - Adicionar `is_current: bool` em `FrameworkIntake` e `FrameworkPRD`.
  - Criar índices parciais únicos por projeto:
    - `framework_intake(project_id) WHERE is_current`
    - `framework_prd(project_id) WHERE is_current`
- Migração Alembic:
  - Adicionar `is_current` nas duas tabelas filhas com default temporário `false`.
  - Backfill:
    - marcar `is_current = true` no intake/prd cujo `id` coincide com `framework_project.current_*_id`;
    - se o ponteiro do projeto estiver nulo ou órfão, deixar todas as linhas desse tipo como `false`.
  - Criar os índices parciais únicos após o backfill.
  - Remover `current_intake_id` e `current_prd_id` de `framework_project`.
- Serviços e regras de escrita:
  - `process_intake` deve, na mesma transação lógica, desmarcar os demais intakes do projeto e marcar o intake persistido como `is_current=true`.
  - `generate_prd` deve usar o intake corrente do projeto, criar o novo PRD como corrente e desmarcar os PRDs anteriores do mesmo projeto.
  - Extrair helpers internos para resolver `current_intake` e `current_prd` por query, para evitar repetir a regra.
- Leitura e API:
  - Remover `current_intake_id` e `current_prd_id` de `FrameworkProjectRead`.
  - Adicionar `is_current` em `FrameworkIntakeRead` e `FrameworkPRDRead`.
  - Manter `FrameworkProjectSnapshot.current_intake` e `current_prd` como campos **derivados**, não persistidos.
  - `GET /framework/projects/{id}/status` deve calcular `has_intake` e `has_prd` consultando as filhas correntes.
  - `POST /framework/projects/{id}/prd/generate` deve parar de usar “mais recente por `created_at`” e passar a exigir/resolver o intake marcado como corrente.
- Contrato e testes:
  - Atualizar os testes de contrato para afirmar:
    - ausência de `current_*_id` em `framework_project`;
    - presença de `is_current` em `framework_intake` e `framework_prd`;
    - migração inicial/seguinte compatível com o novo contrato.
  - Atualizar testes de fluxo para validar troca de corrente ao criar novo intake/PRD.

## APIs/interfaces públicas
- Remover de `FrameworkProjectRead`:
  - `current_intake_id`
  - `current_prd_id`
- Adicionar em `FrameworkIntakeRead`:
  - `is_current: bool`
- Adicionar em `FrameworkPRDRead`:
  - `is_current: bool`
- Semântica nova:
  - “corrente” é sempre a linha filha com `is_current=true`;
  - `FrameworkProject` não carrega mais ponteiros persistidos para artefatos correntes.

## Testes e cenários
- Migração:
  - projeto com `current_*_id` válido vira exatamente uma linha filha `is_current=true`.
  - projeto com ponteiro nulo mantém zero linhas correntes.
  - projeto com ponteiro órfão não quebra a migração.
- Intake:
  - primeiro intake do projeto vira corrente.
  - segundo intake do mesmo projeto desmarca o anterior e vira o único corrente.
- PRD:
  - geração usa o intake corrente.
  - segundo PRD do mesmo projeto desmarca o anterior e vira o único corrente.
- API:
  - listagem/leitura de projetos não expõe mais `current_*_id`.
  - respostas de intake/PRD incluem `is_current`.
  - endpoint de status continua reportando `has_intake/has_prd` corretamente.
- Contrato:
  - testes de schema/model/migration cobrem ausência dos ponteiros no projeto e presença das flags nas filhas.

## Assunções
- A referência canônica a seguir é a da Fabrica observada no clone `C:\Users\NPBB\fabrica`: `is_current` nos filhos, sem `projects.current_*_id`.
- O escopo é o backend `framework_*` do `npbb`; não inclui alterar o schema/read model principal da Fabrica, que já segue esse padrão.
- `FrameworkProjectSnapshot.current_intake/current_prd` permanecem válidos porque são projeções derivadas, não uma segunda fonte de verdade.
- Em caso de projeto sem linha corrente após backfill, o sistema tolera ausência de corrente em vez de inventar “latest” como fallback.
