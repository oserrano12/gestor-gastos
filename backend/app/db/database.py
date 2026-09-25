from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está configurada en el archivo .env")

# Crear el motor de base de datos
engine = create_engine(DATABASE_URL)

# Crear la fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para que hereden los modelos
Base = declarative_base()

# Dependencia para obtener la sesión de la base de datos en FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
