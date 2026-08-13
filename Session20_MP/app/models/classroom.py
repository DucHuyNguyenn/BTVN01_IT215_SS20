from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    class_code = Column(String(50), unique=True, nullable=False, index=True)
    class_name = Column(String(100), nullable=False)
    max_students = Column(Integer, nullable=False, default=30)
    status = Column(String(20), nullable=False, default="active")

    # 1-N relationship with Student
    students = relationship("Student", back_populates="classroom")
