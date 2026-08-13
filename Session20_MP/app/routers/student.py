from typing import Optional, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from database import get_db
from models.student import Student
from models.classroom import Classroom
from schemas.student import StudentCreate, StudentUpdate, StudentResponse, StudentListResult
from schemas.response import StandardResponse
from exceptions.handlers import NotFoundException, ConflictException

router = APIRouter(prefix="/students", tags=["Student Management"])


def build_response(status_code: int, message: str, data: Any, request: Request, error: Any = None):
    return {
        "statusCode": status_code,
        "message": message,
        "data": data,
        "error": error,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "path": request.url.path
    }



@router.get("", response_model=StandardResponse[StudentListResult], status_code=status.HTTP_200_OK)
def get_students(
    request: Request,
    keyword: Optional[str] = Query(None),
    class_id: Optional[int] = Query(None, ge=1),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Student).options(joinedload(Student.classroom))

    if keyword and keyword.strip():
        search_pattern = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                Student.full_name.ilike(search_pattern),
                Student.student_code.ilike(search_pattern),
                Student.email.ilike(search_pattern)
            )
        )

    if class_id is not None:
        query = query.filter(Student.class_id == class_id)

    total = query.count()
    items = query.order_by(Student.id.asc()).offset((page - 1) * limit).limit(limit).all()
    serialized_items = [StudentResponse.model_validate(item) for item in items]

    data = {
        "total": total,
        "items": serialized_items
    }

    return build_response(
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách sinh viên thành công!",
        data=data,
        request=request
    )


@router.get("/{student_id}", response_model=StandardResponse[StudentResponse], status_code=status.HTTP_200_OK)
def get_student_detail(
    student_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    student = db.query(Student).options(joinedload(Student.classroom)).filter(Student.id == student_id).first()

    if not student:
        raise NotFoundException(message="Không tìm thấy sinh viên!", error_code="ERR-STUDENT-01")

    serialized_student = StudentResponse.model_validate(student)

    return build_response(
        status_code=status.HTTP_200_OK,
        message="Lấy chi tiết sinh viên thành công!",
        data=serialized_student,
        request=request
    )


@router.post("", response_model=StandardResponse[StudentResponse], status_code=status.HTTP_201_CREATED)
def create_student(
    payload: StudentCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    classroom = db.query(Classroom).filter(Classroom.id == payload.class_id).first()
    if not classroom:
        raise NotFoundException(message="Không tìm thấy lớp học!", error_code="ERR-CLASS-01")

    if classroom.status != "active":
        raise ConflictException(message="Lớp học không ở trạng thái hoạt động!", error_code="ERR-CLASS-INACTIVE")

    current_students_count = db.query(Student).filter(Student.class_id == payload.class_id).count()
    if current_students_count >= classroom.max_students:
        raise ConflictException(message="Lớp học đã đầy!", error_code="ERR-CLASS-FULL")

    existing_code = db.query(Student).filter(Student.student_code == payload.student_code).first()
    if existing_code:
        raise ConflictException(message="Mã sinh viên đã tồn tại!", error_code="ERR-STUDENT-CODE-DUPLICATE")

    existing_email = db.query(Student).filter(Student.email == payload.email).first()
    if existing_email:
        raise ConflictException(message="Email đã tồn tại!", error_code="ERR-STUDENT-EMAIL-DUPLICATE")

    new_student = Student(
        student_code=payload.student_code,
        full_name=payload.full_name,
        email=payload.email,
        age=payload.age,
        gender=payload.gender.value if hasattr(payload.gender, "value") else payload.gender,
        class_id=payload.class_id
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    created_student = db.query(Student).options(joinedload(Student.classroom)).filter(Student.id == new_student.id).first()
    serialized_student = StudentResponse.model_validate(created_student)

    return build_response(
        status_code=status.HTTP_201_CREATED,
        message="Thêm mới sinh viên thành công!",
        data=serialized_student,
        request=request
    )


@router.put("/{student_id}", response_model=StandardResponse[StudentResponse], status_code=status.HTTP_200_OK)
def update_student(
    student_id: int,
    payload: StudentUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise NotFoundException(message="Không tìm thấy sinh viên!", error_code="ERR-STUDENT-01")

    # Lấy dictionary chứa các trường thực sự được truyền trong request
    update_data = payload.model_dump(exclude_unset=True)

    # 1. Kiểm tra trùng mã sinh viên nếu có cập nhật student_code
    if "student_code" in update_data and update_data["student_code"] != student.student_code:
        dup_code = db.query(Student).filter(
            Student.student_code == update_data["student_code"],
            Student.id != student_id
        ).first()
        if dup_code:
            raise ConflictException(message="Mã sinh viên đã tồn tại!", error_code="ERR-STUDENT-CODE-DUPLICATE")

    # 2. Kiểm tra trùng email nếu có cập nhật email
    if "email" in update_data and update_data["email"] != student.email:
        dup_email = db.query(Student).filter(
            Student.email == update_data["email"],
            Student.id != student_id
        ).first()
        if dup_email:
            raise ConflictException(message="Email đã tồn tại!", error_code="ERR-STUDENT-EMAIL-DUPLICATE")

    # 3. Kiểm tra lớp học nếu có cập nhật/chuyển class_id
    if "class_id" in update_data:
        new_class_id = update_data["class_id"]
        target_class = db.query(Classroom).filter(Classroom.id == new_class_id).first()
        if not target_class:
            raise NotFoundException(message="Không tìm thấy lớp học!", error_code="ERR-CLASS-01")

        if target_class.status != "active":
            raise ConflictException(message="Lớp học không ở trạng thái hoạt động!", error_code="ERR-CLASS-INACTIVE")

        if new_class_id != student.class_id:
            current_count = db.query(Student).filter(Student.class_id == new_class_id).count()
            if current_count >= target_class.max_students:
                raise ConflictException(message="Lớp học đã đầy!", error_code="ERR-CLASS-FULL")

    # 4. Gán tự động tất cả các trường được gửi lên vào model ORM
    for key, value in update_data.items():
        setattr(student, key, value)

    db.commit()
    db.refresh(student)

    updated_student = db.query(Student).options(joinedload(Student.classroom)).filter(Student.id == student_id).first()
    serialized_student = StudentResponse.model_validate(updated_student)

    return build_response(
        status_code=status.HTTP_200_OK,
        message="Cập nhật sinh viên thành công!",
        data=serialized_student,
        request=request
    )

