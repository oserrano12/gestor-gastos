from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models import models
from app.schemas import schemas
from app.services.amortizacion import generar_tabla_amortizacion

router = APIRouter()

# --- Entidades Crediticias ---
@router.post("/entidades/", response_model=schemas.EntidadResponse)
def crear_entidad(entidad: schemas.EntidadCreate, db: Session = Depends(get_db)):
    db_entidad = models.EntidadCrediticia(**entidad.model_dump())
    db.add(db_entidad)
    db.commit()
    db.refresh(db_entidad)
    return db_entidad

@router.get("/entidades/", response_model=List[schemas.EntidadResponse])
def obtener_entidades(db: Session = Depends(get_db)):
    return db.query(models.EntidadCrediticia).all()

# --- Transacciones Corrientes ---

@router.post("/transacciones/", response_model=schemas.TransaccionResponse)
def crear_transaccion(transaccion: schemas.TransaccionCreate, db: Session = Depends(get_db)):
    db_transaccion = models.TransaccionCorriente(**transaccion.model_dump())
    db.add(db_transaccion)
    db.commit()
    db.refresh(db_transaccion)
    return db_transaccion

@router.get("/transacciones/", response_model=List[schemas.TransaccionResponse])
def obtener_transacciones(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.TransaccionCorriente).offset(skip).limit(limit).all()

# --- Créditos y Amortización ---

@router.post("/creditos/", response_model=schemas.CreditoResponse)
def crear_credito(credito: schemas.CreditoCreate, db: Session = Depends(get_db)):
    # 1. Obtener la entidad para saber los días de corte y límite de pago
    entidad = db.query(models.EntidadCrediticia).filter(models.EntidadCrediticia.id == credito.entidad_id).first()
    if not entidad:
        raise HTTPException(status_code=404, detail="Entidad crediticia no encontrada")

    # 2. Guardar el crédito base
    db_credito = models.CreditoCompra(**credito.model_dump())
    db.add(db_credito)
    db.commit()
    db.refresh(db_credito)

    # 3. Generar la tabla de amortización usando nuestro motor financiero
    tabla_generada = generar_tabla_amortizacion(
        monto_total=db_credito.monto_total,
        tasa_interes=db_credito.tasa_interes,
        tipo_tasa=db_credito.tipo_tasa,
        numero_cuotas=db_credito.numero_cuotas,
        fecha_compra=db_credito.fecha_compra,
        dia_corte=entidad.dia_corte,
        dia_limite_pago=entidad.dia_limite_pago
    )

    # 4. Guardar cada cuota en la base de datos
    for cuota_data in tabla_generada:
        db_cuota = models.TablaAmortizacion(
            credito_id=db_credito.id,
            numero_cuota=cuota_data["numero_cuota"],
            fecha_vencimiento=cuota_data["fecha_vencimiento"],
            capital=cuota_data["capital"],
            interes=cuota_data["interes"],
            cuota_total=cuota_data["cuota_total"],
            estado=models.EstadoCuota.pendiente
        )
        db.add(db_cuota)
    
    db.commit()
    db.refresh(db_credito) # Refrescar para obtener la tabla asociada por relationship
    return db_credito

@router.get("/cuotas/pendientes/", response_model=List[schemas.CuotaAmortizacionResponse])
def obtener_cuotas_pendientes(db: Session = Depends(get_db)):
    """Obtiene todas las cuotas que están pendientes de pago."""
    return db.query(models.TablaAmortizacion).filter(
        models.TablaAmortizacion.estado == models.EstadoCuota.pendiente
    ).order_by(models.TablaAmortizacion.fecha_vencimiento).all()
