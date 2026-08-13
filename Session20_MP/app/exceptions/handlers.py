from datetime import datetime, timezone
from typing import Optional, Any
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppException(Exception):
    def __init__(self, status_code: int, message: str, error_code: Optional[str] = None):
        self.status_code = status_code
        self.message = message
        self.error_code = error_code or f"ERR-{status_code}"


class NotFoundException(AppException):
    def __init__(self, message: str = "Không tìm thấy tài nguyên!", error_code: str = "ERR-NOT-FOUND"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, message=message, error_code=error_code)


class ConflictException(AppException):
    def __init__(self, message: str = "Dữ liệu bị xung đột!", error_code: str = "ERR-CONFLICT"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, message=message, error_code=error_code)


class BadRequestException(AppException):
    def __init__(self, message: str = "Yêu cầu không hợp lệ!", error_code: str = "ERR-BAD-REQUEST"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, message=message, error_code=error_code)


def create_error_response(status_code: int, message: str, error: Any, path: str):
    return JSONResponse(
        status_code=status_code,
        content={
            "statusCode": status_code,
            "message": message,
            "data": None,
            "error": error,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "path": path
        }
    )


async def app_exception_handler(request: Request, exc: AppException):
    return create_error_response(
        status_code=exc.status_code,
        message=exc.message,
        error=exc.error_code,
        path=request.url.path
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return create_error_response(
        status_code=exc.status_code,
        message=str(exc.detail),
        error=f"ERR-{exc.status_code}",
        path=request.url.path
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    formatted_errors = []
    for err in errors:
        loc = " -> ".join([str(l) for l in err.get("loc", []) if l != "body"])
        msg = err.get("msg")
        formatted_errors.append({"field": loc, "message": msg})

    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Dữ liệu đầu vào không hợp lệ!",
        error=formatted_errors,
        path=request.url.path
    )


async def global_exception_handler(request: Request, exc: Exception):
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Lỗi hệ thống xảy ra!",
        error="ERR-INTERNAL-SERVER",
        path=request.url.path
    )
