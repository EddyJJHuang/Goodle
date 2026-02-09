def success_response(data, message: str = "success"):
    return {"code": 200, "message": message, "data": data}
