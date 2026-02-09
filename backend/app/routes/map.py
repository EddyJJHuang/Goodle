"""地图数据接口：GET /api/map/stray、GET /api/map/lost，支持范围查询与最近 N 天过滤"""
import math
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Query
from app.schemas import success_response

# 使用 stray / lost 模块内的存储，避免重复
from app.routes.stray import _store as stray_store
from app.routes.lost import _store as lost_store

router = APIRouter(prefix="/map", tags=["map"])


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """计算两点间距离（米）。"""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def _to_naive_utc(dt: datetime) -> datetime:
    if dt.tzinfo:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def _parse_time(iso: str | None) -> datetime | None:
    if not iso:
        return None
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return _to_naive_utc(dt) if dt.tzinfo else dt
    except Exception:
        return None


def _filter_stray(
    items: list[dict],
    center_lat: float | None,
    center_lng: float | None,
    radius_m: float | None,
    days: int | None,
) -> list[dict]:
    out = list(reversed(items))
    now = datetime.utcnow()
    if days is not None and days > 0:
        since = now - timedelta(days=days)
        out = [
            r for r in out
            if _parse_time(r.get("report_time")) and _parse_time(r["report_time"]) >= since
        ]
    if center_lat is not None and center_lng is not None and radius_m is not None and radius_m > 0:
        lat = center_lat
        lng = center_lng
        out = [
            r for r in out
            if r.get("lat") is not None and r.get("lng") is not None
            and haversine_meters(lat, lng, float(r["lat"]), float(r["lng"])) <= radius_m
        ]
    return out


def _filter_lost(
    items: list[dict],
    center_lat: float | None,
    center_lng: float | None,
    radius_m: float | None,
    days: int | None,
) -> list[dict]:
    out = [r for r in reversed(items) if r.get("status") != "found"]
    now = datetime.utcnow()
    if days is not None and days > 0:
        since = now - timedelta(days=days)
        out = [
            r for r in out
            if _parse_time(r.get("lost_time")) and _parse_time(r["lost_time"]) >= since
        ]
    if center_lat is not None and center_lng is not None and radius_m is not None and radius_m > 0:
        lat = center_lat
        lng = center_lng
        out = [
            r for r in out
            if r.get("lat") is not None and r.get("lng") is not None
            and haversine_meters(lat, lng, float(r["lat"]), float(r["lng"])) <= radius_m
        ]
    return out


@router.get("/stray")
def get_map_stray(
    lat: float | None = Query(None, description="中心点纬度"),
    lng: float | None = Query(None, description="中心点经度"),
    radius: float | None = Query(None, description="半径（米）"),
    days: int | None = Query(None, description="最近 N 天的上报数据"),
):
    """获取流浪狗地图标记点列表。支持根据中心点坐标和半径返回附近数据，支持查询最近 N 天的上报数据。"""
    result = _filter_stray(stray_store, lat, lng, radius, days)
    return success_response(result)


@router.get("/lost")
def get_map_lost(
    lat: float | None = Query(None, description="中心点纬度"),
    lng: float | None = Query(None, description="中心点经度"),
    radius: float | None = Query(None, description="半径（米）"),
    days: int | None = Query(None, description="最近 N 天的数据"),
):
    """获取寻狗地图标记点列表。支持根据中心点坐标和半径返回附近数据，支持查询最近 N 天的数据。"""
    result = _filter_lost(lost_store, lat, lng, radius, days)
    return success_response(result)
