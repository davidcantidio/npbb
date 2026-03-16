---
doc_id: "SESSION-MAPA.md"
version: "2.1"
status: "active"
owner: "PM"
last_updated: "2026-03-10"
---

# SESSION-MAPA

> Mapa de todos os prompts de sessao disponiveis no framework.
> Use este arquivo como ponto de entrada quando operar em chat interativo
> em vez de Cloud Agent autonomo.
> O estado atual do framework possui sete prompts operacionais com
> nomenclatura canonica `SESSION-*.md`; este arquivo e o mapa de entrada
> que inventaria esses prompts sem contar como prompt operacional adicional.

## Quando usar sessao de chat vs agente autonomo

| Situacao | Modo recomendado |
|---|---|
| quer controle passo a passo com confirmacoes | sessao de chat |
| tarefa bem definida, risco baixo, sem surpresas esperadas | `boot-prompt.md` |
| primeira vez executando uma fase ou tipo de tarefa | sessao de chat |
| auditoria com achados potencialmente bloqueantes | sessao de chat |
| refatoracao de monolito | sessao de chat |
| sprint rotineira em projeto maduro | `boot-prompt.md` |

## Mapa de Prompts

```text
PROJETOS/COMUM/
  SESSION-CRIAR-INTAKE.md
  SESSION-CRIAR-PRD.md
  SESSION-PLANEJAR-PROJETO.md
  SESSION-IMPLEMENTAR-ISSUE.md
  SESSION-AUDITAR-FASE.md
  SESSION-REMEDIAR-HOLD.md
  SESSION-REFATORAR-MONOLITO.md
  SESSION-MAPA.md
```

## Prompts Disponiveis

| Prompt | Arquivo | Uso principal | Status |
|---|---|---|---|
| `SESSION-CRIAR-INTAKE` | `PROJETOS/COMUM/SESSION-CRIAR-INTAKE.md` | contexto bruto -> intake aprovado | active |
| `SESSION-CRIAR-PRD` | `PROJETOS/COMUM/SESSION-CRIAR-PRD.md` | intake aprovado -> PRD | active |
| `SESSION-PLANEJAR-PROJETO` | `PROJETOS/COMUM/SESSION-PLANEJAR-PROJETO.md` | PRD -> fases, epicos, issues e sprints | active |
| `SESSION-IMPLEMENTAR-ISSUE` | `PROJETOS/COMUM/SESSION-IMPLEMENTAR-ISSUE.md` | execucao de issue especifica | active |
| `SESSION-AUDITAR-FASE` | `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md` | gate de fase e follow-ups | active |
| `SESSION-REMEDIAR-HOLD` | `PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md` | relatorio hold -> issues locais ou intakes de remediacao | active |
| `SESSION-REFATORAR-MONOLITO` | `PROJETOS/COMUM/SESSION-REFATORAR-MONOLITO.md` | intake de remediacao -> mini-projeto de decomposicao | active |

## Gatilhos Rapidos

| Necessidade | Prompt |
|---|---|
| gerar intake | `SESSION-CRIAR-INTAKE` |
| gerar PRD | `SESSION-CRIAR-PRD` |
| planejar projeto ou fase | `SESSION-PLANEJAR-PROJETO` |
| executar uma issue | `SESSION-IMPLEMENTAR-ISSUE` |
| auditar uma fase | `SESSION-AUDITAR-FASE` |
| rotear follow-ups de auditoria `hold` | `SESSION-REMEDIAR-HOLD` |
| transformar monolito em remediacao estruturada | `SESSION-REFATORAR-MONOLITO` |

## Relacao com o Boot Prompt

| Dimensao | `boot-prompt.md` | `SESSION-*.md` |
|---|---|---|
| entrada | agente autonomo recebe apenas o projeto | PM escolhe o prompt e informa os parametros |
| modo | autonomo | interativo |
| confirmacoes | nenhuma | HITL a cada etapa material |
| descoberta de fase/issue | automatica | nao ha descoberta autonoma; o PM informa escopo e parametros |
| escrita de arquivo | direta | sempre anunciada antes |
| ideal para | execucao madura e repetitiva | planejamento, auditoria e alto risco |
