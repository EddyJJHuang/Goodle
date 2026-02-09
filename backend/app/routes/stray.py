"""流浪狗上报：POST /api/stray-report，照片存 uploads/stray/，坐标逆解析为地址"""
import uuid
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form
from app.schemas import success_response
from app.config import UPLOAD_STRAY
from app.services.geolocation import reverse_geocode

router = APIRouter(prefix="/stray-report", tags=["stray"])

_store: list[dict] = []


@router.post("", status_code=201)
async def create_stray_report(
    description: str = Form(""),
    lat: str = Form(""),
    lng: str = Form(""),
    report_time: str = Form(""),
    photo: UploadFile | None = File(None),
):
    """创建流浪狗上报。字段：照片、文字描述、GPS 坐标、上报时间；地址由坐标逆解析。"""
    photo_path: str | None = None
    if photo and photo.filename and photo.content_type and photo.content_type.startswith("image/"):
        ext = Path(photo.filename).suffix or ".jpg"
        name_file = f"{uuid.uuid4().hex}{ext}"
        path = UPLOAD_STRAY / name_file
        content = await photo.read()
        path.write_bytes(content)
        photo_path = f"/uploads/stray/{name_file}"

    lat_f = float(lat) if lat else None
    lng_f = float(lng) if lng else None
    address: str | None = None
    if lat_f is not None and lng_f is not None:
        address = reverse_geocode(lat_f, lng_f)

    try:
        report_dt = datetime.fromisoformat(report_time.replace("Z", "+00:00")) if report_time else datetime.utcnow()
    except Exception:
        report_dt = datetime.utcnow()

    record = {
        "id": str(len(_store) + 1),
        "description": description or "",
        "lat": lat_f,
        "lng": lng_f,
        "address": address or "",
        "report_time": report_dt.isoformat(),
        "photo_path": photo_path,
    }
    _store.append(record)
    return success_response(record, message="success")


@router.get("")
def list_stray_reports():
    """上报列表（供地图等使用）。"""
    return success_response(list(reversed(_store)))
