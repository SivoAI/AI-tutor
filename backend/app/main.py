# main.py
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from . import models, schemas, auth
from .database import engine, get_db
from .utils import hash_password, verify_password

router = APIRouter()

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, user.hashed_password): # Fixed auth.verify_password to verify_password
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    return current_user



app = FastAPI(title="AI Tutor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router) #Include the router

models.Base.metadata.create_all(bind=engine) #Moved to here



@app.get("/")
def read_root():
    return {"message": "Welcome to AI Tutor API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = hash_password(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/courses", response_model=List[schemas.Course])
def get_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    courses = db.query(models.Course).offset(skip).limit(limit).all()
    return courses


@app.post("/chat")
def chat(request: schemas.ChatRequest):
    # This is a placeholder. You'll need to implement the actual AI response
    return {
        "response": f"This is a placeholder response to: {request.message}",
        "audio_url": None
    }

@app.post("/user_profiles/", response_model=schemas.UserProfile, status_code=status.HTTP_201_CREATED)
def create_user_profile(user_profile: schemas.UserProfileCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_profile.user_id).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")
    
    db_user_profile = models.UserProfile(**user_profile.dict())
    db.add(db_user_profile)
    db.commit()
    db.refresh(db_user_profile)
    return db_user_profile

@app.post("/courses/", response_model=schemas.Course, status_code=status.HTTP_201_CREATED)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    db_course = models.Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@app.post("/courses", response_model=schemas.Course, status_code=status.HTTP_201_CREATED)
def create_course_no_slash(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    db_course = models.Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@app.post("/modules/", response_model=schemas.Module, status_code=status.HTTP_201_CREATED)
def create_module(module: schemas.ModuleCreate, db: Session = Depends(get_db)):
    db_course = db.query(models.Course).filter(models.Course.id == module.course_id).first()
    if not db_course:
        raise HTTPException(status_code=400, detail="Course not found")
    db_module = models.Module(**module.dict())
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    return db_module

@app.post("/lessons/", response_model=schemas.Lesson, status_code=status.HTTP_201_CREATED)
def create_lesson(lesson: schemas.LessonCreate, db: Session = Depends(get_db)):
    db_module = db.query(models.Module).filter(models.Module.id == lesson.module_id).first()
    if not db_module:
        raise HTTPException(status_code=400, detail="Module not found")
    db_lesson = models.Lesson(**lesson.dict())
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson