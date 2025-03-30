from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Tutor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Tutor API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/courses", response_model=list[schemas.Course])
def get_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # This is a placeholder. You'll need to implement the actual database query
    return []

@app.post("/chat")
def chat(request: schemas.ChatRequest):
    # This is a placeholder. You'll need to implement the actual AI response
    return {
        "response": f"This is a placeholder response to: {request.message}",
        "audio_url": None
    }