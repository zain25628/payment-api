# Refactored by Copilot – Dependencies (Auth)
"""Authentication dependencies used by FastAPI routes.

This module exposes `get_current_company` and `get_current_channel` which
resolve identity based on API keys provided in request headers.

Note: logic/behavior unchanged — only docstrings and type hints added.
"""
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.company import Company
from app.models.channel import Channel


def get_current_company(
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> Company:
    """Resolve the current Company from `X-API-Key` header.

    Resolution steps (in order):
    1. Try to find a Channel whose `channel_api_key` equals the provided key
       and return its Company (requires Channel.is_active and Company.is_active).
    2. Fallback to matching `Company.api_key` directly (requires Company.is_active).

    Raises:
        HTTPException(status_code=401) when no active Company/Channel is found.

    Returns:
        The resolved `Company` instance.
    """
    # Debug trace (kept from previous implementation)
    print(f"[DEBUG] get_current_company: X-API-Key={x_api_key!r}")

    # 1) Try resolve via Channel.channel_api_key
    company = (
        db.query(Company)
        .join(Channel, Channel.company_id == Company.id)
        .filter(
            Channel.channel_api_key == x_api_key,
            Channel.is_active.is_(True),
            Company.is_active.is_(True),
        )
        .first()
    )

    if company:
        print(
            f"[DEBUG] Resolved company via Channel: "
            f"company_id={company.id}, name={company.name}"
        )
        return company

    # 2) Fallback: match directly on Company.api_key
    company = (
        db.query(Company)
        .filter(
            Company.api_key == x_api_key,
            Company.is_active.is_(True),
        )
        .first()
    )

    if company:
        print(
            f"[DEBUG] Resolved company via Company.api_key: "
            f"company_id={company.id}, name={company.name}"
        )
        return company

    # 3) No match: raise 401
    print(f"[DEBUG] No active company found for API key {x_api_key!r}")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or inactive API key",
    )


def get_current_channel(
    channel_api_key: str = Header(..., alias="channel_api_key"),
    db: Session = Depends(get_db),
) -> Channel:
    """Resolve the current Channel from `channel_api_key` header.

    The function ensures the channel is active; otherwise raises HTTP 401.

    Returns:
        The resolved `Channel` instance.
    """
    channel = db.query(Channel).filter(Channel.channel_api_key == channel_api_key, Channel.is_active == True).first()
    if not channel:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Channel API Key")
    return channel
