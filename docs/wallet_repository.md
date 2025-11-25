# Wallet Repository

## Responsibility

The Wallet Repository centralizes SQLAlchemy queries for the `Wallet` entity. Services call into this module to obtain candidate wallets and individual wallet records.

## Key Functions

- `get_by_id(db, wallet_id)` — return a `Wallet` or `None`.
- `get_company_active_wallets(db, company_id)` — return active wallets for a company ordered by `id`.
- `get_company_channel_active_wallets(db, company_id, channel_id)` — return active wallets for a company & channel ordered by `id`.

## Interaction

- `wallet_service` uses this repository to obtain wallet lists and lookup wallets by id.
- Tests for repository use SQLite in-memory to validate filtering and ordering.
