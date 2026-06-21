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
