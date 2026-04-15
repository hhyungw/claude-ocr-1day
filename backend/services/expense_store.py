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


def get_one(expense_id: str) -> Optional[dict]:
    """ID로 단일 지출 항목 반환. 없으면 None."""
    for expense in _load():
        if expense.get("id") == expense_id:
            return expense
    return None


def get_summary(month: Optional[str] = None) -> dict:
    """지출 요약 통계 반환.

    Args:
        month: 필터할 월 (YYYY-MM 형식, 선택). 없으면 전체 기간 집계.

    Returns:
        PRD 명세 형식:
        {
            "total_amount": int,
            "this_month_amount": int,
            "count": int,
            "category_summary": [{"category": str, "amount": int}, ...]
        }
    """
    from datetime import date

    all_expenses = _load()

    # this_month_amount: 항상 현재 월 기준
    current_month = date.today().strftime("%Y-%m")
    this_month_expenses = [
        e for e in all_expenses
        if (e.get("receipt_date") or "").startswith(current_month)
    ]

    # 집계 대상: month 파라미터가 있으면 해당 월만, 없으면 전체
    target = all_expenses
    if month:
        target = [e for e in all_expenses if (e.get("receipt_date") or "").startswith(month)]

    total = sum(e.get("total_amount", 0) for e in target)
    this_month_total = sum(e.get("total_amount", 0) for e in this_month_expenses)

    by_category: dict = {}
    for e in target:
        cat = e.get("category") or "기타"
        by_category[cat] = by_category.get(cat, 0) + e.get("total_amount", 0)

    category_summary = [
        {"category": cat, "amount": amount}
        for cat, amount in sorted(by_category.items(), key=lambda x: -x[1])
    ]

    return {
        "total_amount": total,
        "this_month_amount": this_month_total,
        "count": len(target),
        "category_summary": category_summary,
    }
