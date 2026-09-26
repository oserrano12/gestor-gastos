from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router

app = FastAPI(title="Gestor de Gastos Avanzado", version="1.0.0")

# Configuración de CORS para permitir peticiones desde el Frontend (PWA)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción se debe cambiar al dominio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API del Gestor de Gastos Avanzado"}
