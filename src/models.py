from sqlalchemy import (
    Column, Integer, String, BigInteger, Boolean,
    Numeric, Date, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from database import Base


# ─── Modelos base de ubicación ───────────────────────────────────────────────

class Localidad(Base):
    __tablename__ = "localidad"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)

    clientes = relationship("Cliente", back_populates="localidad")

    def __repr__(self):
        return f"<Localidad {self.nombre}>"


class Barrio(Base):
    __tablename__ = "barrio"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)

    clientes = relationship("Cliente", back_populates="barrio")

    def __repr__(self):
        return f"<Barrio {self.nombre}>"


class Provincia(Base):
    __tablename__ = "provincia"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)

    clientes = relationship("Cliente", back_populates="provincia")

    def __repr__(self):
        return f"<Provincia {self.nombre}>"


# ─── Ingredientes y Recetas ──────────────────────────────────────────────────

class UnidadMedida(Base):
    __tablename__ = "unidad_medida"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)

    ingredientes = relationship("Ingrediente", back_populates="unidad_medida")

    def __repr__(self):
        return f"<UnidadMedida {self.nombre}>"


class Ingrediente(Base):
    __tablename__ = "ingrediente"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    costo = Column(Numeric(15, 2), default=0, nullable=False)
    unidad_medida_id = Column(Integer, ForeignKey("unidad_medida.id"), nullable=False)

    unidad_medida = relationship("UnidadMedida", back_populates="ingredientes")
    recetas = relationship("Receta", back_populates="ingrediente")

    def __repr__(self):
        return f"<Ingrediente {self.nombre} ${self.costo}>"


class Producto(Base):
    __tablename__ = "producto"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    ganancia = Column(Numeric(15, 2), default=0, nullable=False)
    es_relleno = Column(Boolean, default=False, nullable=False)

    recetas = relationship("Receta", back_populates="producto", lazy="joined")
    detalle_ventas = relationship("DetalleVenta", back_populates="producto")
    descuento = Column(Numeric(5, 2), default=0, nullable=False)  # nuevo (ejemplo tuto)

    @property
    def precio(self) -> float:
        """
        Calcula el precio multiplicando el costo de cada ingrediente
        por su cantidad en la receta, luego aplica el coeficiente de ganancia.
        """
        total = sum(
            float(r.cantidad) * float(r.ingrediente.costo)
            for r in self.recetas
        )
        return round(total * float(self.ganancia), 2)

    def __repr__(self):
        return f"<Producto {self.nombre} ${self.precio}>"


class Receta(Base):
    __tablename__ = "receta"

    id = Column(Integer, primary_key=True, index=True)
    cantidad = Column(Numeric(15, 3), default=0, nullable=False)
    ingrediente_id = Column(Integer, ForeignKey("ingrediente.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("producto.id"), nullable=False)

    ingrediente = relationship("Ingrediente", back_populates="recetas", lazy="joined")
    producto = relationship("Producto", back_populates="recetas")

    def __repr__(self):
        return f"<Receta producto={self.producto_id} ingrediente={self.ingrediente_id}>"


# ─── Clientes y Ventas ───────────────────────────────────────────────────────

class Cliente(Base):
    __tablename__ = "cliente"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    numero_documento = Column(BigInteger, nullable=True)
    direccion = Column(String(200), nullable=True)
    celular = Column(BigInteger, nullable=True)
    telefono = Column(BigInteger, nullable=True)
    email = Column(String(254), nullable=True)
    barrio_id = Column(Integer, ForeignKey("barrio.id"), nullable=True)
    localidad_id = Column(Integer, ForeignKey("localidad.id"), nullable=True)
    provincia_id = Column(Integer, ForeignKey("provincia.id"), nullable=True)

    barrio = relationship("Barrio", back_populates="clientes")
    localidad = relationship("Localidad", back_populates="clientes")
    provincia = relationship("Provincia", back_populates="clientes")
    compras = relationship("Venta", back_populates="cliente")

    __table_args__ = (
        Index("ix_cliente_documento", "numero_documento"),
    )

    def __repr__(self):
        return f"<Cliente {self.nombre} DNI={self.numero_documento}>"


class Venta(Base):
    __tablename__ = "venta"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False)
    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=False)

    cliente = relationship("Cliente", back_populates="compras")
    detalle = relationship("DetalleVenta", back_populates="venta")

    def __repr__(self):
        return f"<Venta {self.fecha} cliente={self.cliente_id}>"


class DetalleVenta(Base):
    __tablename__ = "detalle_venta"

    id = Column(Integer, primary_key=True, index=True)
    cantidad = Column(Numeric(15, 2), nullable=True)
    venta_id = Column(Integer, ForeignKey("venta.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("producto.id"), nullable=False)

    venta = relationship("Venta", back_populates="detalle")
    producto = relationship("Producto", back_populates="detalle_ventas")

    def __repr__(self):
        return f"<DetalleVenta venta={self.venta_id} producto={self.producto_id}>"
