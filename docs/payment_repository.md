# Payment Repository

## Responsibility

The Payment Repository centralizes SQLAlchemy queries and persistence for the `Payment` entity. It isolates ORM code from the service layer so services can focus on domain logic and tests can more easily stub repository behavior.

## Key Functions

- `create(db, payment)`
  - Persists a `Payment` instance, commits, refreshes, and returns the persisted object.

- `find_most_recent_matching(db, company_id, currency, payer_phone=None, max_age_minutes=None)`
  - Finds the most-recent payment for a company and currency with status in `['new','pending_confirmation']`.
  - Optionally filters by `payer_phone` and limits candidates to those created within `max_age_minutes`.
  - Returns the most recent matching `Payment` or `None`.

- `get_by_id_for_company(db, company_id, payment_id)`
  - Looks up a payment by id, scoped to the provided `company_id`. Returns `Payment` or `None`.

## Interaction

- `payment_service` uses this repository instead of issuing `db.query(...)` calls directly.
- Routers should call `payment_service` rather than the repository directly to keep layering clear.
