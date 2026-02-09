"""领养发帖：POST /pets（创建）、GET /pets（列表）"""
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form
from app.schemas import success_response
from app.config import UPLOAD_PETS

router = APIRouter(prefix="/pets", tags=["pets"])

# 内存存储（可后续改为数据库）
_store: list[dict] = []


@router.post("", status_code=201)
async def create_pet(
    name: str = Form(""),
    breed: str = Form(""),
    age: str = Form(""),
    description: str = Form(""),
    tags: str = Form(""),  # 逗号分隔
    photo: UploadFile | None = File(None),
):
    """创建领养帖。"""
    image_path: str | None = None
    if photo and photo.filename:
        ext = Path(photo.filename).suffix or ".jpg"
        name_file = f"{uuid.uuid4().hex}{ext}"
        path = UPLOAD_PETS / name_file
        content = await photo.read()
        path.write_bytes(content)
        image_path = f"/uploads/pets/{name_file}"

    tags_list = [t.strip() for t in tags.split(",") if t.strip()]
    pet = {
        "id": str(len(_store) + 1),
        "name": name or "Unnamed",
        "breed": breed or "Unknown",
        "age": age or "",
        "description": description or "",
        "tags": tags_list,
        "image": image_path or "",
        "images": [image_path] if image_path else [],
        "status": "Available",
        "gender": "Male",
        "distance": "",
        "location": "",
    }
    _store.append(pet)
    return success_response(pet, message="success")


@router.get("")
def list_pets(page: int = 1, limit: int = 10, status: str | None = None):
    """领养列表，分页，新帖在前。"""
    items = list(_store)
    if status:
        items = [p for p in items if p.get("status") == status]
    items.reverse()
    total = len(items)
    start = (page - 1) * limit
    page_items = items[start : start + limit]
    return success_response({
        "items": page_items,
        "total": total,
        "page": page,
        "pageSize": limit,
        "totalPages": (total + limit - 1) // limit if limit else 0,
    })
