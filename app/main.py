from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import chat, adoption

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pet Match Platform API",
    description="宠物匹配平台 API",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router)
app.include_router(adoption.router)

@app.get("/")
def read_root():
    return {"message": "Pet Match Platform API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}