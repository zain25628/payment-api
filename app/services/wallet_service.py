
# Refactored by Copilot – Wallet Service Feature
"""Wallet-related domain helpers.

This module provides small utilities around wallet usage tracking and
selection. Changes here are limited to type hints and docstrings; behavior
and signatures are preserved.
"""
from typing import Optional
from sqlalchemy.orm import Session
from datetime import date
from app.models.wallet import Wallet
from sqlalchemy import asc

import app.repositories.wallet_repository as wallet_repository


def reset_wallet_if_needed(wallet: Wallet, db: Session) -> None:
    """Reset a wallet's daily usage if the last reset date is before today.

    Args:
        wallet: `Wallet` instance to inspect and potentially reset.
        db: SQLAlchemy `Session` used to persist changes when a reset occurs.

    Behavior:
        - If `wallet.last_reset_date` is None or older than today, set
          `wallet.used_today = 0.0` and update `wallet.last_reset_date` to today,
          then persist via `db.add`, `db.commit`, `db.refresh`.
        - Otherwise perform no changes.
    """
    today = date.today()
    if wallet.last_reset_date is None or wallet.last_reset_date < today:
        wallet.used_today = 0.0
        wallet.last_reset_date = today
        db.add(wallet)
        db.commit()
        db.refresh(wallet)


def find_available_wallet(db: Session, company_id: int, amount: float) -> Optional[Wallet]:
    """Return the first active wallet for `company_id` that can accept `amount`.

    The selection iterates wallets ordered by `id`, resets daily usage if needed,
    and returns the first wallet where `used_today + amount <= daily_limit`.

    Returns:
        A `Wallet` instance when found, otherwise `None`.
    """
    wallets = wallet_repository.get_company_active_wallets(db, company_id)

    for wallet in wallets:
        reset_wallet_if_needed(wallet, db)
        if wallet.used_today + amount <= wallet.daily_limit:
            return wallet
    return None


def update_wallet_usage(db: Session, wallet_id: int, amount: float) -> Optional[Wallet]:
    """Increment `used_today` on the wallet and persist changes.

    Args:
        db: SQLAlchemy `Session` used to query and persist the wallet.
        wallet_id: Identifier of the wallet to update.
        amount: Amount to add to the wallet's `used_today`.

    Returns:
        The updated `Wallet` when found and updated; otherwise `None`.
    """
    wallet = wallet_repository.get_by_id(db, wallet_id)
    if wallet:
        reset_wallet_if_needed(wallet, db)
        wallet.used_today += amount
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
        return wallet
    return None
