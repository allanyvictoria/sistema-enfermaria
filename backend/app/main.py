import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import router as auth_router

from app.routes import (
    aluno,
    salas,
    professoras,
    profissionais,
    responsaveis,
    tipos_ocorrencia,
    ocorrencias,
    turmas,
    matriculas,
    dashboard,
    relatorios,
    usuarios
)



app = FastAPI(
    title="Sistema de Gestão da Enfermaria Escolar",
    version="1.0.0"
)

load_dotenv()

# Em producao, defina ALLOWED_ORIGINS no .env com a URL do frontend,
# separada por virgula se houver mais de uma. Ex:
# ALLOWED_ORIGINS=https://meusite.netlify.app,https://meusite.com
_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS = (
    ["*"] if _origins_env.strip() == "*"
    else [origem.strip() for origem in _origins_env.split(",") if origem.strip()]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)


app.include_router(aluno.router)
app.include_router(salas.router)
app.include_router(professoras.router)
app.include_router(profissionais.router)
app.include_router(responsaveis.router)
app.include_router(tipos_ocorrencia.router)
app.include_router(ocorrencias.router)
app.include_router(auth_router)
app.include_router(dashboard.router)
app.include_router(relatorios.router)
app.include_router(turmas.router)
app.include_router(matriculas.router)
app.include_router(usuarios.router)

@app.get("/")
def inicio():
    return {
        "mensagem": "Sistema de Gestão da Enfermaria Escolar"
    }