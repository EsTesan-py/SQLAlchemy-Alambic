# Tutorial: Aplicación de Fábrica de Pastas con SQLAlchemy + FastAPI + Docker

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-6DB33F?style=for-the-badge&logoColor=white)
![Python 3.13](https://img.shields.io/badge/Python%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL 17](https://img.shields.io/badge/PostgreSQL%2017-336791?style=for-the-badge&logo=postgresql&logoColor=white)

> Este tutorial replica la aplicación de Fábrica de Pastas del tutorial Django, pero **sin Django**. Usamos SQLAlchemy como ORM, Alembic para migraciones y FastAPI como framework web. El resultado es un stack más liviano, explícito y portable.

---

## ¿Por qué este stack?

| Rol | Django (original) | Este tutorial |
|---|---|---|
| Framework web | Django | FastAPI |
| ORM | Django ORM | SQLAlchemy |
| Migraciones | makemigrations | Alembic |
| Admin | Django Admin | Interfaz propia vía API |
| Validación | Django Forms | Pydantic |
| Servidor | gunicorn | uvicorn |

**FastAPI** es el complemento natural de SQLAlchemy: comparten el mismo ecosistema Python moderno, FastAPI usa Pydantic para validación de datos y provee documentación automática de la API en `/docs`.

---

## Requisitos Previos

- **Docker** y **Docker Compose** instalados. Ver [documentación oficial](https://docs.docker.com/get-docker/).
- Conocimientos básicos de Python.

---

## 1. Estructura del Proyecto

```sh
mkdir fabrica
cd fabrica/
```

Hermoso Diagrama de la Estructura final:

```
fabrica/
├── .env.db
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── src/
    ├── main.py                  # Punto de entrada FastAPI
    ├── database.py              # Engine, sesión y Base
    ├── models.py                # Modelos SQLAlchemy 
    ├── schemas.py               # Esquemas Pydantic (validación)
    ├── routers/
    │   ├── productos.py
    │   ├── clientes.py
    │   ├── ventas.py
    │   ├── ingredientes.py
    │   ├── __init__.py
    │   └── __pycache__/
    │       ├── productos.pyc
    │       ├── clientes.pyc
    │       ├── ventas.pyc
    │       ├── ingredientes.pyc
    │       └── __init__.pyc
    ├── migrations/              # Generado por Alembic (debería ser algo más o menos así)
    │   ├── env.py
    │   ├── versions/
    │   │   └── __pycache__/
    │   │       └── ab71c68efd34_inicial.cpython-313.pyc
    │   ├── __pycache__
    │   │   └── env.cpython-313.pyc
    │   ├── README
    │   └── script.py.mako
    ├── __pycache__
    │   ├── database.cpython-313.pyc
    │   ├── main.cpython-313.pyc
    │   ├── models.cpython-313.pyc
    │   └── schemas.cpython-313.pyc
    ├── alembic.ini
    └── fixtures/
        └── initial_data.py
```

---

## 2. Dependencias

> **Pega esto en `requirements.txt`.**

```txt
# Base de datos
SQLAlchemy
psycopg2-binary         # Driver PostgreSQL
alembic                 # Migraciones

# Validación y serialización
pydantic
pydantic-settings       # Lectura de variables de entorno

# Utilidades
python-multipart        # Para formularios en FastAPI
```

---

## 3. Dockerfile

> **Pega esto en `Dockerfile`.**

```dockerfile
FROM python:3.13-alpine AS base
LABEL maintainer="PINDU"
RUN apk --no-cache add bash curl gcc musl-dev libffi-dev g++ make build-base

FROM base AS builder
COPY ./requirements.txt .
RUN pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt \
  && rm requirements.txt

FROM base
RUN mkdir /code
WORKDIR /code
COPY ./requirements.txt .
RUN pip install -r requirements.txt && rm requirements.txt
COPY --chown=user:group --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
ENV PATH /usr/local/lib/python3.13/site-packages:$PATH
RUN ln -s /usr/share/zoneinfo/America/Cordoba /etc/localtime

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 4. Variables de Entorno

> **Pega esto en `.env.db`.**

```conf
# .env.db
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=postgres
PGUSER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST_AUTH_METHOD=scram-sha-256
POSTGRES_INITDB_ARGS="--locale-provider=icu --icu-locale=es-AR --auth-local=trust"

# URL de conexión para SQLAlchemy
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/postgres
```

---

## 5. Docker Compose

> **Pega esto en `docker-compose.yml`.**

```yml
services:
  db:
    image: postgres:alpine
    env_file:
      - .env.db
    healthcheck:
      test: [ "CMD-SHELL", "pg_isready" ]
      interval: 10s
      timeout: 2s
      retries: 5
    volumes:
      - postgres-db:/var/lib/postgresql
    networks:
      - net

  backend:
    build: .
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    env_file:
      - .env.db
    ports:
      - "8000:8000"
    volumes:
      - ./src:/code
    depends_on:
      db:
        condition: service_healthy
    networks:
      - net

  alembic:
    build: .
    entrypoint: alembic
    env_file:
      - .env.db
    volumes:
      - ./src:/code
    depends_on:
      db:
        condition: service_healthy
    networks:
      - net

  fixtures:
    build: .
    command: ["python", "fixtures/initial_data.py"]
    env_file:
      - .env.db
    volumes:
      - ./src:/code
    depends_on:
      db:
        condition: service_healthy
    networks:
      - net

networks:
  net:

volumes:
  postgres-db:
```

---

## 6. Configuración de la Base de Datos

> **Crea `./src/database.py`.**

```python
# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = os.environ["DATABASE_URL"]

# pool_pre_ping=True: verifica la conexión antes de usarla.
# Esencial en Docker donde el contenedor de DB puede reiniciarse.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """
    Dependencia de FastAPI: provee una sesión de DB por request
    y la cierra automáticamente al terminar.

    Uso en un router:
        @router.get("/productos")
        def lista(db: Session = Depends(get_db)):
            return db.query(Producto).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 7. Modelos SQLAlchemy

Estos son exactamente los mismos modelos de la Fábrica de Pastas del tutorial Django, reescritos para SQLAlchemy.

> **Crea `./src/models.py`.**

```python
# models.py
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

    @property
    def precio(self) -> float:
        """
        Calcula el precio multiplicando el costo de cada ingrediente
        por su cantidad en la receta, luego aplica el coeficiente de ganancia.
        Replica la lógica del modelo Django original.
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
```

---

## 8. Esquemas Pydantic

Pydantic cumple el rol de validación que en Django hacían los Forms y los Serializers. Define qué datos se aceptan en cada endpoint y cómo se serializan las respuestas.

> **Crea `./src/schemas.py`.**

```python
# schemas.py
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
    email: Optional[Str] = None
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
```

---

## 9. Routers (Endpoints de la API)

Cada recurso tiene su propio router, equivalente a las `views.py` de Django.

### 9.1 Productos

> **Crea `./src/routers/productos.py`.**

```python
# routers/productos.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Producto, Receta
from schemas import ProductoCreate, ProductoOut

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.get("/", response_model=list[ProductoOut])
def listar_productos(db: Session = Depends(get_db)):
    return db.query(Producto).order_by(Producto.nombre).all()


@router.get("/{producto_id}", response_model=ProductoOut)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.post("/", response_model=ProductoOut, status_code=201)
def crear_producto(data: ProductoCreate, db: Session = Depends(get_db)):
    producto = Producto(**data.model_dump())
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto


@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar_producto(producto_id: int, data: ProductoCreate, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for key, value in data.model_dump().items():
        setattr(producto, key, value)
    db.commit()
    db.refresh(producto)
    return producto


@router.delete("/{producto_id}", status_code=204)
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(producto)
    db.commit()
```

### 9.2 Clientes

> **Crea `./src/routers/clientes.py`.**

```python
# routers/clientes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Cliente
from schemas import ClienteCreate, ClienteOut

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("/", response_model=list[ClienteOut])
def listar_clientes(db: Session = Depends(get_db)):
    return db.query(Cliente).order_by(Cliente.nombre).all()


@router.get("/{cliente_id}", response_model=ClienteOut)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.get("/documento/{numero_documento}", response_model=ClienteOut)
def buscar_por_documento(numero_documento: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(
        Cliente.numero_documento == numero_documento
    ).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.post("/", response_model=ClienteOut, status_code=201)
def crear_cliente(data: ClienteCreate, db: Session = Depends(get_db)):
    cliente = Cliente(**data.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


@router.put("/{cliente_id}", response_model=ClienteOut)
def actualizar_cliente(cliente_id: int, data: ClienteCreate, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    for key, value in data.model_dump().items():
        setattr(cliente, key, value)
    db.commit()
    db.refresh(cliente)
    return cliente


@router.delete("/{cliente_id}", status_code=204)
def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    db.delete(cliente)
    db.commit()
```

### 9.3 Ventas

> **Crea `./src/routers/ventas.py`.**

```python
# routers/ventas.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Venta, DetalleVenta
from schemas import VentaCreate, VentaOut

router = APIRouter(prefix="/ventas", tags=["Ventas"])


@router.get("/", response_model=list[VentaOut])
def listar_ventas(db: Session = Depends(get_db)):
    return db.query(Venta).order_by(Venta.fecha.desc()).all()


@router.get("/{venta_id}", response_model=VentaOut)
def obtener_venta(venta_id: int, db: Session = Depends(get_db)):
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta


@router.post("/", response_model=VentaOut, status_code=201)
def crear_venta(data: VentaCreate, db: Session = Depends(get_db)):
    # Creamos la venta
    venta = Venta(fecha=data.fecha, cliente_id=data.cliente_id)
    db.add(venta)
    db.flush()  # flush para obtener el ID antes de commit

    # Creamos el detalle
    for item in data.detalle:
        detalle = DetalleVenta(
            venta_id=venta.id,
            producto_id=item.producto_id,
            cantidad=item.cantidad,
        )
        db.add(detalle)

    db.commit()
    db.refresh(venta)
    return venta


@router.delete("/{venta_id}", status_code=204)
def eliminar_venta(venta_id: int, db: Session = Depends(get_db)):
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    db.delete(venta)
    db.commit()
```

### 9.4 Ingredientes

> **Crea `./src/routers/ingredientes.py`.**

```python
# routers/ingredientes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Ingrediente
from schemas import IngredienteCreate, IngredienteOut

router = APIRouter(prefix="/ingredientes", tags=["Ingredientes"])


@router.get("/", response_model=list[IngredienteOut])
def listar_ingredientes(db: Session = Depends(get_db)):
    return db.query(Ingrediente).order_by(Ingrediente.nombre).all()


@router.get("/{ingrediente_id}", response_model=IngredienteOut)
def obtener_ingrediente(ingrediente_id: int, db: Session = Depends(get_db)):
    ing = db.query(Ingrediente).filter(Ingrediente.id == ingrediente_id).first()
    if not ing:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
    return ing


@router.post("/", response_model=IngredienteOut, status_code=201)
def crear_ingrediente(data: IngredienteCreate, db: Session = Depends(get_db)):
    ing = Ingrediente(**data.model_dump())
    db.add(ing)
    db.commit()
    db.refresh(ing)
    return ing


@router.put("/{ingrediente_id}", response_model=IngredienteOut)
def actualizar_ingrediente(ingrediente_id: int, data: IngredienteCreate, db: Session = Depends(get_db)):
    ing = db.query(Ingrediente).filter(Ingrediente.id == ingrediente_id).first()
    if not ing:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
    for key, value in data.model_dump().items():
        setattr(ing, key, value)
    db.commit()
    db.refresh(ing)
    return ing


@router.delete("/{ingrediente_id}", status_code=204)
def eliminar_ingrediente(ingrediente_id: int, db: Session = Depends(get_db)):
    ing = db.query(Ingrediente).filter(Ingrediente.id == ingrediente_id).first()
    if not ing:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
    db.delete(ing)
    db.commit()
```

---

## 10. Punto de Entrada de la Aplicación

> **Crea `./src/main.py`.**

```python
# main.py
from fastapi import FastAPI
from routers import productos, clientes, ventas, ingredientes

app = FastAPI(
    title="Fábrica de Pastas API",
    description="Sistema de gestión para fábrica de pastas artesanales",
    version="1.0.0",
)

# Registrar routers
app.include_router(productos.router)
app.include_router(clientes.router)
app.include_router(ventas.router)
app.include_router(ingredientes.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": "Fábrica de Pastas"}
```

También necesitamos el `__init__.py` del paquete routers:

> **Crea `./src/routers/__init__.py`** (vacío).

```python
# routers/__init__.py
```

---

## 11. Migraciones con Alembic

### 11.1 Inicializar Alembic

```sh
docker compose run --rm alembic init migrations
sudo chown $USER:$USER -R .
```

### 11.2 Configurar `alembic.ini`

En `./src/alembic.ini`, reemplazá la línea de `sqlalchemy.url`:

```ini
sqlalchemy.url = %(DATABASE_URL)s
```

### 11.3 Configurar `./src/migrations/env.py`

Reemplazá todo en el archivo generado, debería quedar así (completo):

```python
# ./src/migrations/env.py
import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Agrega src/ al path para que Alembic encuentre database.py y models.py
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Importa la Base y los modelos para que Alembic los detecte
from database import Base
import models  

config = context.config

# Lee DATABASE_URL desde la variable de entorno del .env.db
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Le dice a Alembic qué tablas tiene que vigilar
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 11.4 Generar y aplicar la migración inicial

```sh
# Detecta los modelos y genera el script de migración
docker compose run --rm alembic revision --autogenerate -m "initial"

# Aplica la migración (crea las tablas en la DB)
docker compose run --rm alembic upgrade head

sudo chown $USER:$USER -R .
```

---

## 12. Carga de Datos Iniciales

Mismos datos que el tutorial Django, cargados con SQLAlchemy directamente.

> **Crea `./src/fixtures/initial_data.py`.**

```python
# fixtures/initial_data.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import SessionLocal
from models import UnidadMedida, Ingrediente, Producto, Receta, Barrio, Localidad, Provincia


def load():
    db = SessionLocal()
    try:
        print("Cargando datos iniciales...")

        # Unidades de medida
        kilo = UnidadMedida(id=1, nombre="KILO")
        unidad = UnidadMedida(id=2, nombre="UNIDAD")
        db.add_all([kilo, unidad])
        db.flush()

        # Ingredientes
        ingredientes = [
            Ingrediente(id=1, nombre="HARINA",   costo=50.00,  unidad_medida_id=1),
            Ingrediente(id=2, nombre="SAL",       costo=50.00,  unidad_medida_id=1),
            Ingrediente(id=3, nombre="HUEVO",     costo=10.00,  unidad_medida_id=2),
            Ingrediente(id=4, nombre="JAMÓN",     costo=600.00, unidad_medida_id=1),
            Ingrediente(id=5, nombre="QUESO",     costo=250.00, unidad_medida_id=1),
            Ingrediente(id=6, nombre="ESPINACA",  costo=100.00, unidad_medida_id=1),
        ]
        db.add_all(ingredientes)
        db.flush()

        # Productos
        productos = [
            Producto(id=1, nombre="TALLARIN",                ganancia=2.00, es_relleno=False),
            Producto(id=2, nombre="RAVIOLI ESPINACA",        ganancia=3.00, es_relleno=True),
            Producto(id=3, nombre="SORRENTINO JAMÓN Y QUESO", ganancia=3.80, es_relleno=True),
        ]
        db.add_all(productos)
        db.flush()

        # Recetas
        recetas = [
            # Tallarín
            Receta(cantidad=0.90, ingrediente_id=1, producto_id=1),
            Receta(cantidad=0.05, ingrediente_id=2, producto_id=1),
            Receta(cantidad=4.00, ingrediente_id=3, producto_id=1),
            # Ravioli Espinaca
            Receta(cantidad=0.60, ingrediente_id=1, producto_id=2),
            Receta(cantidad=4.00, ingrediente_id=3, producto_id=2),
            Receta(cantidad=0.30, ingrediente_id=6, producto_id=2),
            # Sorrentino Jamón y Queso
            Receta(cantidad=0.60, ingrediente_id=1, producto_id=3),
            Receta(cantidad=4.00, ingrediente_id=3, producto_id=3),
            Receta(cantidad=0.15, ingrediente_id=4, producto_id=3),
            Receta(cantidad=0.15, ingrediente_id=5, producto_id=3),
        ]
        db.add_all(recetas)

        # Ubicaciones
        barrios = [
            Barrio(id=1, nombre="CENTRO"),
            Barrio(id=2, nombre="LAMADRID"),
            Barrio(id=3, nombre="AMEGHINO"),
        ]
        localidades = [
            Localidad(id=1, nombre="VILLA MARÍA"),
        ]
        provincias = [
            Provincia(id=1, nombre="CÓRDOBA"),
        ]
        db.add_all(barrios + localidades + provincias)

        db.commit()
        print("✅ Datos iniciales cargados correctamente.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load()
```

---

## 13. Primer Arranque

Ejecutar en orden:

```sh
# 1. Construir las imágenes
docker compose build

# 2. Levantar la DB
docker compose up -d db

# 3. Generar y aplicar migraciones
docker compose run --rm alembic revision --autogenerate -m "initial"
docker compose run --rm alembic upgrade head

# 4. Cargar datos de ejemplo
docker compose run --rm fixtures

# 5. Levantar el backend
docker compose up -d backend

# 6. Ver logs
docker compose logs -f backend
```

---

## 14. Documentación Automática de la API

FastAPI genera documentación interactiva automáticamente:

| URL | Descripción |
|---|---|
| `http://localhost:8000` | Debería salir algo como {"status": "ok", "app": "Fábrica de Pastas"} si todo salio bien
| `http://localhost:8000/docs` | Swagger UI — probar endpoints interactivamente |
| `http://localhost:8000/redoc` | ReDoc — documentación navegable |
| `http://localhost:8000/openapi.json` | Schema OpenAPI en JSON |

Desde `/docs` podés crear productos, registrar ventas, buscar clientes y probar todos los endpoints sin ninguna herramienta externa.

---

## 15. Comandos Útiles

**Migraciones:**
```sh
# Nueva migración tras modificar models.py
docker compose run --rm alembic revision --autogenerate -m "descripcion"
docker compose run --rm alembic upgrade head

# Ver historial de migraciones
docker compose run --rm alembic history

# Rollback de la última migración
docker compose run --rm alembic downgrade -1
```

**Sesión interactiva de Python con acceso a la DB:**
```sh
docker compose run --rm backend python
# >>> from database import SessionLocal
# >>> from models import Producto
# >>> db = SessionLocal()
# >>> db.query(Producto).all()
```

**Detener y limpiar:**
```sh
docker compose down
docker compose down -v --remove-orphans --rmi all
docker system prune -a
```

**Cambiar permisos:**
```sh
sudo chown $USER:$USER -R .
```

---
## Ejemplo

**Para el ejemplo agregamos un descuento a la tabla productos**
**Modificamos la tabla de productos en `./src/models.py`**

```Python

    class Producto(Base):
        tablename = "producto"

        id = Column(Integer, primary_key=True, index=True)
        nombre = Column(String(200), nullable=False)
        ganancia = Column(Numeric(15, 2), default=0, nullable=False)
        es_relleno = Column(Boolean, default=False, nullable=False)
        descuento = Column(Numeric(5, 2), default=0, nullable=False)  # nuevo campo/atributo

```
**Creamos la nueva migracion con el siguiente comndo**
```sh
docker compose run --rm alembic revision --autogenerate -m "agrega descuento a producto"
```

**Deberia verse en `./src/migrations/versions/`:**
```py
def upgrade():
    op.add_column('producto', sa.Column('descuento', sa.Numeric(5, 2), nullable=False, server_default='0'))

def downgrade():
    op.drop_column('producto', 'descuento')
```

**Subimos la migracion**
```sh
docker compose run --rm alembic upgrade head
```

**Actualizamos en `./src/schemas.py`**
```Python
class ProductoBase(BaseModel):
    nombre: str
    ganancia: Decimal
    es_relleno: bool = False
    descuento: Decimal = 0  # agregar esta linea
```

**Verificamos resultados en http://localhost:8000/docs donde el campo de descuendo ya aparece en los endpoints de Producto**

## Conclusión

Con este stack se obtiene una aplicación Python moderna, sin dependencias de Django:

- **SQLAlchemy** maneja el acceso a datos con total control sobre las queries
- **Alembic** gestiona las migraciones de forma versionada y con soporte para rollback
- **FastAPI** provee los endpoints REST con validación automática via Pydantic y documentación interactiva incluida
- **Docker Compose** orquesta todo en contenedores reproducibles

Los mismos datos de la Fábrica de Pastas (Tallarín, Ravioli Espinaca, Sorrentino Jamón y Queso con sus recetas e ingredientes) quedan disponibles vía API REST en `http://localhost:8000`.

---

## Referencias

- [Documentación SQLAlchemy](https://docs.sqlalchemy.org/)
- [Documentación Alembic](https://alembic.sqlalchemy.org/)
- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [FastAPI con SQLAlchemy — guía oficial](https://fastapi.tiangolo.com/tutorial/sql-databases/)
