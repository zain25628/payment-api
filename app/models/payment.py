# Refactored by Copilot
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.config import settings, get_settings


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    txn_id = Column(String, unique=True, index=True, nullable=True)
    payer_phone = Column(String, nullable=False)
    receiver_phone = Column(String, nullable=False)
    raw_message = Column(String, nullable=False)
    status = Column(String, default="new") # new/pending_confirmation/used/mismatch
    order_id = Column(String, nullable=True)
    confirm_token = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    used_at = Column(DateTime(timezone=True), nullable=True)

    company = relationship("Company", back_populates="payments")
    channel = relationship("Channel", back_populates="payments")
    wallet = relationship("Wallet", back_populates="payments")
