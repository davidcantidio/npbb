---
doc_id: "GOV-BRANCH-STRATEGY.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-18"
---

# GOV-BRANCH-STRATEGY

## Objetivo

Definir a estratégia de branches para projetos ativos, garantindo que o desenvolvimento siga o principio **delivery-first**, materializado como planejamento **feature-first**, e nao seja orientado por **camadas tecnicas** (banco/backend/frontend).

## Regra Principal

> **Branch por feature, não por camada**

O desenvolvimento de uma feature deve acontecer em uma única branch que contenha todas as camadas necessárias (banco, backend, frontend, testes) para que a feature seja **completa e demonstrável**.

## Formato Canonico de Branch

Use o identificador da feature definido no PRD, normalizado para branch:

```
feature/<id-feature-normalizado>-<slug>
```

Exemplos:

- ✅ `feature/feature-1-cadastro-usuario`
- ✅ `feature/feature-2-login`
- ✅ `feature/feature-3-exportar-relatorio`

### Formatos Inválidos (Anti-patterns)

- ❌ `feature/backend-cadastro`
- ❌ `feature/frontend-cadastro`
- ❌ `feature/database-migration`
- ❌ `feature/api-login`

## Estrutura de Branch

### Branch Principal de Feature

Uma branch de feature deve conter:

1. **Banco/Migrações**: tabelas, colunas, constraints
2. **Backend**: endpoints, modelos, regras de negócio
3. **Frontend**: telas, componentes, estados
4. **Testes**: unitários, integração, E2E

### Por Que Esta Estrutura Funciona

- **Entrega valor completo**: a branch pode ser mergeada e demonstrada
- **Facilita review**: código relacionado está junto
- **Reduz branch gigante parada**: escopo menor e integrável
- **Evita integração tardia**: feature completa desde o início
- **Permite rollback claro**: reversão de feature inteira

## Branches Técnicas Separadas (Exceção)

Apenas para fundações compartilhadas genuinamente transversais, onde o trabalho é puramente de infraestrutura e não entrega valor diretamente:

```
infra/<slug>
```

Exemplos válidos:

- `infra/schema-base`
- `infra/auth-core`
- `infra/database-migrations`

### Critérios para Branch Infra

Uma branch técnica separada faz sentido **apenas** quando:

- É trabalho de fundação que não entrega comportamento por si só
- Será consumida por múltiplas features
- Não tem dependência de outras branches técnicas
- Contrato bem definido entre as partes

### Quando NÃO Usar Branch Infra

- ❌ Para "fazer o banco" enquanto frontend espera
- ❌ Para "fazer a API" enquanto UI não tem o que consumir
- ❌ Para separar trabalho que poderia estar junto na feature

## Branches de Suporte

### Bugfix

```
bugfix/<ID-ISSUE>-<slug>
```

Exemplo: `bugfix/ISSUE-F1-01-003-corrigir-validacao-email`

### Hotfix (Produção)

```
hotfix/<slug>
```

### Refatoração

```
refactor/<slug>
```

Exemplo: `refactor/limpar-modelos-usuario`

## Branches de Auditoria

```
audit/<FASE>-R<NN>
```

Exemplo: `audit/F1-R01`

## Merge e Integração

### Merge Strategy

1. **Feature completa**: quando todos os testes passam e a feature é demonstrável
2. **Rebase vs Merge**: preferencialmente rebase para manter histórico linear
3. **Code Review**: obrigatório antes de merge

### Critério de Merge

Uma branch de feature está pronta para merge quando:

- [ ] Todos os critérios de aceite da feature foram atendidos
- [ ] Testes passam (unitários, integração)
- [ ] Code review aprovado
- [ ] Branch não tem conflitos com main/develop
- [ ] Feature e demonstravel de forma standalone

## Commits por Task

Conforme `GOV-COMMIT-POR-TASK.md`:

- Cada task concluída deve gerar um commit
- Mensagem deve conter: PROJETO, ISSUE_ID, TASK_ID, descrição breve

Formato:
```
<PROJETO> [<ISSUE_ID>] [<TASK_ID>] <descrição>
```

Exemplo:
```
DASHBOARD-LEADS [ISSUE-F1-01-003] [T1] criar tabela de usuários
```

## Rebase e Atualização

### Antes de Iniciar Nova Task

```bash
git fetch origin
git rebase origin/main
```

### Durante Desenvolvimento

Se main avançou significativamente:

```bash
git fetch origin
git rebase origin/main
```

## Workflow Completo

```
1. Planejar feature no PRD (Features como eixo)
2. Criar branch: feature/<id-feature-normalizado>-<slug>
3. Implementar: banco + backend + frontend + testes
4. Commits por task (conforme GOV-COMMIT-POR-TASK.md)
5. Code review
6. Merge para main/develop
7. Deletar branch
```

## Anti-Patterns Reconhecíveis

| Anti-pattern | Sintoma | Solução |
|--------------|---------|---------|
| Branch por camada | 3 branches avançando separadamente | Unir em uma branch de feature |
| Feature "80% pronta" | Branch parada há dias sem merge | Quebrar em tasks menores |
| Integração no final | Merge conflict massivo | Merge frequente |
| Mocking eterno | Frontend sem API real | Feature completa na branch |

## Referências

- `GOV-SCRUM.md` - Cadeia de trabalho
- `LEGADO/GOV-ISSUE-FIRST.md` - Estrutura historica de issues
- `GOV-COMMIT-POR-TASK.md` - Commits
- `SPEC-TASK-INSTRUCTIONS.md` - Atomicidade

---

> **Frase Guia**: "Branch por feature entrega, branch por camada bloqueia"
