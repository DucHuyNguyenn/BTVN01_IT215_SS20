from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")


class StandardResponse(BaseModel, Generic[T]):
    statusCode: int
    message: str
    data: Optional[T] = None
    error: Optional[Any] = None
    timestamp: str
    path: str
