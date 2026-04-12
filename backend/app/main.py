import os

from fastapi import FastAPI
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse

from app.routers.agencias import router as agencias_router
from app.routers.ativacao import eventos_router as eventos_ativacao_router
from app.routers.ativacao import router as ativacao_router
from app.routers.auth import router as auth_router
from app.routers.ativos import router as ativos_router
from app.routers.dashboard import router as dashboard_router
from app.routers.dashboard_leads import router as dashboard_leads_router
from app.routers.eventos import router as eventos_router
from app.routers.gamificacao import router as gamificacao_router
from app.routers.checkin_sem_qr_public import router as checkin_sem_qr_public_router
from app.routers.landing_public import router as landing_public_router
from app.routers.leads import router as leads_router
from app.routers.publicidade import router as publicidade_router
from app.routers.ingressos import router as ingressos_router
from app.routers.ingressos_v2 import router as ingressos_v2_router
from app.routers.revisao_humana import router as revisao_humana_router
from app.routers.usuarios import router as usuarios_router
from app.routers.ingestion_registry import router as ingestion_registry_router
from app.routers.ingestao_inteligente import router as ingestao_inteligente_router
from app.routers.internal_catalog import router as internal_catalog_router
from app.routers.internal_etl import router as internal_etl_router
from app.routers.internal_health import router as internal_health_router
from app.routers.internal_scraping import router as internal_scraping_router
from app.routers.data_quality import router as data_quality_router
from app.routers.sponsorship import router as sponsorship_router
from app.api.v1.endpoints.framework import router as framework_router


def _normalize_root_path(value: str | None) -> str:
    raw = (value or "").strip()
    if not raw or raw == "/":
        return ""
    return "/" + raw.strip("/")


app = FastAPI(
    title="NPBB API",
    root_path=_normalize_root_path(os.getenv("API_ROOT_PATH")),
)

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
origins = [origin.strip() for origin in frontend_origin.split(",") if origin.strip()]
allow_origin_regex = os.getenv("CORS_ALLOW_ORIGIN_REGEX")
if not allow_origin_regex and any(
    "localhost" in origin or "127.0.0.1" in origin for origin in origins
):
    allow_origin_regex = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "Content-Disposition"],
)


@app.exception_handler(RequestValidationError)
async def questionario_validation_exception_handler(request, exc: RequestValidationError):
    if "/questionario" not in request.url.path:
        return await request_validation_exception_handler(request, exc)

    body_errors = [error for error in exc.errors() if error.get("loc", [None])[0] == "body"]
    if not body_errors:
        return await request_validation_exception_handler(request, exc)

    safe_errors = []
    for error in body_errors:
        ctx = error.get("ctx")
        if isinstance(ctx, dict) and "error" in ctx:
            safe_ctx = dict(ctx)
            if isinstance(safe_ctx.get("error"), Exception):
                safe_ctx["error"] = str(safe_ctx["error"])
            error = {**error, "ctx": safe_ctx}
        safe_errors.append(error)

    return JSONResponse(
        status_code=400,
        content={
            "detail": {
                "code": "QUESTIONARIO_INVALID_STRUCTURE",
                "message": "Estrutura de questionario invalida",
                "extra": {"errors": safe_errors},
            }
        },
    )


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/novo-usuario", response_class=HTMLResponse, include_in_schema=False)
def novo_usuario_page():
    return """
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Novo Usuario</title>
    <style>
      body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; background: #f6f7fb; margin: 0; }
      .wrap { max-width: 560px; margin: 48px auto; background: #fff; padding: 24px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,.12); }
      label { display: block; font-weight: 600; margin-top: 12px; }
      input, select { width: 100%; padding: 10px 12px; margin-top: 6px; border: 1px solid #cbd5e1; border-radius: 10px; }
      .row { display: flex; gap: 12px; }
      .row > * { flex: 1; }
      .hint { color: #64748b; font-size: 14px; margin-top: 8px; }
      button { margin-top: 16px; padding: 10px 14px; border: 0; border-radius: 10px; background: #6750A4; color: #fff; font-weight: 700; cursor: pointer; }
      button[disabled] { opacity: .6; cursor: not-allowed; }
    </style>
  </head>
  <body>
    <div class="wrap">
      <h1 style="margin:0 0 6px 0;">Criar nova conta</h1>
      <div class="hint">Formulario em branco (placeholder). O front-end em React esta em <code>http://localhost:5173/novo-usuario</code>.</div>

      <form>
        <label>Tipo de usuario</label>
        <select>
          <option value="bb">Funcionario BB</option>
          <option value="npbb" selected>Funcionario NPBB</option>
          <option value="agencia">Funcionario Agencia</option>
        </select>

        <label>Email</label>
        <input type="email" placeholder="seu.email@empresa.com.br" />

        <div class="row">
          <div>
            <label>Senha</label>
            <input type="password" placeholder="********" />
          </div>
          <div>
            <label>Confirmar senha</label>
            <input type="password" placeholder="********" />
          </div>
        </div>

        <label>Matricula BB (apenas BB)</label>
        <input placeholder="A123" />

        <label>Agencia (apenas Agencia)</label>
        <select>
          <option value="">Selecione...</option>
          <option>V3A</option>
          <option>Sherpa</option>
          <option>Monumenta</option>
          <option>Terrua</option>
        </select>

        <button type="button" disabled>Criar Conta</button>
      </form>
    </div>
  </body>
</html>
"""


app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(dashboard_leads_router)
app.include_router(usuarios_router)
app.include_router(agencias_router)
app.include_router(eventos_router)
app.include_router(gamificacao_router)
app.include_router(ativacao_router)
app.include_router(eventos_ativacao_router)
app.include_router(ativos_router)
app.include_router(ingressos_router)
app.include_router(ingressos_v2_router)
app.include_router(leads_router)
app.include_router(publicidade_router)
app.include_router(landing_public_router)
app.include_router(checkin_sem_qr_public_router)
app.include_router(revisao_humana_router)
app.include_router(ingestion_registry_router)
app.include_router(ingestao_inteligente_router)
app.include_router(internal_catalog_router)
app.include_router(internal_etl_router)
app.include_router(internal_health_router)
app.include_router(internal_scraping_router)
app.include_router(data_quality_router)
app.include_router(sponsorship_router)
app.include_router(framework_router)
