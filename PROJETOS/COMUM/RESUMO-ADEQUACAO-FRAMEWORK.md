# Resumo: Adequação do Framework de Projetos

## Contexto

Este documento resume a análise e recomendações para adequação do framework de projetos existente em `PROJETOS/COMUM`. O framework atual foi analisado e foram identificadas oportunidades de melhoria significativas na organização do planejamento de projetos de software.

---

## Problema Original

O usuário perguntou se fazia sentido quebrar o PRD em 3 partes relativas a camadas de arquitetura (banco de dados, frontend, backend) e desenvolver cada um em uma branch com suas próprias fases.

---

## Análise do Framework Atual

### O que está bom

O framework atual possui pontos fortes importantes:

1. **Padronização existente** - Templates e guias organizados para PRD, fases, arquitetura, organização de projeto
2. **Separação explícita de arquitetura** - Clareza técnica para padrões e evoluções futuras
3. **Pensamento em fases** - Ajuda a evitar começar frontend sem backend
4. **Cascata completa** - Pipeline de intake → PRD → decomposição → tarefas → TDD → execução
5. **Atomicidade real** - Não é "task pequena" genérica, mas sim unidade testável com comportamento verificável
6. **Cascata lógica coerente** - Cada nível deriva do anterior (PRD → tarefa → TDD)

### Pontos de Atenção (Problemas Identificados)

1. **Eixo principal errado** - Organização por "banco / backend / frontend" ao invés de por feature/comportamento
2. **PRD técnico demais** - Quando estruturado por camada, vira modelagem de tabela + endpoint + tela, ao invés de o que o usuário consegue fazer
3. **Risco de "projeto 80% pronto"** - Banco pronto, backend quase, frontend mockado, mas nada utilizável
4. **Fases por camada criam gargalo** - Se tiver fase banco → fase backend → fase frontend, cria fila artificial e bloqueio entre times
5. **Atomicidade orientada a camada** - Tarefa atômica = unidade técnica pequena, ao invés de menor unidade testável de comportamento
6. **Feature no Intake** - Se colocar feature direto no intake, mata a principal função do intake que é explorar o problema sem viés de solução

---

## Solução Recomendada

### Principio Fundamental

> "Se eu pegar qualquer item e perguntar: 'isso entrega algo utilizável?', se a resposta for não → estrutura errada, se for sim → você acertou."

### 1. Trocar o Eixo Principal

**Antes:**
```
Projeto
├── Banco
├── Backend
└── Frontend
```

**Depois:**
```
Projeto
├── Features
│   ├── Criar usuário
│   ├── Login
│   └── Listar pedidos
└── Arquitetura (suporte)
```

### 2. Formalizar a Etapa de Síntese

Nova estrutura do pipeline:

```
INTAKE (problema)
    ↓
SÍNTESE CONCEITUAL (organização)
    ↓
PRD (decisão)
    ↓
FEATURE (comportamento)
    ↓
TAREFA ATÔMICA (ação)
    ↓
TESTE (validação)
```

**O que é a Síntese:**
- Estágio conceitual entre intake e PRD onde você organiza o problema, delimita escopo e identifica blocos de valor
- Aqui nascem as possíveis features (ainda não formais)
- É onde a transição de "problema" para "solução" acontece
- Não precisa virar artefato canônico separado para o framework funcionar

**Por que NÃO colocar feature no Intake:**
- Intake deve conter: problema, contexto, dor, hipótese
- Intake NÃO deve conter: feature definida, endpoint, estrutura técnica
- Se colocar feature no intake, você já decidiu arquitetura prematuramente

### 3. Reinterpretar Tarefa Atômica

**Antes:**
tarefa atômica = unidade técnica pequena (criar tabela, criar endpoint, criar tela)

**Depois:**
tarefa atômica = menor unidade testável de comportamento (usuário consegue se cadastrar com email válido)

### 4. Manter Atomicidade com Cascata Completa

A atomicidade e cascata devem ser preservadas, mas subordinadas a comportamento:

```
Feature: Cadastro de usuário

Cenário:
Usuário consegue se cadastrar com email válido

Tarefas atômicas:
- validar formato de email
- persistir usuário
- retornar erro se duplicado
- exibir mensagem de sucesso

Testes:
- deve aceitar email válido
- deve rejeitar email inválido
- não deve permitir duplicado
```

### 5. Branch Strategy

**Antes (provável):**
```
feature/backend
feature/frontend
feature/database
```

**Depois:**
```
feature/criar-usuario
feature/login
feature/relatorio
```

Dentro de cada branch entram: migration/banco, endpoint/backend, tela/frontend, testes.

Branches técnicas separadas só para fundações compartilhadas (infra/schema-base, infra/auth-core, infra/design-system).

---

## Frase Guia

> **"Intake descobre, PRD decide, Feature organiza, Tarefa executa, Teste valida"**

---

## Regras Práticas

1. **Intake pode conter:** problema, contexto, dor, hipótese
2. **Intake NÃO deve conter:** feature definida, endpoint, estrutura técnica
3. **Feature deve nascer quando:** você consegue descrever comportamento, validar, demonstrar
4. **Se atomicidade não consegue ser demonstrada como comportamento do usuário, está no nível errado**

---

## Estrutura Final Recomendada

```
PROJETOS/
  COMUM/
    TEMPLATE-PRD.md
    GOV-ISSUE-FIRST.md
    GOV-BRANCH-STRATEGY.md

  PROJETO_X/
    INTAKE-PROJETO_X.md
    PRD-PROJETO_X.md
    F1-NOME-DA-FASE/
      F1_PROJETO_X_EPICS.md
      EPIC-F1-01-NOME.md
      issues/
        ISSUE-F1-01-001-NOME/
          README.md
          TASK-1.md
```

---

## Objetivo do PRD a Ser Gerado

Com base nesta análise, deve-se criar um PRD que:

1. **Redefina o eixo principal** do framework de camadas técnicas para features/comportamentos
2. **Formalize a Síntese como etapa conceitual** entre Intake e PRD
3. **Mantenha a atomicidade** mas reoriente-a para comportamento
4. **Ajuste a branch strategy** para feature-first
5. **Atualize templates** para refletir a nova filosofia
6. **Mantenha os pontos fortes** já existentes (cascata, TDD-first, decomposição)

---

## Referências

- Análise baseada na estrutura existente em `PROJETOS/COMUM/`
- Problema original: quebra do PRD por camadas técnicas
- Modelo mental: `delivery-first`, materializado como planejamento `feature-first`
