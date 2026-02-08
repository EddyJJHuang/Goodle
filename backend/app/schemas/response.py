from pydantic import BaseModel
from typing import TypeVar, Generic, Optional

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    code: int
    message: str
    data: Optional[T] = None

    @classmethod
    def success(cls, data: T, message: str = "success"):
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, code: int, message: str):
        return cls(code=code, message=message, data=None)
