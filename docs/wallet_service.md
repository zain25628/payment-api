# Wallet Service

## Responsibility

The Wallet Service contains domain logic for selecting and accounting wallet usage. It is responsible for:

- Resetting daily usage for wallets when the day rolls over.
- Selecting an available wallet for a requested amount (`find_available_wallet`).
- Updating wallet usage when a payment consumes wallet capacity (`update_wallet_usage`).

## Key Functions

- `reset_wallet_if_needed(wallet, db)`
  - Description: Reset `wallet.used_today` to `0.0` and set `wallet.last_reset_date` to today if the stored date is missing or older than today. Persists changes when a reset occurs.
  - Inputs: `wallet: Wallet`, `db: Session`.
  - Output: `None`.

- `find_available_wallet(db, company_id, amount)`
  - Description: Iterate active wallets for a company (ordered by `id`), reset each wallet if needed, and return the first wallet that can accept the requested amount without exceeding its `daily_limit`.
  - Inputs: `db: Session`, `company_id: int`, `amount: float`.
  - Output: `Wallet` or `None`.

- `update_wallet_usage(db, wallet_id, amount)`
  - Description: Find wallet by `wallet_id`, reset its usage if needed, increment `used_today` by `amount`, and persist changes. If wallet not found, returns `None`.
  - Inputs: `db: Session`, `wallet_id: int`, `amount: float`.
  - Output: Updated `Wallet` or `None`.

## Interaction with Other Components

- `models.Wallet`: Primary data model this service manipulates.
- `payment_service.confirm_payment_usage`: Calls into wallet usage update when a payment is consumed.

## Notes

- This module favors small, testable functions. Unit tests can stub the `db` session to avoid a real database.
