"""加载 .env 后启动后端（使 GEMINI_API_KEY 生效）。运行：python run.py 或 python -m run"""
import os
from pathlib import Path

# 在导入 app 前加载 backend/.env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(env_path)
except ImportError:
    pass

# 启动 uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=3000, reload=True)
