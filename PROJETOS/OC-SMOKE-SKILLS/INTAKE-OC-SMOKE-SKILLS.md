---
doc_id: "INTAKE-OC-SMOKE-SKILLS.md"
version: "1.1"
status: "draft"
owner: "PM"
last_updated: "2026-03-23"
project: "OC-SMOKE-SKILLS"
intake_kind: "new-capability"
source_mode: "original"
origin_project: "nao_aplicavel"
origin_phase: "nao_aplicavel"
origin_audit_id: "nao_aplicavel"
origin_report_path: "PROJETOS/OC-SMOKE-SKILLS/GUIA-TESTE-SKILLS.md"
product_type: "platform-capability"
delivery_surface: "docs-governance"
business_domain: "governanca"
criticality: "media"
data_sensitivity: "interna"
integrations:
  - "PROJETOS/COMUM"
  - "openclaw-* skills"
  - "bin/check-openclaw-smoke.sh"
change_type: "nova-capacidade"
audit_rigor: "standard"
---

# INTAKE - OC-SMOKE-SKILLS

> Intake do projeto-canario usado para validar a suite `openclaw-*` contra o
> framework atual, sem confundir esse projeto com backlog de produto.

## 0. Rastreabilidade de Origem

- projeto de origem: nao_aplicavel
- fase de origem: nao_aplicavel
- auditoria de origem: nao_aplicavel
- relatorio de origem: `PROJETOS/OC-SMOKE-SKILLS/GUIA-TESTE-SKILLS.md`
- motivo da abertura deste intake: manter um canario pequeno e controlado para provar roteamento, execucao, revisao e auditoria das skills `openclaw-*` antes de remodernizar os demais projetos

### Fontes principais

- `PROJETOS/OC-SMOKE-SKILLS/GUIA-TESTE-SKILLS.md`
- `PROJETOS/COMUM/boot-prompt.md`
- `PROJETOS/COMUM/SESSION-MAPA.md`
- `bin/check-openclaw-smoke.sh`

## 1. Resumo Executivo

- nome curto da iniciativa: canario de framework OpenClaw
- tese em 1 frase: usar `OC-SMOKE-SKILLS` como projeto minimo para validar que a suite `openclaw-*` le o framework atual, encontra a unidade certa e respeita os gates documentais
- valor esperado em 3 linhas:
  - detectar drift de wrappers, prompts e governanca antes que ele atinja projetos reais
  - provar o ciclo `roteamento -> execucao -> revisao -> auditoria` em um backlog controlado
  - manter um smoke test reproduzivel via `GUIA-TESTE-SKILLS.md` e `./bin/check-openclaw-smoke.sh`

## 2. Problema ou Oportunidade

- problema atual: depois das mudancas em `PROJETOS/COMUM` e nos wrappers locais, um projeto gerado por scaffold antigo pode continuar roteando para defaults obsoletos e mascarar regressao no framework
- evidencia do problema: o `GUIA-TESTE-SKILLS.md` ja descreve prompts esperados para autonomia, execucao, revisao e auditoria, mas o intake antigo ainda tratava o projeto como scaffold generico
- custo de nao agir: regressao do framework pode aparecer primeiro em projetos reais, sem um ambiente pequeno para isolar o problema
- por que agora: a remodernizacao dos projetos depende de um canario confiavel para provar o gerador corrigido e os fluxos `openclaw-*`

## 3. Publico e Operadores

- usuario principal: PM ou mantenedor do framework OpenClaw
- usuario secundario: quem instala skills locais ou valida o gateway remoto
- operador interno: suite `openclaw-*`, `boot-prompt.md`, wrappers locais e `./bin/check-openclaw-smoke.sh`
- quem aprova ou patrocina: PM

## 4. Jobs to be Done

- job principal: "Quero provar rapidamente se a stack OpenClaw ainda sabe rotear e operar um projeto issue-first minimo sem inventar escopo."
- jobs secundarios:
  - validar se as skills leem `PROJETOS/COMUM/*.md` e os wrappers locais atuais
  - testar o canario antes de remodernizar backlog real
  - capturar regressao documental em um projeto de blast radius baixo
- tarefa atual que sera substituida: descobrir regressao de framework apenas quando um projeto maior quebra

## 5. Fluxo Principal Desejado

1. Instalar ou atualizar as skills `openclaw-*` no runtime OpenClaw local e, quando aplicavel, no gateway remoto.
2. Rodar `./bin/check-openclaw-smoke.sh` para validar a superficie minima do framework.
3. Executar prompts do guia para confirmar roteamento, autonomia, execucao da issue canario, revisao e auditoria.
4. Usar qualquer falha encontrada como evidencia para corrigir `PROJETOS/COMUM`, wrappers locais ou o gerador compartilhado.

## 6. Escopo Inicial

### Dentro

- validacao da suite `openclaw-*` contra este projeto-canario
- wrappers locais alinhados ao framework atual
- backlog minimo da fase F1 usado como prova controlada de execucao, revisao e auditoria
- smoke local e remoto descrito no guia

### Fora

- backlog de produto proprio
- implementacao de feature de negocio fora do proprio framework OpenClaw
- deploy de runtime de produto

## 7. Resultado de Negocio e Metricas

- objetivo principal: detectar drift do framework cedo e com baixo custo
- metricas leading:
  - `./bin/check-openclaw-smoke.sh` termina com `OK`
  - prompts do guia acionam o fluxo correto sem fallback manual
  - wrappers do projeto nao congelam filas antigas
- metricas lagging:
  - menos regressao descoberta tardiamente em projetos reais
  - menor tempo para validar novas mudancas em `PROJETOS/COMUM` ou `scripts/criar_projeto.py`
- criterio minimo para considerar sucesso: o projeto-canario consegue validar o ciclo minimo do framework com evidencias reproduziveis

## 8. Restricoes e Guardrails

- restricoes tecnicas:
  - manter o projeto pequeno, previsivel e 100% documental
  - reaproveitar o guia como contrato de aceite do canario
- restricoes operacionais:
  - nao transformar `OC-SMOKE-SKILLS` em backlog de produto
  - qualquer drift detectado aqui deve virar correcao no framework ou no gerador, nao no canario apenas
- restricoes legais ou compliance: nenhuma alem das politicas normativas do framework
- restricoes de prazo: o canario precisa acompanhar a evolucao do framework no mesmo ciclo de mudanca
- restricoes de design ou marca: nenhuma

## 9. Dependencias e Integracoes

- sistemas internos impactados: `PROJETOS/COMUM`, wrappers locais, `scripts/criar_projeto.py`, `bin/check-openclaw-smoke.sh`
- sistemas externos impactados: gateway remoto quando houver deploy da suite
- dados de entrada necessarios: prompts do guia, artefatos do projeto, install local de skills
- dados de saida esperados: veredito rapido sobre aderencia do framework e evidencias para correcao

## 10. Arquitetura Afetada

- backend: nao_aplicavel
- frontend: nao_aplicavel
- banco/migracoes: nao_aplicavel
- observabilidade: audit log, relatorio base de fase e saida do smoke
- autorizacao/autenticacao: nao_aplicavel
- rollout: local primeiro; remoto opcional para o gateway

## 11. Riscos Relevantes

- risco de produto: baixo, porque o projeto e canario
- risco tecnico: canario envelhecer e voltar a mascarar drift
- risco operacional: tratar o canario como backlog de negocio e perder a funcao de prova controlada
- risco de dados: nenhum
- risco de adocao: ignorar o canario e descobrir regressao apenas nos projetos reais

## 12. Nao-Objetivos

- substituir testes de produto
- carregar escopo funcional fora do framework OpenClaw
- virar o backlog principal da plataforma

## 13. Contexto Especifico para Problema ou Refatoracao

- sintoma observado: wrappers locais e docs do canario ainda refletiam o scaffold generico, nao o `GUIA-TESTE-SKILLS.md`
- impacto operacional: o projeto deixava de ser fonte confiavel para provar o comportamento atual da suite `openclaw-*`
- evidencia tecnica: drift entre guia, wrappers e backlog bootstrap do canario
- componente(s) afetado(s): `PROJETOS/OC-SMOKE-SKILLS/*`, `scripts/criar_projeto.py`, `bin/check-openclaw-smoke.sh`
- riscos de nao agir: regressao do framework passa sem deteccao ou so aparece em backlog real

## 14. Lacunas Conhecidas

- smoke remoto depende de deploy do gateway quando essa trilha for usada
- revisao e auditoria completas do canario continuam dependentes de executar a issue bootstrap ate o handoff
