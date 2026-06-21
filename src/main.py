from fastapi import FastAPI
from routers import productos, clientes, ventas, ingredientes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Fábrica de Pastas API",
    description="Sistema de gestión para fábrica de pastas artesanales",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(productos.router)
app.include_router(clientes.router)
app.include_router(ventas.router)
app.include_router(ingredientes.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": "Fábrica de Pastas"}
