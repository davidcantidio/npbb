---
doc_id: "TASK-1.md"
user_story_id: "US-5-03-CONTRATO-MINIMO-PAYLOAD-QR"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on: []
parallel_safe: false
write_scope:
  - "PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-5-EMISSAO-INTERNA-QR-UNITARIO/CONTRATO-PAYLOAD-QR.md"
tdd_aplicavel: false
---

# TASK-1 - Publicar documento de contrato minimo do payload QR

## objetivo

Publicar um documento versionado sob a feature que fixe o contrato minimo do payload associado ao QR de emissao interna unitaria, alinhado ao PRD sec. 3 (hipoteses sobre identidade para validador futuro), ao intake (incluindo rastreio da pergunta na sec. 15) e ao manifesto da FEATURE-5, sem acrescentar semantica fora do escopo acordado.

## precondicoes

- Leitura do [README da US](./README.md), do [FEATURE-5.md](../../FEATURE-5.md), de trechos relevantes do [PRD](../../../../PRD-ATIVOS-INGRESSOS.md) sec. 3 e do [INTAKE](../../../../INTAKE-ATIVOS-INGRESSOS.md) sec. 15.
- Nenhuma dependencia de US predecessoras para **redigir** o documento; o texto deve permanecer alinhado ao que o PRD e o intake ja definem (identidade persistida suficiente; validador completo fora do corte).

## orquestracao

- `depends_on`: nenhuma task anterior na mesma US.
- `parallel_safe`: `false` — precede implementacao e testes automatizados.
- `write_scope`: apenas o ficheiro de contrato listado no frontmatter; nao alterar codigo de aplicacao nesta task.

## arquivos_a_ler_ou_tocar

- [README.md](./README.md)
- [FEATURE-5.md](../../FEATURE-5.md)
- [PRD-ATIVOS-INGRESSOS.md](../../../../PRD-ATIVOS-INGRESSOS.md)
- [INTAKE-ATIVOS-INGRESSOS.md](../../../../INTAKE-ATIVOS-INGRESSOS.md)
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-5-EMISSAO-INTERNA-QR-UNITARIO/CONTRATO-PAYLOAD-QR.md` *(criar)*

## passos_atomicos

1. Criar `CONTRATO-PAYLOAD-QR.md` na pasta da feature com identificador de versao do contrato (ex.: `contrato_versao: 1`) e data.
2. Listar campos obrigatorios do payload **ou** referencia inequivoca ao identificador persistido pela emissao unitaria, como exige o primeiro criterio Given/When/Then da US.
3. Documentar explicitamente o que permanece **fora** do escopo do validador neste corte (scanner, uso unico no portao, estado `qr_validado`, PRD 2.4 fora / sec. 6).
4. Definir regras de compatibilidade e o que constitui mudanca de **major** versus evolucao compativel, para que um leitor usando apenas esta US e o doc consiga decidir (terceiro criterio Given/When/Then).
5. Incluir um exemplo de payload **nao sensivel** (IDs ficticios, sem dados pessoais reais).
6. Referenciar cruzadamente o [INTAKE](../../../../INTAKE-ATIVOS-INGRESSOS.md) sec. 15 no corpo do documento.

## comandos_permitidos

- Ferramentas de edicao de Markdown no repositorio (IDE, `git diff`).

## resultado_esperado

- Ficheiro `CONTRATO-PAYLOAD-QR.md` existente, revisavel em Git, cobrindo campos ou referencia ao ID persistido, exclusoes de escopo do validador e politica de versao/compatibilidade.

## testes_ou_validacoes_obrigatorias

- Revisao humana: um segundo leitor confirma que o doc nao inventa requisitos ausentes do PRD/intake e que os tres criterios documentais da US sao atendidos pelo texto.

## stop_conditions

- Parar e reportar `BLOQUEADO` se houver conflito entre PRD, intake e FEATURE-5 que exija decisao de produto antes de fixar campos ou versao.
