import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Usuario

URL = "postgresql+psycopg://postgres.lftebaaiooibuhnpivzx:eGv2Ex%5EKgkFJ6yMA7UCr@aws-0-us-east-1.pooler.supabase.com:5432/postgres"
engine = create_engine(URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

print("Eliminando todos los usuarios...")
db.query(Usuario).delete()
db.commit()
print("Usuarios eliminados.")
db.close()
