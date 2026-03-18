# Fluxo Enxuto do Algoritmo

```mermaid
flowchart TD
  classDef ad fill:#163b4d,stroke:#5bc0de,color:#fff;
  classDef orq fill:#3f3a14,stroke:#d4c94f,color:#fff;
  classDef wk fill:#2c274d,stroke:#8c7cf0,color:#fff;
  classDef rv fill:#4a2b16,stroke:#f0a35e,color:#fff;
  classDef human fill:#1f4d2c,stroke:#6fd18a,color:#fff;
  classDef blocked fill:#4d1f1f,stroke:#ff7b7b,color:#fff;

  subgraph P["Planejamento"]
    I1["1 Intake<br/>AD mini"]:::ad
    I2{"2 Gate Intake -> PRD<br/>ORQ + PM"}:::human
    P3["3 PRD<br/>AD mini"]:::ad
    P4{"4 Aprovar PRD<br/>PM"}:::human
    P56["5-6 Fase + Epic<br/>AD mini"]:::ad
    P7["7 Issue<br/>AD mini"]:::ad
    P89["8-9 Task + Sprint<br/>AD mini"]:::ad
  end

  subgraph E["Execucao"]
    E10{"10-13 Preflight<br/>ORQ 5.2"}:::orq
    E11["14-16 Executar task(s)<br/>WK 5.3-codex"]:::wk
    E12["17-20 Fechamento<br/>ORQ 5.2"]:::orq
    B["BLOQUEADO<br/>corrigir artefato / risco / limite"]:::blocked
  end

  subgraph R["Review e Auditoria"]
    R21{"21 Review pos-issue?<br/>RV 5.2"}:::rv
    R22L["22 Correcao local<br/>volta para 7"]:::rv
    R22S["22 Correcao sistemica<br/>volta para 1"]:::rv
    R23{"23 Elegivel para auditoria?<br/>ORQ + RV"}:::rv
    R24{"24 Auditoria de fase<br/>RV 5.2"}:::rv
    R25L["25 Hold local<br/>volta para 7"]:::rv
    R25S["25 Hold sistemico<br/>volta para 1"]:::rv
    R26["26 Go<br/>feito/ + proxima fase"]:::human
  end

  I1 --> I2
  I2 -- lacunas --> I1
  I2 -- pronto --> P3
  P3 --> P4
  P4 -- ajustar --> P3
  P4 -- aprovado --> P56
  P56 --> P7
  P7 --> P89
  P89 --> E10

  E10 -- ok --> E11
  E10 -- bloqueado --> B
  B --> P7

  E11 --> E12
  E12 --> R21

  R21 -- aprovada --> R23
  R21 -- correcao local --> R22L
  R21 -- correcao sistemica --> R22S
  R21 -- cancelled --> R23

  R22L --> P7
  R22S --> I1

  R23 -- nao --> B
  R23 -- sim --> R24

  R24 -- go --> R26
  R24 -- hold local --> R25L
  R24 -- hold sistemico --> R25S
  R24 -- cancelled/provisional --> R23

  R25L --> P7
  R25S --> I1
```

## Legenda de Agentes

- `AD mini`: analista documental com `gpt-5.4-mini`
- `ORQ 5.2`: orquestrador de governanca com `gpt-5.2`
- `WK 5.3-codex`: worker de implementacao com `gpt-5.3-codex`
- `RV 5.2`: reviewer/auditor com `gpt-5.2`
- `PM`: aprovacao humana

## Politica de Modelos

- `gpt-5.4-mini`: intake, PRD, fase, epic, issue, task e sprint. Melhor custo/qualidade para transformacao documental e checagem de aderencia.
- `gpt-5.2`: preflight, risco, gate, work order, review e auditoria padrao. Melhor equilibrio para governanca e decisao.
- `gpt-5.3-codex`: implementacao de codigo como default.
- `gpt-5.4`: usar so por escalada, quando houver `R2/R3`, migration/rollback delicado, refatoracao sistemica, auditoria ambigua ou conflito de evidencias.

## Regra de Escalada

- subir de `mini` para `5.2` quando a tarefa deixar de ser documental e passar a exigir julgamento
- subir de `5.2` para `5.4` quando risco e ambiguidade forem altos
- nao usar modelo caro para tarefa mecanica
- nao usar modelo barato para tarefa que pode errar a governanca ou a arquitetura
