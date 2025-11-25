# Payments Endpoints

## Overview
This group of endpoints allows integrators to:
- Search for a payment (match) based on order_id/txn_id/amount.
- Mark a payment as pending confirmation.
- Confirm a payment usage (mark as used).

## Authentication
All endpoints require the header `X-API-Key` to identify the calling company. The application resolves the company using the `get_current_company` dependency.

---

### POST /payments/match
- Purpose: find a recent payment that matches the expected amount and optional payer/txn.
- Request body:
  - `amount` (float, > 0) — required
  - `order_id` (string, optional)
  - `txn_id` (string, optional)
  - `currency` (string, optional, default `USD`)
  - `payer_phone` (string, optional)
- Response example:
```json
{
  "found": false,
  "match": false
}
```
Or when matched:
```json
{
  "found": true,
  "match": true,
  "payment_id": 123,
  "txn_id": "ABC123",
  "status": "new"
}
```

---

### POST /payments/{payment_id}/pending-confirmation
- Purpose: mark an existing payment as `pending_confirmation`.
- Path params: `payment_id` (int)
- Response example:
```json
{
  "payment_id": 123,
  "status": "pending_confirmation"
}
```

---

### POST /payments/{payment_id}/confirm-usage
- Purpose: mark a payment as used (consume it).
- Path params: `payment_id` (int)
- Response example:
```json
{
  "payment_id": 123,
  "status": "used"
}
```

---

## Error Responses
- `401/403` — invalid or unauthorized `X-API-Key`.
- `404` — `Payment not found` when the payment id is not found or doesn't belong to the company.
- `422` — validation errors (e.g., missing `amount`).
- Other `4xx/5xx` — service/database errors as they arise.
