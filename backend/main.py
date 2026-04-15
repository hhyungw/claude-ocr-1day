from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from backend.routers import expenses, upload  # noqa: E402 (load_dotenv 먼저 실행)

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

app.include_router(upload.router)
app.include_router(expenses.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
