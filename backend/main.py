from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from typing import List, Annotated, Optional
from datetime import datetime
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from routers import auth, financial_resource, jobs, jobs, profile
from dotenv import load_dotenv
load_dotenv()

# Frontend dev origin for CORS
origins = [
    "http://localhost:4200"
]

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(financial_resource.router)
app.include_router(profile.router)
app.include_router(jobs.router)
app.include_router(profile.router)

def get_db():
    # Provide a DB session per request
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/")
def read_root():
    # Health endpoint to verify API is up
    return {"message": "Welcome to the HustleHub API"}
