from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from backend.routers import expenses, upload  # noqa: E402 (load_dotenv 먼저 실행)

UPLOADS_DIR = Path(__file__).parent / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="영수증 지출관리 API",
    description="영수증 OCR 기반 지출 관리 서비스 (Upstage Vision LLM)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 업로드된 영수증 이미지 정적 서빙 (/uploads/{filename})
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

app.include_router(upload.router)
app.include_router(expenses.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
