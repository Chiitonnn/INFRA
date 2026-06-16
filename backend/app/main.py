from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import httpx
import os

from .database import engine, get_db
from . import models, schemas, auth
from .routes import biens, estimation, auth as auth_routes

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ymmo API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(biens.router, prefix="/biens", tags=["biens"])
app.include_router(estimation.router, prefix="/estimation", tags=["estimation"])

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Ymmo"}

@app.get("/health")
def health_check():
    return {"status": "ok"}