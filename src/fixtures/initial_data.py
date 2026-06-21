import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import SessionLocal
from models import UnidadMedida, Ingrediente, Producto, Receta, Barrio, Localidad, Provincia


def load():
    db = SessionLocal()
    try:
        print("Cargando datos iniciales...")

        kilo = UnidadMedida(id=1, nombre="KILO")
        unidad = UnidadMedida(id=2, nombre="UNIDAD")
        db.add_all([kilo, unidad])
        db.flush()

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

        productos = [
            Producto(id=1, nombre="TALLARIN",                ganancia=2.00, es_relleno=False),
            Producto(id=2, nombre="RAVIOLI ESPINACA",        ganancia=3.00, es_relleno=True),
            Producto(id=3, nombre="SORRENTINO JAMÓN Y QUESO", ganancia=3.80, es_relleno=True),
        ]
        db.add_all(productos)
        db.flush()

        recetas = [
            Receta(cantidad=0.90, ingrediente_id=1, producto_id=1),
            Receta(cantidad=0.05, ingrediente_id=2, producto_id=1),
            Receta(cantidad=4.00, ingrediente_id=3, producto_id=1),
            Receta(cantidad=0.60, ingrediente_id=1, producto_id=2),
            Receta(cantidad=4.00, ingrediente_id=3, producto_id=2),
            Receta(cantidad=0.30, ingrediente_id=6, producto_id=2),
            Receta(cantidad=0.60, ingrediente_id=1, producto_id=3),
            Receta(cantidad=4.00, ingrediente_id=3, producto_id=3),
            Receta(cantidad=0.15, ingrediente_id=4, producto_id=3),
            Receta(cantidad=0.15, ingrediente_id=5, producto_id=3),
        ]
        db.add_all(recetas)

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
