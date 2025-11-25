# Refactored by Copilot
"""
# Refactored by Copilot – Incoming SMS Feature
Clean, typed incoming SMS endpoint. Delegates parsing and persistence to
`sms_service` while validating input shape and returning a typed response.
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional

from app.config import settings, get_settings
from app.db.session import get_db
from app.dependencies.deps import get_current_company
from app.models.channel import Channel
from app.models.wallet import Wallet
from app.models.company import Company
import app.services.sms_service as sms_service


class IncomingSMSRequest(BaseModel):
    payer_phone: Optional[str] = Field(default=None, description="Phone number of the sender (payer)")
    receiver_phone: Optional[str] = Field(default=None, description="Phone number receiving funds (wallet)")
    raw_message: str = Field(..., description="Raw full SMS message text")
    amount: Optional[float] = Field(default=None, gt=0, description="Parsed amount, if already known")
    currency: Optional[str] = Field(default="USD", description="Currency code")
    txn_id: Optional[str] = Field(default=None, description="Provider transaction identifier, if available")


class IncomingSMSResponse(BaseModel):
    payment_id: int


router = APIRouter(tags=["incoming-sms"])


@router.post("/incoming-sms", response_model=IncomingSMSResponse)
def incoming_sms(
    payload: IncomingSMSRequest,
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db),
    company: Company = Depends(get_current_company),
):
    """Handle an incoming payment SMS.

    - Resolves the calling company via `X-API-Key` header (dependency `get_current_company`).
    - Optionally determines the Channel that sent the notification and scopes wallet lookup.
    - Delegates parsing to `sms_service.parse_incoming_sms` and persistence to `sms_service.store_payment`.
    - Returns the created `payment_id`.
    """

    payload_dict = payload.model_dump()

    # Resolve channel by the same API key if present
    channel = (
        db.query(Channel)
        .filter(Channel.channel_api_key == x_api_key, Channel.company_id == company.id, Channel.is_active == True)
        .first()
    )
    channel_id = channel.id if channel else None

    # Parse and normalize incoming SMS fields using service logic
    try:
        parsed_data = sms_service.parse_incoming_sms(payload_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid SMS payload: {e}")

    # Attempt to associate a wallet by receiver_phone (preserve existing behavior)
    try:
        wallet_query = db.query(Wallet).filter(Wallet.wallet_identifier == parsed_data.get("receiver_phone"))
        if channel_id:
            wallet_query = wallet_query.filter(Wallet.channel_id == channel_id)
        else:
            wallet_query = wallet_query.filter(Wallet.company_id == company.id)
        wallet = wallet_query.first()
        if wallet:
            parsed_data["wallet_id"] = wallet.id
    except Exception:
        # Keep behavior tolerant — wallet association is best-effort
        wallet = None

    # Persist payment via sms_service
    payment = sms_service.store_payment(db, channel_id, company.id, parsed_data)
    return IncomingSMSResponse(payment_id=payment.id)
