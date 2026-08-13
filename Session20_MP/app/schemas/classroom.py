from typing import Optional
from pydantic import BaseModel, Field


class ClassroomCreate(BaseModel):
    class_code: str = Field(min_length=2, max_length=50)
    class_name: str = Field(min_length=2, max_length=100)
    max_students: int = Field(30, ge=1)
    status: str = "active"


class ClassroomResponse(BaseModel):
    id: int
    class_code: str
    class_name: str
    max_students: Optional[int] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True
