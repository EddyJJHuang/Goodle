"""寻狗发布功能：POST /api/lost-dog，状态 待寻找/已找到"""
import uuid
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form
from app.schemas import success_response
from app.config import UPLOAD_LOST

router = APIRouter(prefix="/lost-dog", tags=["lost"])

_store: list[dict] = []


@router.post("", status_code=201)
async def create_lost_dog(
    breed: str = Form(""),
    description: str = Form(""),
    lost_time: str = Form(""),
    lat: str = Form(""),
    lng: str = Form(""),
    address: str = Form(""),
    contact: str = Form(""),
    photo: UploadFile | None = File(None),
):
    """创建寻狗启事。字段：狗狗照片、品种、特征描述、走失时间、走失地点(GPS+地址)、联系方式。状态默认待寻找。"""
    photo_path: str | None = None
    if photo and photo.filename and photo.content_type and photo.content_type.startswith("image/"):
        ext = Path(photo.filename).suffix or ".jpg"
        name_file = f"{uuid.uuid4().hex}{ext}"
        path = UPLOAD_LOST / name_file
        content = await photo.read()
        path.write_bytes(content)
        photo_path = f"/uploads/lost/{name_file}"

    try:
        lost_dt = datetime.fromisoformat(lost_time.replace("Z", "+00:00")) if lost_time else datetime.utcnow()
    except Exception:
        lost_dt = datetime.utcnow()

    record = {
        "id": str(len(_store) + 1),
        "breed": breed or "未知",
        "description": description or "",
        "lost_time": lost_dt.isoformat(),
        "lat": float(lat) if lat else None,
        "lng": float(lng) if lng else None,
        "address": address or "",
        "contact": contact or "",
        "photo_path": photo_path,
        "status": "pending",  # 待寻找
    }
    _store.append(record)
    return success_response(record, message="success")


@router.get("")
def list_lost_dogs():
    """寻狗列表（供地图等使用）。"""
    return success_response(list(reversed(_store)))


@router.patch("/{dog_id}/status")
def update_lost_dog_status(dog_id: str, status: str):
    """更新状态：pending 待寻找 / found 已找到。"""
    if status not in ("pending", "found"):
        return success_response(None, message="invalid status")
    for r in _store:
        if str(r.get("id")) == str(dog_id):
            r["status"] = status
            return success_response(r, message="success")
    return success_response(None, message="not found")
