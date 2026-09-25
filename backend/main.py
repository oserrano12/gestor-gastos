from fastapi import FastAPI

app = FastAPI(title="Gestor de Gastos Avanzado", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API del Gestor de Gastos Avanzado"}
