from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from app.models.models import TipoCategoria, TipoTasa, EstadoCredito, EstadoCuota

# --- Usuarios ---
class UsuarioCreate(BaseModel):
    email: str
    password: str
    nombre: str

class UsuarioResponse(BaseModel):
    id: int
    email: str
    nombre: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class RecuperarPassword(BaseModel):
    email: str

class ResetearPassword(BaseModel):
    token: str
    new_password: str

# --- Cuentas (NUEVO) ---
class CuentaBase(BaseModel):
    nombre: str
    color: Optional[str] = "#3b82f6"

class CuentaCreate(CuentaBase):
    pass

class CuentaResponse(CuentaBase):
    id: int
    saldo: float
    
    class Config:
        orm_mode = True

# --- Metas de Ahorro (NUEVO) ---
class MetaAhorroBase(BaseModel):
    nombre: str
    monto_objetivo: float
    fecha_limite: Optional[date] = None

class MetaAhorroCreate(MetaAhorroBase):
    pass

class MetaAhorroResponse(MetaAhorroBase):
    id: int
    monto_actual: float
    completada: bool
    
    class Config:
        orm_mode = True

# --- Presupuestos (NUEVO) ---
class PresupuestoBase(BaseModel):
    categoria_id: int
    monto_limite: float
    mes: int
    anio: int

class PresupuestoCreate(PresupuestoBase):
    pass

class PresupuestoResponse(PresupuestoBase):
    id: int
    
    class Config:
        orm_mode = True

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
    cuenta_id: Optional[int] = None # Temporalmente opcional por migración
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

# --- Suscripciones ---
class SuscripcionBase(BaseModel):
    nombre: str
    monto: Decimal = Field(..., max_digits=12, decimal_places=2)
    categoria_id: int
    dia_cobro: int
    activa: int = 1

class SuscripcionCreate(SuscripcionBase):
    pass

class SuscripcionResponse(SuscripcionBase):
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
