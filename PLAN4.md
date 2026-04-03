# PRD -> Features: contrato JSON e validador determinístico

## Summary
- Introduzir um contrato canônico e estrito para propostas de feature em JSON como artefato legível por máquina mais código Python de validação em `scripts/fabrica_core`, sem integrar provider, sem renderizar markdown final e sem alterar o comportamento atual de `generate_features`.
- Manter o hot path existente intacto; esta iteração adiciona apenas contrato, checagem de elegibilidade do PRD, um validador reproduzível via CLI e testes focados.
- Tratar as versões atuais em worktree de `GOV-PRD.md`, `GOV-FEATURE.md`, `TEMPLATE-FEATURE.md` e `PROMPT-PRD-PARA-FEATURES.md` como baseline normativa; ajustar só o que ainda divergir do contrato obrigatório.

## Key Changes
- Adicionar um artefato canônico do contrato em `scripts/fabrica_core`:
  - chaves raiz estritas: `project`, `prd_path`, `blocked`, `blockers`, `features`
  - chaves estritas por feature: `feature_key`, `feature_slug`, `title`, `prd_evidence`, `business_objective`, `behavior_expected`, `depends_on`, `acceptance_criteria`, `risks`, `layer_impacts`
  - chaves estritas de evidência: `section`, `basis`
  - chaves estritas de camadas: `banco`, `backend`, `frontend`, `testes`, `observabilidade`
  - rejeição de chaves desconhecidas em todos os níveis
- Adicionar modelos tipados e entrypoints estáveis:
  - `validate_feature_proposal_payload(payload, *, repo_root=None, prd_body=None)`
  - `validate_feature_proposal_file(path, *, repo_root=None)`
  - `validate_prd_for_feature_proposal(project, prd_path, *, repo_root)`
  - `FeatureProposalValidationError` com mensagens ordenadas por campo e coleção `errors`
- Separar validação em camadas mecânicas:
  - estrutural: tipos, obrigatoriedade, listas/strings não vazias, regexes e chaves extras
  - regras do contrato: coerência entre `blocked`/`blockers`/`features`, numeração contígua `FEATURE-<N>` a partir de 1, duplicidade, slug válido, `depends_on` apenas para `FEATURE-<N>` existente, mínimo de 2 critérios de aceite, evidência/objetivo/comportamento/riscos/impactos por camada não vazios
  - elegibilidade do PRD: coerência exata entre `project` e `prd_path`, seções canônicas obrigatórias presentes e não vazias, marcadores proibidos de backlog no corpo do PRD
- Manter a checagem de PRD estritamente mecânica:
  - detectar IDs explícitos como `FEATURE-<N>` e `US-...`
  - detectar headings/tabelas/listas explícitas de backlog de features ou user stories
  - exigir seções canônicas não vazias para problema, objetivo, público, jobs, escopo (`Dentro` e `Fora`), métricas, guardrails, dependências, hipóteses, arquitetura, riscos, rollout, revisões/auditorias e não-objetivos
  - sem NLP, inferência, coerção silenciosa ou auto-correção
- Adicionar um wrapper CLI standalone no padrão de `session_logs/validate_trace.py`, por exemplo `scripts/validate_feature_proposal.py`, que:
  - carrega um arquivo JSON de proposta
  - valida payload e PRD referenciado
  - imprime `OK <path>` para proposta válida e desbloqueada
  - imprime `BLOCKED <path>` e os blockers para proposta estruturalmente válida com `blocked=true`
  - sai com erro apenas em falhas reais de contrato/PRD
- Alinhar a documentação ao contrato exato:
  - remover `agent_id` de `PROMPT-PRD-PARA-FEATURES.md`
  - documentar a política estrita de rejeição de chaves extras
  - manter `GOV-PRD.md`, `GOV-FEATURE.md` e `TEMPLATE-FEATURE.md` alinhados aos campos validados
  - explicitar que `business_objective` e `layer_impacts` são campos-fonte do renderer futuro; o renderer segue fora de escopo nesta tarefa
- Não alterar `scripts/fabrica_core/generation.py` nesta iteração, salvo import/helper mínimo se ficar realmente necessário para reaproveitar validação

## Test Plan
- Adicionar uma suíte pytest dedicada em `scripts/fabrica_core/tests/` com helpers que montam em disco um PRD mínimo válido usando os headings canônicos atuais.
- Cobrir no mínimo:
  - JSON válido + PRD válido passa
  - `feature_key` duplicado falha
  - menos de 2 `acceptance_criteria` falha
  - `depends_on` para feature inexistente falha
  - campo obrigatório ausente falha
  - `blocked=true` sem blockers falha
  - `blocked=false` sem features falha
  - PRD inválido por conter backlog de feature/user story falha com mensagem clara
- Adicionar casos extras de rigidez:
  - chave extra na raiz/feature/evidência/layer falha
  - numeração inconsistente (`FEATURE-1`, `FEATURE-3`) falha
  - `feature_slug` vazio ou inválido falha
  - ausência de chave obrigatória em `layer_impacts` falha
  - smoke test do CLI para saídas `OK` e `BLOCKED`
- Executar a nova suíte com o runner padrão do repo no Windows:
  - `scripts\run-pytest.ps1 scripts/fabrica_core/tests/test_feature_proposal_validator.py -q`

## Assumptions
- O shape fornecido por você é o contrato canônico; campos extras como `agent_id` não serão aceitos.
- `project` e `prd_path` são valores canônicos, relativos ao repo e com `/`, sem normalização silenciosa no validador.
- Um payload com `blocked=true` é um resultado contratualmente válido quando estiver estruturalmente correto; o validador o reporta claramente, mas não o trata como erro de schema.
- Renderização markdown e integração com provider continuam fora desta iteração; o trabalho termina em contrato formal, validação de PRD/payload, exposição via CLI e testes.
