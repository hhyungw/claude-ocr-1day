"""GET /api/expenses, DELETE/PUT /api/expenses/{id}, GET /api/summary"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services import expense_store

router = APIRouter(prefix="/api", tags=["expenses"])


class ExpenseUpdate(BaseModel):
    model_config = {"extra": "allow"}

    store_name: Optional[str] = None
    receipt_date: Optional[str] = None
    receipt_time: Optional[str] = None
    category: Optional[str] = None
    items: Optional[list] = None
    subtotal: Optional[float] = None
    discount: Optional[float] = None
    tax: Optional[float] = None
    total_amount: Optional[float] = None
    payment_method: Optional[str] = None


@router.get("/expenses")
def list_expenses(from_date: Optional[str] = None, to_date: Optional[str] = None):
    """전체 지출 목록 조회 (날짜 범위 필터 선택)"""
    return expense_store.get_all(from_date=from_date, to_date=to_date)


@router.get("/expenses/{expense_id}")
def get_expense(expense_id: str):
    """단일 지출 항목 조회"""
    expense = expense_store.get_one(expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="해당 지출 항목을 찾을 수 없습니다.")
    return expense


@router.delete("/expenses/{expense_id}")
def delete_expense(expense_id: str):
    """지출 항목 삭제"""
    if not expense_store.delete(expense_id):
        raise HTTPException(status_code=404, detail="해당 지출 항목을 찾을 수 없습니다.")
    return {"message": "삭제되었습니다.", "id": expense_id}


@router.put("/expenses/{expense_id}")
def update_expense(expense_id: str, body: ExpenseUpdate):
    """지출 항목 수정"""
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    updated = expense_store.update(expense_id, updates)
    if updated is None:
        raise HTTPException(status_code=404, detail="해당 지출 항목을 찾을 수 없습니다.")
    return updated


@router.get("/summary")
def get_summary(month: Optional[str] = None):
    """지출 요약 통계 (월별 필터 선택, month 형식: YYYY-MM)"""
    return expense_store.get_summary(month=month)
