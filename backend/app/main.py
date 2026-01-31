import os

from fastapi import FastAPI
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse

from app.routers.agencias import router as agencias_router
from app.routers.ativacao import router as ativacao_router
from app.routers.ativos import router as ativos_router
from app.routers.auth import router as auth_router
from app.routers.ingressos import router as ingressos_router
from app.routers.eventos import router as eventos_router
from app.routers.gamificacao import router as gamificacao_router
from app.routers.checkin_sem_qr_public import router as checkin_sem_qr_public_router
from app.routers.landing_public import router as landing_public_router
from app.routers.usuarios import router as usuarios_router

app = FastAPI(title="NPBB API")

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

    return JSONResponse(
        status_code=400,
        content={
            "detail": {
                "code": "QUESTIONARIO_INVALID_STRUCTURE",
                "message": "Estrutura de questionario invalida",
                "extra": {"errors": body_errors},
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
app.include_router(usuarios_router)
app.include_router(agencias_router)
app.include_router(eventos_router)
app.include_router(ativos_router)
app.include_router(ingressos_router)
app.include_router(gamificacao_router)
app.include_router(ativacao_router)
app.include_router(landing_public_router)
app.include_router(checkin_sem_qr_public_router)
