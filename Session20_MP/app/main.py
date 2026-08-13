from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from database import engine, Base, SessionLocal
from routers import student_router, classroom_router
from exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler
)
from utils import seed_initial_data

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Management API",
    version="1.0.0",
    description="Hệ thống RESTful API Quản lý sinh viên theo lớp học - Mini Project"
)

# Register Exception Handlers to guarantee standard 6-field JSON error responses
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Register API Routers
app.include_router(student_router)
app.include_router(classroom_router)


@app.on_event("startup")
def startup_event():
    # Seed initial data for testing and demonstration
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()


@app.get("/", tags=["Health Check"])
def root():
    return {
        "statusCode": 200,
        "message": "Student Management API is running stably!",
        "data": {
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "error": None
    }
