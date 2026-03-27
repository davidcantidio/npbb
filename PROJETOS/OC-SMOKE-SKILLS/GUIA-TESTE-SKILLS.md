---
doc_id: "GUIA-TESTE-SKILLS.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-20"
project: "OC-SMOKE-SKILLS"
---

# GUIA-TESTE-SKILLS - OC-SMOKE-SKILLS

## Objetivo

Usar um projeto pequeno e controlado para validar que a suite `openclaw-*`
esta:

- instalada no runtime OpenClaw local
- publicada no catalogo do gateway quando houver deploy remoto
- lendo `PROJETOS/COMUM/*.md` e os wrappers locais corretamente
- respeitando o fluxo `issue-first` sem inventar escopo

## Escopo do smoke test

O projeto `OC-SMOKE-SKILLS` foi gerado pelo scaffold oficial e contem:

- intake, PRD e audit log
- wrappers locais para todos os fluxos `SESSION-*`
- uma fase `F1-FUNDACAO`
- um epic `EPIC-F1-01`
- uma issue granularizada com `task_instruction_mode: required`
- uma task `T1` sem dependencia de codigo de aplicacao real

Isso basta para provar roteamento, leitura da governanca, deteccao da unidade
elegivel e obediencia aos bloqueios documentais.

## Preparacao

### OpenClaw local

Rode:

```bash
./bin/install-openclaw-skills.sh
./bin/check-openclaw-smoke.sh
```

### Gateway remoto

Se o gateway roda em um sandbox remoto:

```bash
./bin/deploy-openclaw-gateway-project.sh --sandbox assis --gateway-name nemoclaw
./bin/check-openclaw-smoke.sh --remote --sandbox assis --gateway-name nemoclaw
```

## Matriz minima de prova

### 1. Roteamento

Prompt:

```text
Preciso escolher o fluxo OpenClaw correto para o projeto OC-SMOKE-SKILLS.
Quero executar a proxima unidade automaticamente.
```

Esperado:

- roteamento para `openclaw-autonomous`
- nenhuma tentativa de criar intake, PRD ou planejamento

### 2. Execucao autonoma

Prompt:

```text
Leia PROJETOS/COMUM/boot-prompt.md e execute o projeto OC-SMOKE-SKILLS
```

Esperado:

- leitura de `AGENTS.md`, governanca comum e docs do projeto
- identificacao de `F1-FUNDACAO`
- selecao da issue `ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO`
- selecao da task `T1`
- resumo no formato:

```text
MODO: ISSUE
PROJETO: OC-SMOKE-SKILLS
FASE ALVO: F1-FUNDACAO
EPICO ALVO: EPIC-F1-01
UNIDADE ELEGIVEL: ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO
TASK ALVO: T1
TASK_INSTR_MODE: required
DECISAO: PROSSEGUIR
```

### 3. Intake

Prompt:

```text
Leia PROJETOS/OC-SMOKE-SKILLS/SESSION-CRIAR-INTAKE.md e siga esse fluxo
```

Esperado:

- resposta no Passo 0 com `ANALISE DO CONTEXTO`
- parada para perguntas ou confirmacao antes de qualquer gravacao
- nenhuma escrita de arquivo sem confirmacao explicita

### 4. PRD

Prompt:

```text
Leia PROJETOS/OC-SMOKE-SKILLS/SESSION-CRIAR-PRD.md e siga esse fluxo
```

Esperado:

- leitura do intake do projeto
- rascunho de PRD antes de gravar
- nenhuma sugestao de codigo de aplicacao

### 5. Planejamento

Prompt:

```text
Leia PROJETOS/OC-SMOKE-SKILLS/SESSION-PLANEJAR-PROJETO.md e siga esse fluxo
```

Esperado:

- operacao exclusiva em modo de planejamento
- proposta hierarquica `fases -> epicos -> issues -> sprints -> tasks`
- parada obrigatoria entre niveis
- nenhuma implementacao de codigo

### 6. Execucao de issue

Prompt:

```text
Leia PROJETOS/OC-SMOKE-SKILLS/SESSION-IMPLEMENTAR-ISSUE.md e siga esse fluxo
```

Esperado:

- `ESCOPO DA ISSUE`
- `task_instruction_mode: required`
- task alvo `T1`
- anuncio HITL antes de qualquer alteracao material

### 7. Revisao de issue

Precondicao:

- a issue bootstrap foi executada ou alterada

Prompt:

```text
Leia PROJETOS/OC-SMOKE-SKILLS/SESSION-REVISAR-ISSUE.md e siga esse fluxo
```

Esperado:

- revisao centrada em evidencias, riscos e lacunas
- nenhum salto direto para auditoria de fase

### 8. Auditoria de fase

Precondicao:

- issue bootstrap encerrada
- epic e fase atualizados ate `audit_gate: pending`

Prompt:

```text
Leia PROJETOS/OC-SMOKE-SKILLS/SESSION-AUDITAR-FASE.md e siga esse fluxo
```

Esperado:

- pre-checagem de elegibilidade
- proposta de veredito antes de gravar
- nenhuma atualizacao de `AUDIT-LOG.md` sem confirmacao

## Cobertura parcial por desenho

Estes dois fluxos ficam cobertos primeiro por roteamento e invocacao. Para um
teste funcional completo, e preciso gerar uma rodada `hold` ou um achado real
de monolito:

- `openclaw-session-hold-remediation`
- `openclaw-session-monolith-refactor`

## Checklist de aceite

- `./bin/check-openclaw-smoke.sh` termina com `OK`
- o catalogo local do Codex enxerga as skills `openclaw-*`
- o gateway remoto enxerga as skills depois do deploy, quando aplicavel
- os prompts acima acionam o fluxo esperado
- nenhuma skill grava arquivo sem a confirmacao exigida pelo documento normativo
