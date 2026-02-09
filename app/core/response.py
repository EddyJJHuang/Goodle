from __future__ import annotations

from typing import Any


def api_success(data: Any, message: str = "success", code: int = 200) -> dict[str, Any]:
    return {"code": code, "message": message, "data": data}


def api_error(message: str, code: int, data: Any = None) -> dict[str, Any]:
    return {"code": code, "message": message, "data": data}
