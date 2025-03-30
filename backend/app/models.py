from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Float, DateTime
from sqlalchemy.orm import relationship
import datetime

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    progress = relationship("LearningProgress", back_populates="user")
    
class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    first_name = Column(String)
    last_name = Column(String)
    learning_style = Column(String)
    experience_level = Column(String)
    goals = Column(Text)
    
    user = relationship("User", back_populates="profile")

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    difficulty_level = Column(String)
    prerequisites = Column(Text)
    
    modules = relationship("Module", back_populates="course")

class Module(Base):
    __tablename__ = "modules"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String)
    description = Column(Text)
    order = Column(Integer)
    
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module")

class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"))
    title = Column(String)
    content = Column(Text)
    order = Column(Integer)
    
    module = relationship("Module", back_populates="lessons")
    progress = relationship("LearningProgress", back_populates="lesson")

class LearningProgress(Base):
    __tablename__ = "learning_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    completion_percentage = Column(Float, default=0.0)
    last_accessed = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="progress")
    lesson = relationship("Lesson", back_populates="progress")