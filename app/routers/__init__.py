# Refactored by Copilot
# routers package initializer

from . import health, incoming_sms, wallets, payments  # noqa: F401

__all__ = ["health", "incoming_sms", "wallets", "payments"]
