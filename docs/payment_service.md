# Payment Service

## Responsibility

The Payment Service contains domain logic for creating and managing `Payment` records. It is responsible for:

- Creating `Payment` records from normalized SMS payloads.
- Attempting to match incoming payments to orders/transactions.
- Marking payments as `pending_confirmation` and generating confirmation tokens.
- Confirming payment usage and triggering wallet usage updates.

## Key Functions

- `create_payment_from_sms(db, payment_data)`
  - Description: Construct a `Payment` model from `payment_data`, persist it, and return the refreshed object.
  - Important inputs: `db: Session`, `payment_data: dict` (fields such as `company_id`, `channel_id`, `amount`, `payer_phone`, `receiver_phone`, `raw_message`).
  - Output: `Payment` instance.

- `match_payment_for_order(db, company_id, amount, currency, payer_phone=None, max_age_minutes=None)`
  - Description: Query recent payments for the company and attempt to find the most-recent candidate that is `new` or `pending_confirmation` and matches currency (optionally narrowed by payer phone and age).
  - Important inputs: `db: Session`, `company_id: int`, `amount: float`, `currency: str`, optional `payer_phone`, `max_age_minutes` to limit age.
  - Output: `Payment` or `None`.

- `mark_payment_pending_confirmation(db, payment)`
  - Description: Mutates `payment` to set it to `pending_confirmation`, generates and stores a `confirm_token`, persists and returns the refreshed `Payment`.
  - Important inputs: `db: Session`, `payment: Payment`.
  - Output: `Payment`.

- `confirm_payment_usage(db, payment)`
  - Description: Marks the `payment` as `used`, sets `used_at`, persists, and if a `wallet_id` exists calls `wallet_service.update_wallet_usage(db, wallet_id, amount)` to adjust wallet usage.
  - Important inputs: `db: Session`, `payment: Payment`.
  - Output: `Payment`.

## Interaction with Other Components

- `models.Payment`: Primary data model persisted by this service.
- `wallet_service.update_wallet_usage`: Invoked when a confirmed payment is associated with a wallet; the implementation of wallet usage accounting lives in `wallet_service`.
- `routers/payments`: Exposes endpoints that call into this service (matching, pending confirmation, confirm usage).

## Notes

- This module intentionally keeps behavior minimal and delegates persistence to SQLAlchemy sessions.
- Tests targeting this service should focus on business logic and can stub or fake the `db` session to avoid a real database.
