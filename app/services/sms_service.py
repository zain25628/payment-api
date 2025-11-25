
# Refactored by Copilot – SMS Service Feature
"""SMS parsing and persistence helpers.

This module validates channel API keys, parses incoming SMS payloads into a
normalized mapping ready for persistence, and stores payments by delegating
to `payment_service.create_payment_from_sms`.
"""
from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.models.channel import Channel
from app.models.payment import Payment
from app.services.payment_service import create_payment_from_sms


def validate_channel_api_key(db: Session, api_key: str) -> Optional[Channel]:
    """Return the active Channel matching `api_key` or None.

    Args:
        db: SQLAlchemy Session.
        api_key: The channel API key header value.
    """
    return db.query(Channel).filter(Channel.channel_api_key == api_key, Channel.is_active == True).first()


def parse_incoming_sms(payload: Dict) -> Dict:
    """Normalize raw incoming SMS payload into fields used for Payment creation.

    Expects (optionally): `payer_phone`, `receiver_phone`, `raw_message`,
    `amount`, `currency`, `txn_id`.

    Returns a dict with keys: `payer_phone`, `receiver_phone`, `raw_message`,
    `amount` (float), `currency` (default 'USD'), `txn_id`.
    """
    return {
        "payer_phone": payload.get("payer_phone"),
        "receiver_phone": payload.get("receiver_phone"),
        "raw_message": payload.get("raw_message"),
        "amount": float(payload.get("amount", 0)),
        "currency": payload.get("currency", "USD"),
        "txn_id": payload.get("txn_id"),
    }


def store_payment(db: Session, channel_id: int, company_id: int, parsed_data: Dict) -> Payment:
    """Persist a Payment built from `parsed_data` and return the created Payment.

    This function augments `parsed_data` with `channel_id`, `company_id`, and
    a default `status` of `new`, then delegates to
    `payment_service.create_payment_from_sms`.
    """
    payment_data = parsed_data.copy()
    payment_data["channel_id"] = channel_id
    payment_data["company_id"] = company_id
    payment_data["status"] = "new"
    return create_payment_from_sms(db, payment_data)
