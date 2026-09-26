import os
from sqlalchemy import create_engine
from app.models.models import Base

URL = "postgresql+psycopg://postgres.lftebaaiooibuhnpivzx:eGv2Ex%5EKgkFJ6yMA7UCr@aws-0-us-east-1.pooler.supabase.com:5432/postgres"

engine = create_engine(URL)

print("Eliminando estructura antigua de Supabase...")
Base.metadata.drop_all(bind=engine)
print("Construyendo nueva arquitectura V2...")
Base.metadata.create_all(bind=engine)
print("¡Base de datos Nivel Pro creada exitosamente!")
