from sqlalchemy.orm import Session
from models.classroom import Classroom
from models.student import Student
from models.user import User, UserProfile
from models.course import Course, Enrollment

def seed_initial_data(db: Session):
    # 1. Seed Classrooms
    if db.query(Classroom).count() == 0:
        c1 = Classroom(id=1, class_code="CNTT01", class_name="Công nghệ thông tin 01", max_students=2, status="active")
        c2 = Classroom(id=2, class_code="CNTT02", class_name="Công nghệ thông tin 02", max_students=50, status="active")
        c3 = Classroom(id=3, class_code="CNTT03", class_name="Công nghệ thông tin 03", max_students=30, status="inactive")
        db.add_all([c1, c2, c3])
        db.commit()

    # 2. Seed Students
    if db.query(Student).count() == 0:
        s1 = Student(
            id=1,
            student_code="SV001",
            full_name="Nguyễn Văn An",
            email="an@example.com",
            age=20,
            gender="male",
            class_id=1
        )
        db.add(s1)
        db.commit()

    # 3. Seed Users & UserProfiles (1-1 relationship example)
    if db.query(User).count() == 0:
        u1 = User(id=1, username="admin", password="password123")
        db.add(u1)
        db.commit()

        p1 = UserProfile(id=1, full_name="Quản trị viên", address="Hà Nội", user_id=u1.id)
        db.add(p1)
        db.commit()

    # 4. Seed Courses & Enrollments (N-N relationship example)
    if db.query(Course).count() == 0:
        crs1 = Course(id=1, course_code="PY101", course_name="Lập trình Python cơ bản")
        crs2 = Course(id=2, course_code="WEB201", course_name="Phát triển Web với FastAPI")
        db.add_all([crs1, crs2])
        db.commit()

        if db.query(Enrollment).count() == 0:
            enr1 = Enrollment(student_id=1, course_id=1, status="enrolled", final_score=9.0)
            enr2 = Enrollment(student_id=1, course_id=2, status="enrolled", final_score=8.5)
            db.add_all([enr1, enr2])
            db.commit()
