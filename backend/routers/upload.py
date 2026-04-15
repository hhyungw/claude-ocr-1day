"""POST /api/upload — 영수증 업로드 및 OCR 파싱"""

import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.services import expense_store, ocr_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["upload"])

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "application/pdf"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

UPLOADS_DIR = Path(__file__).parent.parent / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_receipt(file: UploadFile = File(...)):
    """영수증 파일 업로드 → OCR 파싱 → expenses.json 저장 → 파싱 결과 반환"""

    # 확장자 검증
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다. (지원: JPG, PNG, PDF)",
        )

    # MIME 타입 검증
    content_type = file.content_type or ""
    if content_type not in ALLOWED_MIME_TYPES:
        # 확장자로 MIME 타입 보정
        ext_to_mime = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".pdf": "application/pdf",
        }
        content_type = ext_to_mime.get(ext, content_type)

    # 파일 크기 검증
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="파일 크기가 10MB를 초과합니다.",
        )
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="빈 파일입니다.")

    # 업로드 파일 저장
    expense_id = str(uuid.uuid4())
    saved_filename = f"{expense_id}{ext}"
    saved_path = UPLOADS_DIR / saved_filename
    saved_path.write_bytes(file_bytes)
    logger.info("파일 저장: %s (%d bytes)", saved_path, len(file_bytes))

    # OCR 파싱
    try:
        parsed = ocr_service.parse_receipt(file_bytes, file.filename or saved_filename, content_type)
    except Exception as e:
        logger.error("OCR 파싱 실패: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"OCR 파싱에 실패했습니다. 다시 시도해 주세요. ({e})",
        )

    # 저장용 expense 객체 구성
    expense = {
        "id": expense_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "store_name": parsed.get("store_name"),
        "receipt_date": parsed.get("receipt_date"),
        "receipt_time": parsed.get("receipt_time"),
        "category": parsed.get("category", "기타"),
        "items": parsed.get("items", []),
        "subtotal": parsed.get("subtotal", 0),
        "discount": parsed.get("discount", 0),
        "tax": parsed.get("tax", 0),
        "total_amount": parsed.get("total_amount", 0),
        "payment_method": parsed.get("payment_method"),
        "raw_image_path": f"uploads/{saved_filename}",
    }

    expense_store.append(expense)
    logger.info("지출 저장 완료: id=%s store=%s total=%s", expense_id, expense["store_name"], expense["total_amount"])

    return expense
