"""地址逆解析：WGS84 坐标 → 地址（Geopy + Nominatim）"""
from typing import Optional

def reverse_geocode(lat: float, lng: float) -> Optional[str]:
    try:
        from geopy.geocoders import Nominatim
        from geopy.exc import GeocoderTimedOut, GeocoderServiceError
        g = Nominatim(user_agent="goodle-stray/1.0")
        loc = g.reverse(f"{lat}, {lng}", timeout=5)
        return loc.address if loc else None
    except Exception:
        return None
