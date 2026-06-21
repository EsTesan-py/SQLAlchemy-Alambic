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
    venta = Venta(fecha=data.fecha, cliente_id=data.cliente_id)
    db.add(venta)
    db.flush()

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
