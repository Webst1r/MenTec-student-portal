from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field


class Role(str, Enum):
    student = "student"
    lecturer = "lecturer"
    admin = "admin"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    full_name: str
    role: Role = Field(default=Role.student)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True)
    title: str
    description: str = ""
    lecturer_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Enrollment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="user.id", index=True)
    course_id: int = Field(foreign_key="course.id", index=True)
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)


class Grade(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="user.id", index=True)
    course_id: int = Field(foreign_key="course.id", index=True)
    assessment: str  # e.g. "Midterm", "Final"
    score: float
    max_score: float = 100.0
    graded_at: datetime = Field(default_factory=datetime.utcnow)


class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id", index=True)
    original_name: str
    stored_name: str  # filename on disk
    mime_type: str
    size_bytes: int
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    thread_id: str = Field(index=True)  # uuid string shared by a conversation
    sender_id: int = Field(foreign_key="user.id", index=True)
    recipient_id: int = Field(foreign_key="user.id", index=True)
    subject: str
    body: str
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    read: bool = False


class Announcement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    author_id: int = Field(foreign_key="user.id")
    title: str
    body: str
    posted_at: datetime = Field(default_factory=datetime.utcnow)


class CalendarEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id", index=True)
    title: str
    description: str = ""
    starts_at: datetime
    ends_at: datetime
