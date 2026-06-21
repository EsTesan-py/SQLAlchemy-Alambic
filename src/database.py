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