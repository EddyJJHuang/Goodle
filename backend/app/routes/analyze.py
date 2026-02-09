"""宠物照片 AI 分析：Gemini 识别品种、颜色"""
import os
import base64
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas import success_response

router = APIRouter(prefix="/analyze-pet-photo", tags=["analyze"])


def _analyze_image(image_bytes: bytes, mime_type: str) -> dict:
    import google.generativeai as genai
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set")
    genai.configure(api_key=api_key)
    # 使用当前 API 支持的模型（gemini-1.5-flash 在 v1beta 已不可用）
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = """Look at this pet photo. Identify the dog or pet breed and main color. Respond with ONLY these lines:
BREED: <breed name in English>
COLOR: <main color in English>
TAGS: <3 short comma-separated traits>

Example:
BREED: Poodle
COLOR: White
TAGS: Curly, Smart, Medium
"""
    image_part = {
        "inline_data": {
            "mime_type": mime_type,
            "data": base64.b64encode(image_bytes).decode("utf-8"),
        }
    }
    response = model.generate_content([image_part, prompt])
    text = (response.text or "").strip()
    breed, color, tags = "Unknown", "Unknown", []
    for line in text.split("\n"):
        line = line.strip()
        if line.upper().startswith("BREED:"):
            breed = line.split(":", 1)[1].strip()
        elif line.upper().startswith("COLOR:"):
            color = line.split(":", 1)[1].strip()
        elif line.upper().startswith("TAGS:"):
            raw = line.split(":", 1)[1].strip()
            tags = [t.strip() for t in raw.split(",") if t.strip()][:3]
    return {"breed": breed, "color": color, "tags": tags}


@router.post("", status_code=200)
async def analyze_pet_photo(photo: UploadFile = File(...)):
    """上传宠物照片，返回 AI 识别的品种、颜色、标签。"""
    if not photo.content_type or not photo.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    content = await photo.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large (max 10MB)")
    mime = photo.content_type or "image/jpeg"
    try:
        result = _analyze_image(content, mime)
        return success_response(result)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
