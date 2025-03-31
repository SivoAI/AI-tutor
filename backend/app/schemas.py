# schemas.py
import enum
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

class UserProfileBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    learning_style: Optional[str] = None
    experience_level: Optional[str] = None
    goals: Optional[str] = None

class UserProfileCreate(UserProfileBase):
    user_id: int

class UserProfile(UserProfileBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class CourseBase(BaseModel):
    title: str
    description: str
    difficulty_level: str
    prerequisites: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    id: int

    class Config:
        orm_mode = True

class ModuleBase(BaseModel):
    title: str
    description: str
    order: int

class ModuleCreate(ModuleBase):
    course_id: int

class Module(ModuleBase):
    id: int
    course_id: int

    class Config:
        orm_mode = True

class LessonBase(BaseModel):
    title: str
    content: str
    order: int

class LessonCreate(LessonBase):
    module_id: int

class Lesson(LessonBase):
    id: int
    module_id: int

    class Config:
        orm_mode = True

class ChatRequest(BaseModel):
    message: str
    lesson_id: Optional[int] = None

class LearningStyle(str, enum.Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"

class ExperienceLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    learning_style: Optional[LearningStyle] = None
    experience_level: Optional[ExperienceLevel] = None
    goals: Optional[str] = None        