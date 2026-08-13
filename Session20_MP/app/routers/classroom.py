from typing import List, Optional, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from database import get_db
from models.classroom import Classroom
from schemas.classroom import ClassroomCreate, ClassroomResponse
from schemas.response import StandardResponse
from exceptions.handlers import ConflictException, NotFoundException

router = APIRouter(prefix="/classrooms", tags=["Classroom Management"])

def build_response(status_code: int, message: str, data: Any, request: Request, error: Any = None):
    return {
        "statusCode": status_code,
        "message": message,
        "data": data,
        "error": error,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "path": request.url.path
    }


@router.get("", response_model=StandardResponse[List[ClassroomResponse]], status_code=status.HTTP_200_OK)
def get_classrooms(
    request: Request,
    db: Session = Depends(get_db)
):
    classrooms = db.query(Classroom).order_by(Classroom.id.asc()).all()
    serialized = [ClassroomResponse.model_validate(c) for c in classrooms]
    return build_response(
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách lớp học thành công!",
        data=serialized,
        request=request
    )

@router.post("", response_model=StandardResponse[ClassroomResponse], status_code=status.HTTP_201_CREATED)
def create_classroom(
    payload: ClassroomCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    existing = db.query(Classroom).filter(Classroom.class_code == payload.class_code).first()
    if existing:
        raise ConflictException(message="Mã lớp học đã tồn tại!", error_code="ERR-CLASS-CODE-DUPLICATE")

    new_classroom = Classroom(
        class_code=payload.class_code,
        class_name=payload.class_name,
        max_students=payload.max_students,
        status=payload.status
    )
    db.add(new_classroom)
    db.commit()
    db.refresh(new_classroom)

    serialized = ClassroomResponse.model_validate(new_classroom)
    return build_response(
        status_code=status.HTTP_201_CREATED,
        message="Thêm mới lớp học thành công!",
        data=serialized,
        request=request
    )
