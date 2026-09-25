from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Enum as SQLEnum, DateTime
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

# --- Modelos ---

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    tipo = Column(SQLEnum(TipoCategoria), nullable=False)

    transacciones = relationship("TransaccionCorriente", back_populates="categoria")


class TransaccionCorriente(Base):
    __tablename__ = "transacciones_corrientes"

    id = Column(Integer, primary_key=True, index=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    monto = Column(Numeric(12, 2), nullable=False)
    fecha = Column(Date, nullable=False)
    descripcion = Column(String, nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    categoria = relationship("Categoria", back_populates="transacciones")


class EntidadCrediticia(Base):
    __tablename__ = "entidades_crediticias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    dia_corte = Column(Integer, nullable=False)
    dia_limite_pago = Column(Integer, nullable=False)

    creditos = relationship("CreditoCompra", back_populates="entidad")


class CreditoCompra(Base):
    __tablename__ = "creditos_compras"

    id = Column(Integer, primary_key=True, index=True)
    entidad_id = Column(Integer, ForeignKey("entidades_crediticias.id"), nullable=False)
    concepto = Column(String, nullable=False)
    monto_total = Column(Numeric(12, 2), nullable=False)
    tasa_interes = Column(Numeric(5, 4), nullable=False) # Ejemplo: 0.0215 representa 2.15%
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

    credito = relationship("CreditoCompra", back_populates="tabla_amortizacion")
