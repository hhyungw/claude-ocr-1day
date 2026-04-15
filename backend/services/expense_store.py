"""expenses.json 파일 기반 CRUD 스토어"""

import json
import os
from pathlib import Path
from typing import Optional

DATA_FILE = Path(__file__).parent.parent / "data" / "expenses.json"


def _load() -> list:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        return json.loads(content) if content else []


def _save(expenses: list) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(expenses, f, ensure_ascii=False, indent=2)


def get_all(from_date: Optional[str] = None, to_date: Optional[str] = None) -> list:
    """전체 지출 목록 조회. 날짜 범위 필터 선택 적용."""
    expenses = _load()
    if from_date:
        expenses = [e for e in expenses if (e.get("receipt_date") or "") >= from_date]
    if to_date:
        expenses = [e for e in expenses if (e.get("receipt_date") or "") <= to_date]
    return expenses


def append(expense: dict) -> dict:
    """지출 항목 추가 저장 후 반환."""
    expenses = _load()
    expenses.append(expense)
    _save(expenses)
    return expense


def delete(expense_id: str) -> bool:
    """ID로 지출 항목 삭제. 삭제 성공 여부 반환."""
    expenses = _load()
    filtered = [e for e in expenses if e.get("id") != expense_id]
    if len(filtered) == len(expenses):
        return False
    _save(filtered)
    return True


def update(expense_id: str, updates: dict) -> Optional[dict]:
    """ID로 지출 항목 수정 후 수정된 객체 반환. 없으면 None."""
    expenses = _load()
    for i, expense in enumerate(expenses):
        if expense.get("id") == expense_id:
            # id, created_at은 변경 불가
            updates.pop("id", None)
            updates.pop("created_at", None)
            expenses[i] = {**expense, **updates}
            _save(expenses)
            return expenses[i]
    return None


def get_summary(month: Optional[str] = None) -> dict:
    """지출 요약 통계 반환.

    Args:
        month: 필터할 월 (YYYY-MM 형식, 선택)

    Returns:
        total_amount, count, by_category 포함 dict
    """
    expenses = _load()
    if month:
        expenses = [e for e in expenses if (e.get("receipt_date") or "").startswith(month)]

    total = sum(e.get("total_amount", 0) for e in expenses)
    by_category: dict = {}
    for e in expenses:
        cat = e.get("category") or "기타"
        by_category[cat] = by_category.get(cat, 0) + e.get("total_amount", 0)

    return {
        "total_amount": total,
        "count": len(expenses),
        "by_category": by_category,
    }
