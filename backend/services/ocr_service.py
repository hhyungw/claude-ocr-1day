"""OCR 서비스: UpstageDocumentParseLoader + ChatUpstage(Solar) 기반 영수증 파싱"""

import json
import logging
import os
import re
import tempfile
from pathlib import Path
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_upstage import ChatUpstage, UpstageDocumentParseLoader

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """당신은 영수증 OCR 데이터에서 구조화된 JSON을 추출하는 전문가입니다.
아래 영수증 텍스트를 분석하여 반드시 아래 JSON 형식으로만 응답하세요. 설명이나 마크다운 코드블록 없이 순수 JSON만 반환하세요.

{
  "store_name": "가게 이름 (없으면 null)",
  "receipt_date": "YYYY-MM-DD (없으면 null)",
  "receipt_time": "HH:MM (없으면 null)",
  "category": "식료품|외식|카페|교통|쇼핑|의료|엔터테인먼트|기타 중 하나",
  "items": [
    {"name": "품목명", "quantity": 1, "unit_price": 0, "total_price": 0}
  ],
  "subtotal": 0,
  "discount": 0,
  "tax": 0,
  "total_amount": 0,
  "payment_method": "신용카드|현금|체크카드|기타 중 하나 (없으면 null)"
}

규칙:
- 숫자 필드는 반드시 정수 또는 소수로 반환 (문자열 불가)
- 품목이 없으면 items는 빈 배열 []
- 금액 관련 필드가 없으면 0
- 카테고리는 가게 이름/품목으로 추론"""


def _extract_ocr_text(file_path: str, mime_type: str) -> str:
    """UpstageDocumentParseLoader로 파일에서 텍스트 추출"""
    is_pdf = mime_type == "application/pdf"
    ocr_mode = "auto" if is_pdf else "force"

    loader = UpstageDocumentParseLoader(
        file_path=file_path,
        split="none",
        ocr=ocr_mode,
        output_format="html",
        coordinates=False,
    )
    docs = loader.load()
    if not docs:
        raise ValueError("OCR 결과가 없습니다.")

    return "\n".join(doc.page_content for doc in docs)


def _parse_json_from_llm(ocr_text: str) -> dict:
    """ChatUpstage(Solar)로 OCR 텍스트 → 구조화 JSON 변환"""
    llm = ChatUpstage(model="solar-pro")
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"다음 영수증 내용을 파싱하세요:\n\n{ocr_text}"),
    ]
    response = llm.invoke(messages)
    raw = response.content.strip()

    # 코드블록 제거 (```json ... ```)
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error("LLM 응답 JSON 파싱 실패: %s\n원문: %s", e, raw)
        raise ValueError(f"LLM이 유효한 JSON을 반환하지 않았습니다: {e}")


def parse_receipt(file_bytes: bytes, filename: str, mime_type: str) -> dict:
    """영수증 파일을 OCR 파싱하여 구조화된 dict 반환.

    Args:
        file_bytes: 업로드된 파일 바이너리
        filename: 원본 파일명 (확장자 판별용)
        mime_type: MIME 타입

    Returns:
        구조화된 영수증 데이터 dict
    """
    suffix = Path(filename).suffix.lower() or ".bin"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        ocr_text = _extract_ocr_text(tmp_path, mime_type)
        logger.info("OCR 텍스트 추출 완료 (%d자)", len(ocr_text))

        parsed = _parse_json_from_llm(ocr_text)
        return parsed
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
