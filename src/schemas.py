from pydantic import BaseModel
from datetime import date
from decimal import Decimal
from typing import Optional


# ─── UnidadMedida ────────────────────────────────────────────────────────────

class UnidadMedidaBase(BaseModel):
    nombre: str


class UnidadMedidaCreate(UnidadMedidaBase):
    pass


class UnidadMedidaOut(UnidadMedidaBase):
    id: int
    model_config = {"from_attributes": True}


# ─── Ingrediente ─────────────────────────────────────────────────────────────

class IngredienteBase(BaseModel):
    nombre: str
    costo: Decimal
    unidad_medida_id: int


class IngredienteCreate(IngredienteBase):
    pass


class IngredienteOut(IngredienteBase):
    id: int
    unidad_medida: UnidadMedidaOut
    model_config = {"from_attributes": True}


# ─── Receta ──────────────────────────────────────────────────────────────────

class RecetaBase(BaseModel):
    cantidad: Decimal
    ingrediente_id: int


class RecetaCreate(RecetaBase):
    pass


class RecetaOut(RecetaBase):
    id: int
    ingrediente: IngredienteOut
    model_config = {"from_attributes": True}


# ─── Producto ────────────────────────────────────────────────────────────────

class ProductoBase(BaseModel):
    nombre: str
    ganancia: Decimal
    es_relleno: bool = False
    descuento: Decimal = 0  # agregar (ejemplo tuto)


class ProductoCreate(ProductoBase):
    pass


class ProductoOut(ProductoBase):
    id: int
    precio: float
    recetas: list[RecetaOut] = []
    model_config = {"from_attributes": True}


# ─── Cliente ─────────────────────────────────────────────────────────────────

class ClienteBase(BaseModel):
    nombre: str
    numero_documento: Optional[int] = None
    direccion: Optional[str] = None
    celular: Optional[int] = None
    telefono: Optional[int] = None
    email: Optional[str] = None
    barrio_id: Optional[int] = None
    localidad_id: Optional[int] = None
    provincia_id: Optional[int] = None


class ClienteCreate(ClienteBase):
    pass


class ClienteOut(ClienteBase):
    id: int
    model_config = {"from_attributes": True}


# ─── Venta ───────────────────────────────────────────────────────────────────

class DetalleVentaBase(BaseModel):
    producto_id: int
    cantidad: Decimal


class DetalleVentaCreate(DetalleVentaBase):
    pass


class DetalleVentaOut(DetalleVentaBase):
    id: int
    model_config = {"from_attributes": True}


class VentaBase(BaseModel):
    fecha: date
    cliente_id: int


class VentaCreate(VentaBase):
    detalle: list[DetalleVentaCreate]


class VentaOut(VentaBase):
    id: int
    detalle: list[DetalleVentaOut] = []
    model_config = {"from_attributes": True}
