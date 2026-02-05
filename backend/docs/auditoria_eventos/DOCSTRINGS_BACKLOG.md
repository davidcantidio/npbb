# Docstrings Backlog (Eventos)

Prioridade: services/utils e helpers de regra de negocio ligados a eventos.

1) `app/routers/eventos.py::_apply_visibility`
- Por que: regra de acesso e central para o dominio (quem ve quais eventos).
- Docstring deve descrever: tipos de usuario considerados, criterio de filtro, comportamento de erro quando agencia_id falta.

2) `app/routers/eventos.py::_find_evento_match`
- Por que: define dedupe/upsert no import CSV (sobreposicao de periodo).
- Docstring deve descrever: criterios de match (nome/cidade/estado + overlap), como escolhe melhor candidato.

3) `app/routers/eventos.py::_build_evento_payload_from_row`
- Por que: mapeamento CSV -> payload do evento e fonte de validacoes.
- Docstring deve descrever: colunas obrigatorias, normalizacoes, tipos esperados, erros possiveis.

4) `app/routers/eventos.py::importar_eventos_csv`
- Por que: fluxo de importacao e log/telemetria do modulo.
- Docstring deve descrever: formato CSV, estrategia de upsert, estrutura de resposta e limites esperados.

5) `app/services/data_health.py::compute_event_data_health`
- Por que: gera indicador de saude do evento e e usado no list.
- Docstring deve descrever: campos avaliados, peso, excecoes por status, fallback de config.

6) `app/services/data_health.py::compute_event_missing_fields_details`
- Por que: fornece lista de pendencias usada no endpoint missing-fields.
- Docstring deve descrever: criterios de prioridade e formato de retorno.

7) `app/services/questionario.py::replace_questionario_estrutura`
- Por que: replace-all do questionario (apaga tudo e reescreve) e sensivel a dados.
- Docstring deve descrever: estrategia de delete/insert, atomicidade, riscos e validacoes.

8) `app/routers/ativacao.py::_check_visibility_or_404`
- Por que: regra de visibilidade duplicada; precisa ficar documentada para evitar divergencias.
- Docstring deve descrever: quem pode acessar e quando retorna 404 vs 403.

9) `app/routers/gamificacao.py::_check_visibility_or_404`
- Por que: mesma regra da ativacao, mas aplicada a gamificacao.
- Docstring deve descrever: criterio de acesso e mensagens de erro.

10) `app/routers/ingressos.py::listar_ativos_para_ingressos`
- Por que: depende de diretoria do usuario e regras de email BB.
- Docstring deve descrever: criterios de elegibilidade, filtros por diretoria e ordenacao.
