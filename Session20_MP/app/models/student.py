from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_code = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    class_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False)

    # 1-N relationship back to Classroom
    classroom = relationship("Classroom", back_populates="students")

    # N-N relationship with Course via Enrollment
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
