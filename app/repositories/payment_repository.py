# Refactored by Copilot – Payment Repository
"""Repository layer for Payment-related DB access.

This module centralizes queries and persistence for `Payment` entities so
service logic can remain focused on domain behavior.
"""
from datetime import timedelta, datetime, timezone
from typing import Optional, Sequence, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.payment import Payment


def create(db: Session, payment: Payment) -> Payment:
    """Persist a new Payment instance and return the refreshed object.

    Args:
        db: SQLAlchemy `Session` used to persist the Payment.
        payment: The `Payment` instance to persist. The instance may be
            constructed by a service and passed in for persistence.

    Returns:
        The refreshed `Payment` instance after commit/refresh.
    """
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def find_most_recent_matching(
    db: Session,
    company_id: int,
    currency: str,
    payer_phone: Optional[str] = None,
    max_age_minutes: Optional[int] = None,
) -> Optional[Payment]:
    """Return the most-recent Payment candidate matching the criteria.

    The query filters payments for the `company_id` and `currency` and
    limits to payments with status in `['new','pending_confirmation']`.
    Optionally narrows by `payer_phone` and by an age window given by
    `max_age_minutes` (relative to now).

    Args:
        db: SQLAlchemy Session.
        company_id: Company id to scope results.
        currency: Currency code to match.
        payer_phone: Optional phone to further filter.
        max_age_minutes: Optional integer to limit candidate age (minutes).

    Returns:
        The most-recent matching Payment or None.
    """
    query = db.query(Payment).filter(
        Payment.company_id == company_id,
        Payment.currency == currency,
        Payment.status.in_(["new", "pending_confirmation"]),
    )

    if payer_phone:
        query = query.filter(Payment.payer_phone == payer_phone)

    if max_age_minutes is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=int(max_age_minutes))
        query = query.filter(Payment.created_at >= cutoff)

    payment = query.order_by(desc(Payment.created_at)).first()
    return payment


def get_by_id_for_company(db: Session, company_id: int, payment_id: int) -> Optional[Payment]:
    """Return a payment by id scoped to a company, or None if not found.

    Args:
        db: SQLAlchemy Session.
        company_id: Company id to enforce scoping.
        payment_id: Payment id to lookup.

    Returns:
        The Payment when found and belonging to `company_id`, else None.
    """
    return db.query(Payment).filter(Payment.id == payment_id, Payment.company_id == company_id).first()
