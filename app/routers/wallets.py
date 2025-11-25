# Refactored by Copilot
"""
# Refactored by Copilot – Wallets Feature
Organize the `/wallets/request` endpoint to use Pydantic request/response
models and clear validation while preserving the existing wallet selection
logic in `find_available_wallet`.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.config import settings, get_settings
from app.db.session import get_db
from app.dependencies.deps import get_current_company
from app.models.company import Company
from app.models.wallet import Wallet
from app.services.wallet_service import find_available_wallet


class WalletRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Requested payment amount, must be > 0")


class WalletResponse(BaseModel):
    wallet_id: int
    wallet_identifier: str
    channel_id: int


router = APIRouter(tags=["wallets"])


@router.post("/wallets/request", response_model=WalletResponse)
def request_wallet(
    payload: WalletRequest,
    db: Session = Depends(get_db),
    company: Company = Depends(get_current_company),
):
    """Select an available wallet for the requested amount for the current company.

    The endpoint depends on `X-API-Key` (resolved by `get_current_company`) to
    identify the company. The actual selection logic is delegated to
    `find_available_wallet` and is not changed here.
    """
    amount = float(payload.amount)

    wallet = find_available_wallet(db, company.id, amount)
    if wallet:
        return WalletResponse(
            wallet_id=wallet.id,
            wallet_identifier=wallet.wallet_identifier,
            channel_id=wallet.channel_id,
        )

    raise HTTPException(
        status_code=404,
        detail="No wallet available for the requested amount",
    )
