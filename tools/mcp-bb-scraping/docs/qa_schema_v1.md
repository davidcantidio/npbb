# QA Schema v1

Arquivo: out/qa.json
Versao: qa_schema_v1

Campos:
- timestamp: string ISO-8601 (UTC).
- min_posts: inteiro ou null; minimo de posts configurado.
- posts_total: inteiro ou null; total de posts no recorte.
- volume_status: "ok" | "baixo" | "nao_configurado" | "nao_disponivel".
- volume_warning: string ou null; mensagem de aviso quando volume baixo.
- coverage_status: objeto por metrica.
- linguistic_checklist: objeto com checklist linguistico.

coverage_status.<metrica>:
- coverage_pct: numero (percentual) ou null.
- min_pct: inteiro (percentual minimo).
- status: "ok" | "baixo" | "nao_disponivel".

linguistic_checklist.summary:
- status: "ok" | "warn".
- warnings: inteiro; quantidade de itens em warn.

linguistic_checklist.items[]:
- id: string identificador.
- status: "ok" | "warn" | "na".
- details: string explicativa.

Exemplo:
{
  "timestamp": "2026-01-13T12:00:00+00:00",
  "min_posts": 30,
  "posts_total": 24,
  "volume_status": "baixo",
  "volume_warning": "Base insuficiente: 24 posts (minimo 30).",
  "coverage_status": {
    "likes": { "coverage_pct": 55.0, "min_pct": 60, "status": "baixo" },
    "comments": { "coverage_pct": 80.0, "min_pct": 60, "status": "ok" }
  },
  "linguistic_checklist": {
    "summary": { "status": "warn", "warnings": 2 },
    "items": [
      { "id": "sem_jargao_sem_explicacao", "status": "ok", "details": "Sem jargao detectado." },
      { "id": "percentual_explicado", "status": "warn", "details": "Percentual sem explicacao simples." }
    ]
  }
}
