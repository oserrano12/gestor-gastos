from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Enum as SQLEnum, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

# Enums para los tipos restringidos
class TipoCategoria(str, enum.Enum):
    ingreso = "Ingreso"
    gasto = "Gasto"

class TipoTasa(str, enum.Enum):
    mv = "MV"
    ea = "EA"

class EstadoCredito(str, enum.Enum):
    activo = "Activo"
    pagado = "Pagado"

class EstadoCuota(str, enum.Enum):
    pendiente = "Pendiente"
    pagada = "Pagada"
    mora = "Mora"

# --- Modelos Nuevos ---
class Cuenta(Base):
    __tablename__ = "cuentas"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    nombre = Column(String, nullable=False) # ej. Efectivo, Bancolombia
    color = Column(String, default="#3b82f6")
    
    transacciones = relationship("TransaccionCorriente", back_populates="cuenta")

class MetaAhorro(Base):
    __tablename__ = "metas_ahorro"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    nombre = Column(String, nullable=False)
    monto_objetivo = Column(Numeric(12, 2), nullable=False)
    monto_actual = Column(Numeric(12, 2), default=0.0)
    fecha_limite = Column(Date, nullable=True)
    completada = Column(Boolean, default=False)

class Presupuesto(Base):
    __tablename__ = "presupuestos"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    monto_limite = Column(Numeric(12, 2), nullable=False)
    mes = Column(Integer, nullable=False)
    anio = Column(Integer, nullable=False)

# --- Modelos Existentes y Modificados ---

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nombre = Column(String, nullable=False)

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    nombre = Column(String, index=True, nullable=False)
    tipo = Column(SQLEnum(TipoCategoria), nullable=False)

    transacciones = relationship("TransaccionCorriente", back_populates="categoria")

class TransaccionCorriente(Base):
    __tablename__ = "transacciones_corrientes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    cuenta_id = Column(Integer, ForeignKey("cuentas.id"), nullable=True) # NUEVO: nullable=True temporalmente para la migracion
    monto = Column(Numeric(12, 2), nullable=False)
    fecha = Column(Date, nullable=False)
    descripcion = Column(String, nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    categoria = relationship("Categoria", back_populates="transacciones")
    cuenta = relationship("Cuenta", back_populates="transacciones")

class Suscripcion(Base):
    __tablename__ = "suscripciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    nombre = Column(String, nullable=False)
    monto = Column(Numeric(12, 2), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    dia_cobro = Column(Integer, nullable=False) 
    activa = Column(Integer, default=1) 
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    categoria = relationship("Categoria")

class EntidadCrediticia(Base):
    __tablename__ = "entidades_crediticias"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    nombre = Column(String, index=True, nullable=False)
    dia_corte = Column(Integer, nullable=False)
    dia_limite_pago = Column(Integer, nullable=False)

    creditos = relationship("CreditoCompra", back_populates="entidad")

class CreditoCompra(Base):
    __tablename__ = "creditos_compras"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    entidad_id = Column(Integer, ForeignKey("entidades_crediticias.id"), nullable=False)
    concepto = Column(String, nullable=False)
    monto_total = Column(Numeric(12, 2), nullable=False)
    tasa_interes = Column(Numeric(5, 4), nullable=False)
    tipo_tasa = Column(SQLEnum(TipoTasa), nullable=False)
    numero_cuotas = Column(Integer, nullable=False)
    fecha_compra = Column(Date, nullable=False)
    estado = Column(SQLEnum(EstadoCredito), default=EstadoCredito.activo, nullable=False)

    entidad = relationship("EntidadCrediticia", back_populates="creditos")
    tabla_amortizacion = relationship("TablaAmortizacion", back_populates="credito", cascade="all, delete-orphan")

class TablaAmortizacion(Base):
    __tablename__ = "tabla_amortizacion"

    id = Column(Integer, primary_key=True, index=True)
    credito_id = Column(Integer, ForeignKey("creditos_compras.id"), nullable=False)
    numero_cuota = Column(Integer, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)
    capital = Column(Numeric(12, 2), nullable=False)
    interes = Column(Numeric(12, 2), nullable=False)
    cuota_total = Column(Numeric(12, 2), nullable=False)
    estado = Column(SQLEnum(EstadoCuota), default=EstadoCuota.pendiente, nullable=False)
    fecha_pago_real = Column(Date, nullable=True)
    cuenta_origen_id = Column(Integer, ForeignKey("cuentas.id"), nullable=True) # NUEVO: para saber de dónde se pagó

    credito = relationship("CreditoCompra", back_populates="tabla_amortizacion")
