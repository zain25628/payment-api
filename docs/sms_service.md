# SMS Service

## Responsibility

This service is responsible for:
- Validating channel API keys (`channel_api_key`).
- Parsing raw SMS payloads into a normalized structure.
- Creating Payment records by delegating to `payment_service.create_payment_from_sms`.

## Data Flow

Example sequence:

Provider → POST `/incoming-sms` → `deps.get_current_company` / `deps.get_current_channel` →
`sms_service.parse_incoming_sms` → `sms_service.store_payment` → Payment stored.

## Key Functions

- `validate_channel_api_key(db, api_key)` — looks up an active `Channel` by API key and returns it or `None`.
- `parse_incoming_sms(payload)` — normalizes fields from the raw incoming payload and returns a dict with `payer_phone`, `receiver_phone`, `raw_message`, `amount` (float), `currency`, and `txn_id`.
- `store_payment(db, channel_id, company_id, parsed_data)` — augments `parsed_data` with `channel_id`, `company_id`, and `status='new'`, then delegates creation to `payment_service.create_payment_from_sms` and returns the created `Payment`.

