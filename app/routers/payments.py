# Refactored by Copilot – Payments Feature
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session

from app.dependencies.deps import get_db, get_current_company
from app.models.company import Company
from app.models.payment import Payment
import app.services.payment_service as payment_service


router = APIRouter(tags=["payments"])


class PaymentMatchRequest(BaseModel):
    order_id: Optional[str] = Field(default=None, description="Client order reference")
    txn_id: Optional[str] = Field(default=None, description="Provider transaction id, if available")
    amount: float = Field(..., gt=0, description="Expected payment amount")
    currency: Optional[str] = Field(default="USD")
    payer_phone: Optional[str] = None


class PaymentMatchResponse(BaseModel):
    found: bool
    match: bool
    payment_id: Optional[int] = None
    txn_id: Optional[str] = None
    status: Optional[str] = None


class PaymentStatusResponse(BaseModel):
    payment_id: int
    status: str


@router.post("/payments/match", response_model=PaymentMatchResponse)
def payments_match(
    payload: PaymentMatchRequest,
    db: Session = Depends(get_db),
    company: Company = Depends(get_current_company),
):
    """Attempt to find a recent payment that matches the expected amount/txn/order.

    Delegates matching to `match_payment_for_order` in the payment service.
    """
    payment = payment_service.match_payment_for_order(
        db,
        company.id,
        float(payload.amount),
        payload.currency or "USD",
        payload.payer_phone,
    )

    if payment is None:
        return PaymentMatchResponse(found=False, match=False)

    # Simple amount tolerance check (same behavior as previous implementation)
    if abs(payment.amount - float(payload.amount)) > 0.01:
        return PaymentMatchResponse(found=True, match=False, payment_id=payment.id, txn_id=payment.txn_id, status=payment.status)

    return PaymentMatchResponse(found=True, match=True, payment_id=payment.id, txn_id=payment.txn_id, status=payment.status)


@router.post("/payments/{payment_id}/pending-confirmation", response_model=PaymentStatusResponse)
def payments_pending_confirmation(
    payment_id: int,
    db: Session = Depends(get_db),
    company: Company = Depends(get_current_company),
):
    """Mark a payment as pending confirmation if it belongs to the current company."""
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.company_id == company.id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment = payment_service.mark_payment_pending_confirmation(db, payment)
    return PaymentStatusResponse(payment_id=payment.id, status=payment.status)


@router.post("/payments/{payment_id}/confirm-usage", response_model=PaymentStatusResponse)
def payments_confirm_usage(
    payment_id: int,
    db: Session = Depends(get_db),
    company: Company = Depends(get_current_company),
):
    """Confirm a pending payment usage (mark as used) if payment belongs to company."""
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.company_id == company.id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment = payment_service.confirm_payment_usage(db, payment)
    return PaymentStatusResponse(payment_id=payment.id, status=payment.status)
