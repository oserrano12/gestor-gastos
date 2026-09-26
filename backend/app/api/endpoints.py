from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordRequestForm
from app.db.database import get_db
from app.models import models
from app.schemas import schemas
from app.core import security
from app.services.amortizacion import generar_tabla_amortizacion

router = APIRouter()

# --- Autenticación ---

@router.post("/usuarios/registro", response_model=schemas.UsuarioResponse)
def registrar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    user_db = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if user_db:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    hashed_pw = security.get_password_hash(usuario.password)
    nuevo_usuario = models.Usuario(email=usuario.email, nombre=usuario.nombre, hashed_password=hashed_pw)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    # NUEVO: Crear cuenta Efectivo por defecto
    cuenta = models.Cuenta(usuario_id=nuevo_usuario.id, nombre="Efectivo", color="#10b981")
    db.add(cuenta)
    db.commit()
    
    return nuevo_usuario

@router.post("/usuarios/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
    
    token = security.create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/usuarios/recuperar")
def recuperar_password(data: schemas.RecuperarPassword, db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Correo no encontrado")
    
    # En un sistema real, enviamos esto por correo. Aquí lo devolvemos directo al frontend por facilidad.
    reset_token = security.create_access_token(data={"sub": user.email, "type": "reset"}, expires_delta=security.timedelta(minutes=15))
    return {"mensaje": "Token generado", "reset_token": reset_token}

@router.post("/usuarios/resetear")
def resetear_password(data: schemas.ResetearPassword, db: Session = Depends(get_db)):
    try:
        payload = security.jwt.decode(data.token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        if payload.get("type") != "reset":
            raise HTTPException(status_code=400, detail="Token inválido")
        email = payload.get("sub")
    except security.jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Token expirado o inválido")
    
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user.hashed_password = security.get_password_hash(data.new_password)
    db.commit()
    return {"mensaje": "Contraseña actualizada exitosamente"}

# --- Entidades Crediticias ---
@router.post("/entidades/", response_model=schemas.EntidadResponse)
def crear_entidad(entidad: schemas.EntidadCreate, db: Session = Depends(get_db), current_user: models.Usuario = Depends(security.get_current_user)):
    db_entidad = models.EntidadCrediticia(**entidad.model_dump(), usuario_id=current_user.id)
    db.add(db_entidad)
    db.commit()
    db.refresh(db_entidad)
    return db_entidad

@router.get("/entidades/", response_model=List[schemas.EntidadResponse])
def obtener_entidades(db: Session = Depends(get_db), current_user: models.Usuario = Depends(security.get_current_user)):
    return db.query(models.EntidadCrediticia).filter(models.EntidadCrediticia.usuario_id == current_user.id).all()

# --- Categorías ---
@router.post("/categorias/", response_model=schemas.CategoriaResponse)
def crear_categoria(categoria: schemas.CategoriaCreate, db: Session = Depends(get_db), current_user: models.Usuario = Depends(security.get_current_user)):
    db_cat = models.Categoria(**categoria.model_dump(), usuario_id=current_user.id)
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@router.get("/categorias/", response_model=List[schemas.CategoriaResponse])
def obtener_categorias(db: Session = Depends(get_db), current_user: models.Usuario = Depends(security.get_current_user)):
    return db.query(models.Categoria).filter(models.Categoria.usuario_id == current_user.id).all()

# --- Transacciones Corrientes ---

@router.post("/transacciones/", response_model=schemas.TransaccionResponse)
def crear_transaccion(transaccion: schemas.TransaccionCreate, db: Session = Depends(get_db), current_user: models.Usuario = Depends(security.get_current_user)):
    db_transaccion = models.TransaccionCorriente(**transaccion.model_dump(), usuario_id=current_user.id)
    db.add(db_transaccion)
    db.commit()
    db.refresh(db_transaccion)
    return db_transaccion

@router.get("/transacciones/", response_model=List[schemas.TransaccionResponse])
def obtener_transacciones(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.Usuario = Depends(security.get_current_user)):
    return db.query(models.TransaccionCorriente).filter(models.TransaccionCorriente.usuario_id == current_user.id).offset(skip).limit(limit).all()

# --- Suscripciones ---

@router.post("/suscripciones/", response_model=schemas.SuscripcionResponse)
def crear_suscripcion(suscripcion: schemas.SuscripcionCreate, db: Session = Depends(get_db), current_user: models.Usuario = Depends(security.get_current_user)):
    db_susc = models.Suscripcion(**suscripcion.model_dump(), usuario_id=current_user.id)
    db.add(db_susc)
    db.commit()
    db.refresh(db_susc)
    return db_susc

@router.get("/suscripciones/", response_model=List[schemas.SuscripcionResponse])
def obtener_suscripciones(db: Session = Depends(get_db), current_user: models.Usuario = Depends(security.get_current_user)):
    return db.query(models.Suscripcion).filter(models.Suscripcion.usuario_id == current_user.id, models.Suscripcion.activa == 1).all()

# --- Créditos y Amortización ---

@router.post("/creditos/", response_model=schemas.CreditoResponse)
def crear_credito(credito: schemas.CreditoCreate, db: Session = Depends(get_db), current_user: models.Usuario = Depends(security.get_current_user)):
    entidad = db.query(models.EntidadCrediticia).filter(models.EntidadCrediticia.id == credito.entidad_id, models.EntidadCrediticia.usuario_id == current_user.id).first()
    if not entidad:
        raise HTTPException(status_code=404, detail="Entidad crediticia no encontrada")
    
    nuevo_credito = models.CreditoCompra(**credito.model_dump(), usuario_id=current_user.id)
    db.add(nuevo_credito)
    db.commit()
    db.refresh(nuevo_credito)

    tabla_dicts = generar_tabla_amortizacion(
        monto=nuevo_credito.monto_total,
        tasa=nuevo_credito.tasa_interes,
        tipo_tasa=nuevo_credito.tipo_tasa.value,
        n_cuotas=nuevo_credito.numero_cuotas,
        fecha_compra=nuevo_credito.fecha_compra,
        dia_corte=entidad.dia_corte,
        dia_limite_pago=entidad.dia_limite_pago
    )

    for cuota in tabla_dicts:
        db_cuota = models.TablaAmortizacion(
            credito_id=nuevo_credito.id,
            numero_cuota=cuota["numero_cuota"],
            fecha_vencimiento=cuota["fecha_vencimiento"],
            capital=cuota["capital"],
            interes=cuota["interes"],
            cuota_total=cuota["cuota_total"]
        )
        db.add(db_cuota)
    db.commit()
    
    db.refresh(nuevo_credito)
    return nuevo_credito

@router.get("/cuotas/pendientes/", response_model=List[schemas.CuotaAmortizacionResponse])
def obtener_cuotas_pendientes(db: Session = Depends(get_db), current_user: models.Usuario = Depends(security.get_current_user)):
    # Filtrar cuotas pendientes de créditos de ESTE usuario
    return db.query(models.TablaAmortizacion)\
             .join(models.CreditoCompra)\
             .filter(models.CreditoCompra.usuario_id == current_user.id)\
             .filter(models.TablaAmortizacion.estado == "Pendiente")\
             .order_by(models.TablaAmortizacion.fecha_vencimiento.asc())\
             .all()

# --- Cuentas ---
@router.get('/cuentas/', response_model=List[schemas.CuentaResponse])
def obtener_cuentas(db: Session = Depends(get_db), current_user: models.Usuario = Depends(security.get_current_user)):
    return db.query(models.Cuenta).filter(models.Cuenta.usuario_id == current_user.id).all()

@router.post('/cuentas/', response_model=schemas.CuentaResponse)
def crear_cuenta(cuenta: schemas.CuentaCreate, db: Session = Depends(get_db), current_user: models.Usuario = Depends(security.get_current_user)):
    nueva_cuenta = models.Cuenta(usuario_id=current_user.id, nombre=cuenta.nombre, color=cuenta.color)
    db.add(nueva_cuenta)
    db.commit()
    db.refresh(nueva_cuenta)
    return nueva_cuenta

