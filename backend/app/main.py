from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, SessionLocal
from . import models
from .routes import biens, contacts, estimation, auth as auth_routes, admin
from .seed import seed_data

models.Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    seed_data(db)
finally:
    db.close()

app = FastAPI(title="Ymmo API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(biens.router, prefix="/biens", tags=["biens"])
app.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
app.include_router(estimation.router, prefix="/estimation", tags=["estimation"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Ymmo"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
