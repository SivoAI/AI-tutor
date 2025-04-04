import enum
from sqlalchemy import Enum, Boolean, Column, ForeignKey, Integer, String, Text, Float, DateTime
from sqlalchemy.orm import relationship
import datetime

from .database import Base

class User(Base):
    """Represents a user in the system."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    """The unique ID of the user."""
    email = Column(String, unique=True, index=True)
    """The email address of the user."""
    hashed_password = Column(String)
    """The hashed password of the user."""
    is_active = Column(Boolean, default=True)
    """Whether the user is active."""
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    """The date and time when the user was created."""

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    progress = relationship("LearningProgress", back_populates="user")


class Course(Base):
    """Represents a course in the system."""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    """The unique ID of the course."""
    title = Column(String, index=True)
    """The title of the course."""
    description = Column(Text)
    """A description of the course."""
    difficulty_level = Column(String)
    """The difficulty level of the course (e.g., Beginner, Intermediate, Advanced)."""
    prerequisites = Column(Text)
    """The prerequisites for the course."""

    modules = relationship("Module", back_populates="course")


class Module(Base):
    """Represents a module within a course."""
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    """The unique ID of the module."""
    course_id = Column(Integer, ForeignKey("courses.id"))
    """The ID of the course to which the module belongs."""
    title = Column(String)
    """The title of the module."""
    description = Column(Text)
    """A description of the module."""
    order = Column(Integer)
    """The order of the module within the course."""

    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module")


class Lesson(Base):
    """Represents a lesson within a module."""
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    """The unique ID of the lesson."""
    module_id = Column(Integer, ForeignKey("modules.id"))
    """The ID of the module to which the lesson belongs."""
    title = Column(String)
    """The title of the lesson."""
    content = Column(Text)
    """The content of the lesson."""
    order = Column(Integer)
    """The order of the lesson within the module."""

    module = relationship("Module", back_populates="lessons")
    progress = relationship("LearningProgress", back_populates="lesson")


class LearningProgress(Base):
    """Represents a user's progress on a lesson."""
    __tablename__ = "learning_progress"

    id = Column(Integer, primary_key=True, index=True)
    """The unique ID of the learning progress entry."""
    user_id = Column(Integer, ForeignKey("users.id"))
    """The ID of the user."""
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    """The ID of the lesson."""
    completion_percentage = Column(Float, default=0.0)
    """The percentage of the lesson that the user has completed."""
    last_accessed = Column(DateTime, default=datetime.datetime.utcnow)
    """The date and time when the lesson was last accessed by the user."""

    user = relationship("User", back_populates="progress")
    lesson = relationship("Lesson", back_populates="progress")


class LearningStyleEnum(enum.Enum):
    """Represents the user's learning style."""
    VISUAL = "Visual"
    """Visual learning style."""
    AUDITORY = "Auditory"
    """Auditory learning style."""
    KINESTHETIC = "Kinesthetic"
    """Kinesthetic learning style."""


class ExperienceLevelEnum(enum.Enum):
    """Represents the user's experience level."""
    BEGINNER = "Beginner"
    """Beginner experience level."""
    INTERMEDIATE = "Intermediate"
    """Intermediate experience level."""
    ADVANCED = "Advanced"
    """Advanced experience level."""


class UserProfile(Base):
    """Represents a user's profile."""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    """The unique ID of the user profile."""
    user_id = Column(Integer, ForeignKey("users.id"))
    """The ID of the user to whom the profile belongs."""
    first_name = Column(String)
    """The first name of the user."""
    last_name = Column(String)
    """The last name of the user."""
    learning_style = Column(Enum(LearningStyleEnum), default=LearningStyleEnum.VISUAL)
    """The user's preferred learning style."""
    experience_level = Column(Enum(ExperienceLevelEnum), default=ExperienceLevelEnum.BEGINNER)
    """The user's experience level."""
    goals = Column(Text)
    """The user's learning goals."""

    user = relationship("User", back_populates="profile")