---
doc_id: "TEMPLATE-IMP-SESSAO.md"
version: "1.2"
status: "active"
owner: "PM"
last_updated: "2026-03-30"
---

# TEMPLATE-IMP-SESSAO — Cabeçalho `imp-N.md` por task

Use na pasta da user story como `imp-1.md`, `imp-2.md`, ... alinhado ao `TASK-N.md`.

Copie o bloco abaixo e preencha antes de invocar `SESSION-IMPLEMENTAR-US.md`.

```text
PROJETO:     <nome do projeto>
FEATURE_ID:  <FEATURE-<N>>
US_ID:       <US-<N>-<NN>>
US_PATH:     <caminho da pasta ou README da US>
TASK_ID:     T<N>
ROUND:       <1 | 2 | ...>
OBJETIVO_EM_UMA_FRASE: <uma linha>
NAO_FAZER:
  - <item 1>
  - <item 2>
COMANDOS_VALIDACAO:
  - <comando copiavel 1>
  - <comando copiavel 2>
COMMIT_BASE_OPCIONAL: <sha ou vazio>
WRITE_SCOPE_EFETIVO: <lista alinhada ao write_scope da task; pode estreitar>
FICHEIROS_PROIBIDOS:
  - <path ou glob 1>
```

**Regras**

- `WRITE_SCOPE_EFETIVO` e `FICHEIROS_PROIBIDOS` nao substituem o `write_scope` da
  task; desvios exigem atualizar a task ou registo de excecao conforme governanca.
- `COMANDOS_VALIDACAO` devem ser os mesmos referidos em `testes_ou_validacoes_obrigatorias`
  quando existirem.
- se o `README.md`, `TASK-N.md` ou manifesto da feature forem longos, use
  `python3 scripts/session_tools/read_file.py` para ler apenas as ancoras
  necessarias; nao despeje o artefato inteiro no contexto do `imp-N.md`.

## Documentos relacionados

| Documento | Relacao |
|-----------|---------|
| `SESSION-IMPLEMENTAR-US.md` | Parametros de entrada e uso do `imp-N.md` |
| `TEMPLATE-TASK.md` | Estrutura canonica da task que o imp espelha |
| `SPEC-TASK-INSTRUCTIONS.md` | Campos obrigatorios, `write_scope`, checklist `done` |
| `GOV-USER-STORY.md` | Gate anti-drift antes de promover task a `done` |
| `SPEC-LEITURA-MINIMA-EVIDENCIA.md` | Leitura por preview/faixa/ancora antes do `imp-N.md` |
| `GOV-FRAMEWORK-MASTER.md` | Secao 3 indexa este template |
