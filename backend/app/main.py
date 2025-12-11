from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.usuarios import router as usuarios_router

app = FastAPI(title="NPBB API")


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(usuarios_router)
