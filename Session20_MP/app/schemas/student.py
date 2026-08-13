from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from schemas.classroom import ClassroomResponse


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class StudentCreate(BaseModel):
    student_code: str = Field(min_length=3, max_length=20)
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    age: Optional[int] = Field(None, ge=16, le=60)
    gender: Gender
    class_id: int = Field(ge=1)


class StudentUpdate(BaseModel):
    student_code: Optional[str] = Field(None, min_length=3, max_length=20)
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=16, le=60)
    gender: Optional[Gender] = None
    class_id: Optional[int] = Field(None, ge=1)


class StudentResponse(BaseModel):
    id: int
    student_code: str
    full_name: str
    email: str
    age: Optional[int] = None
    gender: Optional[Gender] = None
    classroom: Optional[ClassroomResponse] = None

    class Config:
        from_attributes = True


class StudentListResult(BaseModel):
    total: int
    items: List[StudentResponse]
