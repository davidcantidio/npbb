# Auditoria de Cobertura (Shows por Dia)

Objetivo: responder ao feedback de omissao de shows por dia e registrar, de forma auditavel, o que existe na pasta de trabalho para cada dia do evento no recorte de shows (noturno).

Definicoes operacionais usadas nesta auditoria:

- "Dado de show (controle de acesso)": existe fonte de controle de acesso claramente associada a sessao noturna (show), permitindo medir "entradas validadas" por sessao.
- "Dado de show (opt-in)": existe extracao Eventim de "opt-in aceitos" para a sessao de show, permitindo analise de pre-venda e proxy de relacionamento.
- "Ingressos vendidos (total)": existe fonte com total de ingressos vendidos/emitidos por sessao (nao apenas recorte de opt-in).
- "Publico unico": existe chave/estrategia para deduplicar pessoas entre sessoes/dias.

## Resultado por dia (status)

| Dia (show noturno) | Controle de acesso (entradas validadas) | Opt-in aceitos (Eventim) | Ingressos vendidos (total) | Publico unico (dedupe) | Conclusao |
|---|---|---|---|---|---|
| Dia doze de dezembro | GAP | OK | GAP | GAP | Ha dados de opt-in para show, mas nao ha controle de acesso de show nesta pasta |
| Dia treze de dezembro | OK | OK | GAP | GAP | Ha controle de acesso e opt-in para show; ainda falta "ingressos vendidos total" e publico unico |
| Dia quatorze de dezembro | GAP | GAP | GAP | GAP | Nao ha dados de show na pasta (apenas controle de acesso diurno gratuito) |

## Evidencia objetiva (fontes encontradas por dia)

### Dia doze de dezembro

- Controle de acesso (diurno, gratuito): `SRC_PDF_ACESSO_DIURNO_GRATUITO_DOZE`
- Opt-in aceitos (show): `SRC_XLSX_OPTIN_ACEITOS_DOZE`
- Ausencia na pasta: nao foi encontrado PDF de controle de acesso noturno (show) para este dia.

### Dia treze de dezembro

- Controle de acesso (diurno, gratuito): `SRC_PDF_ACESSO_DIURNO_GRATUITO_TREZE`
- Controle de acesso (noturno, show): `SRC_PDF_ACESSO_NOTURNO_TREZE`
- Opt-in aceitos (show): `SRC_XLSX_OPTIN_ACEITOS_TREZE`

### Dia quatorze de dezembro

- Controle de acesso (diurno, gratuito): `SRC_PDF_ACESSO_DIURNO_GRATUITO_QUATORZE`
- Ausencia na pasta: nao foi encontrado PDF de controle de acesso noturno (show) para este dia.
- Ausencia na pasta: nao foi encontrado XLSX de opt-in aceitos (Eventim) para show neste dia.

## O que falta pedir para fechar as lacunas

- Para controle de acesso de show:
  - Relatorio/PDF (ou extrato tabular) do controle de acesso das sessoes noturnas (show) do dia doze e do dia quatorze.
  - Ideal: mesma estrutura de colunas do resumo por sessao (validos/invalidos/bloqueados/presentes/ausentes/comparecimento).
- Para "ingressos vendidos (total)":
  - Extracao Eventim (ou bilheteria) com total de ingressos vendidos/emitidos por sessao, incluindo cancelamentos/estornos quando aplicavel.
- Para "publico unico":
  - Identificador deduplicavel (CPF, documento, ou ID transacao) ou uma regra formal de dedupe com chaves disponiveis; sem isso, reportar explicitamente apenas "entradas validadas" por sessao.
- Para confirmacao de calendario:
  - Agenda oficial do evento com lista de sessoes (diurno gratuito vs noturno show) por dia, para evitar interpretar ausencia de arquivo como ausencia de show.

