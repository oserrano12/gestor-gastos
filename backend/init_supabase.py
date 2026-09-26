import os
from sqlalchemy import create_engine
from app.models.models import Base

# Obtenemos la URL directamente para asegurarnos
URL = "postgresql+psycopg://postgres.lftebaaiooibuhnpivzx:eGv2Ex%5EKgkFJ6yMA7UCr@aws-0-us-east-1.pooler.supabase.com:5432/postgres"

engine = create_engine(URL)

print("Conectando a Supabase y creando tablas...")
try:
    Base.metadata.create_all(bind=engine)
    print("¡Tablas creadas en Supabase exitosamente!")
except Exception as e:
    print(f"Error: {e}")
