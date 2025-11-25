# Refactored by Copilot – Wallet Repository
"""Repository layer for Wallet-related DB access.

This module centralizes queries for the `Wallet` entity used by
`wallet_service`.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import asc

from app.models.wallet import Wallet


def get_by_id(db: Session, wallet_id: int) -> Optional[Wallet]:
    """Return a Wallet by id or None."""
    return db.query(Wallet).filter(Wallet.id == wallet_id).first()


def get_company_active_wallets(db: Session, company_id: int) -> List[Wallet]:
    """Return active wallets for a company ordered by id.

    Mirrors the filtering used in `wallet_service.find_available_wallet`.
    """
    return (
        db.query(Wallet)
        .filter(Wallet.company_id == company_id, Wallet.is_active == True)
        .order_by(asc(Wallet.id))
        .all()
    )


def get_company_channel_active_wallets(db: Session, company_id: int, channel_id: int) -> List[Wallet]:
    """Return active wallets for a company scoped to a channel, ordered by id."""
    return (
        db.query(Wallet)
        .filter(
            Wallet.company_id == company_id,
            Wallet.channel_id == channel_id,
            Wallet.is_active == True,
        )
        .order_by(asc(Wallet.id))
        .all()
    )
