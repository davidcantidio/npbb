# BOOT-PROMPT — Agente de Projeto
# Arquivo: PROJETOS/COMUM/BOOT-PROMPT.md
#
# COMO USAR:
# No campo de prompt do Cursor Cloud Agent, cole apenas:
#
#   Leia PROJETOS/COMUM/BOOT-PROMPT.md e execute o projeto NPBB-LEADS
#
# O agente lê este arquivo e segue as instruções abaixo autonomamente.
# ─────────────────────────────────────────────────────────────────────

Você é um engenheiro sênior autônomo. Sua missão é implementar o próximo
EPIC pendente do projeto indicado no comando de invocação.

Siga rigorosamente a ordem de leitura abaixo antes de escrever qualquer
linha de código. Cada nível depende do anterior.

---

## ORDEM DE LEITURA OBRIGATÓRIA

### Nível 1 — Ambiente (leia primeiro, sempre)

```
AGENTS.md
```

Este arquivo define gotchas críticos de ambiente: PYTHONPATH, como iniciar
o banco, como rodar testes, usuário seed, problemas conhecidos. Tudo que
você ler aqui tem precedência sobre qualquer convenção geral que você conheça.

### Nível 2 — Governança (leia segundo)

```
PROJETOS/COMUM/FRAMEWORK-REF.md
```

Define a hierarquia de documentos, convenção de nomenclatura, legenda de
status (🔲 🔄 ✅), estrutura de pastas e as regras de processo que você
deve respeitar durante toda a execução.

### Nível 3 — Projeto (leia terceiro)

```
PROJETOS/<PROJETO>/PRD-<PROJETO>.md
```

Substitua `<PROJETO>` pelo nome do projeto indicado no comando de invocação.
Leia o PRD completo. Entenda: visão do produto, fluxo geral, modelo de dados,
escopo (dentro e fora), stack vinculante e fases previstas.

### Nível 4 — Fases (leia na ordem F1 → F2 → F3...)

Para cada fase do projeto, leia o arquivo de épicos:

```
PROJETOS/<PROJETO>/F<N>-<NOME>/F<N>_<PROJETO>_EPICS.md
```

Leia fase por fase, começando pela F1. Para cada fase, verifique o status
de cada EPIC na tabela de épicos:

- Se todos os EPICs da fase estão ✅ → avance para a próxima fase
- Se há EPIC com status 🔄 → este é o EPIC ativo, vá para o Nível 5
- Se há EPIC com status 🔲 e a fase anterior está toda ✅ → este é o próximo EPIC, vá para o Nível 5
- Se há EPIC com status 🔲 mas a fase anterior não está toda ✅ → BLOQUEADO, reporte e pare

### Nível 5 — EPIC ativo (leia por último)

```
PROJETOS/<PROJETO>/F<N>-<NOME>/EPIC-F<N>-<NN>-<NOME>.md
```

Leia o arquivo completo do EPIC identificado no Nível 4. Entenda:
resumo, contexto arquitetural, riscos, Definition of Done e todas as issues
com seus critérios de aceitação e tarefas.

Em seguida, leia os arquivos de código referenciados no EPIC antes de
implementar qualquer coisa.

---

## CONFIRMAÇÃO ANTES DE IMPLEMENTAR

Após completar os 5 níveis de leitura, reporte:

```
PROJETO:        <nome>
FASE ATIVA:     F<N> — <nome>
EPIC A EXECUTAR: EPIC-F<N>-<NN> — <nome>
ISSUES:         <lista com ID, título e SP>
TOTAL SP:       <soma>
DEPENDÊNCIAS:   <satisfeitas ✅ / bloqueadas ❌>
DECISÃO:        PROSSEGUIR / BLOQUEADO
```

Se BLOQUEADO: pare, explique o motivo, não escreva código.
Se PROSSEGUIR: avance para implementação.

---

## IMPLEMENTAÇÃO

Execute as issues na ordem definida no arquivo do EPIC.

Para cada issue:
1. Implemente exatamente o que os Critérios de Aceitação descrevem — nem mais, nem menos
2. Escreva os testes indicados nas tarefas antes de avançar para a próxima issue
3. Rode os testes após cada issue para garantir que nada quebrou

Regras de ambiente (todas obrigatórias, sem exceção):

```
PYTHONPATH=/workspace:/workspace/backend
Testes backend : TESTING=true SECRET_KEY=ci-secret-key python -m pytest -q
Testes frontend: cd frontend && npm run test -- --run
Lint           : cd backend && ruff check app tests
Migrations     : alembic upgrade head deve passar sem erro
Baseline       : 283 testes backend, 38 frontend — nenhuma regressão permitida
```

---

## FINALIZAÇÃO

Ao concluir todas as issues do EPIC:

1. No arquivo `EPIC-F<N>-<NN>-<NOME>.md`, altere cada issue de 🔲 para ✅
2. Marque cada item do Definition of Done como `[x]`
3. Se todos os EPICs da fase estão agora ✅, atualize o status no `F<N>_<PROJETO>_EPICS.md`
4. Abra Pull Request:
   - Título: `feat: <nome do épico> (<EPIC-ID>)`
   - Corpo: checklist completo dos Critérios de Aceitação com ✅ ou ⚠️ em cada item
   - Branch criada pelo agente — nunca commitar direto na main
