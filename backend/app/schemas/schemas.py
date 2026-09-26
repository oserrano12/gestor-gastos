from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from app.models.models import TipoCategoria, TipoTasa, EstadoCredito, EstadoCuota

# --- Categorías ---
class CategoriaBase(BaseModel):
    nombre: str
    tipo: TipoCategoria

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaResponse(CategoriaBase):
    id: int
    class Config:
        from_attributes = True

# --- Transacciones Corrientes ---
class TransaccionBase(BaseModel):
    categoria_id: int
    monto: Decimal = Field(..., max_digits=12, decimal_places=2)
    fecha: date
    descripcion: Optional[str] = None

class TransaccionCreate(TransaccionBase):
    pass

class TransaccionResponse(TransaccionBase):
    id: int
    creado_en: datetime
    categoria: CategoriaResponse
    
    class Config:
        from_attributes = True

# --- Amortización ---
class CuotaAmortizacionResponse(BaseModel):
    id: int
    numero_cuota: int
    fecha_vencimiento: date
    capital: Decimal
    interes: Decimal
    cuota_total: Decimal
    estado: EstadoCuota
    fecha_pago_real: Optional[date] = None

    class Config:
        from_attributes = True

# --- Créditos ---
class CreditoBase(BaseModel):
    entidad_id: int
    concepto: str
    monto_total: Decimal
    tasa_interes: Decimal
    tipo_tasa: TipoTasa
    numero_cuotas: int
    fecha_compra: date

class CreditoCreate(CreditoBase):
    pass

class CreditoResponse(CreditoBase):
    id: int
    estado: EstadoCredito
    tabla_amortizacion: List[CuotaAmortizacionResponse] = []

    class Config:
        from_attributes = True

# --- Entidades Crediticias ---
class EntidadBase(BaseModel):
    nombre: str
    dia_corte: int
    dia_limite_pago: int

class EntidadCreate(EntidadBase):
    pass

class EntidadResponse(EntidadBase):
    id: int

    class Config:
        from_attributes = True
