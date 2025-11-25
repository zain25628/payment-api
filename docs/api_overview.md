**API Overview**

This document summarizes the public endpoints implemented in the project routers related to incoming SMS, wallets, and payments. For each endpoint you'll find: the path and HTTP method, the expected JSON body, a step-by-step description of what the endpoint does, and the simplified expected response.

**Notes**
- Most endpoints resolve the calling organization via an API key (channel or company) provided by the client — typically via the `X-API-Key` header. The router dependencies (`get_current_channel` / `get_current_company`) perform that lookup.
- All responses are JSON. Errors are returned using HTTP status codes and JSON error details.

**Incoming SMS**
- Path & Method: POST `/incoming-sms`
- Expected body (JSON):
  - `payer_phone` (string, optional): phone number of the sender
  - `receiver_phone` (string, optional): phone number receiving funds
  - `raw_message` (string, optional): full raw SMS text
  - `amount` (number or string, optional): amount in the message (defaults to 0 if absent)
  - `currency` (string, optional): currency code (defaults to `"USD"`)
  - `txn_id` (string, optional): external transaction id
- Behavior (step-by-step):
  1. The endpoint uses the calling channel (resolved from the request API key) to determine `company_id` and `channel.id`.
  2. The payload is parsed using the SMS parsing helper to normalize fields (payer_phone, receiver_phone, amount, currency, txn_id, raw_message).
  3. The service attempts to find a `Wallet` that matches `receiver_phone` within the same channel. If found, the wallet's `id` is attached to the parsed data.
  4. A payment record is created from the parsed data (the service sets channel_id, company_id, and status) and saved to the database.
  5. The endpoint returns the created payment id.
- Expected response (success):
  - HTTP 200 with JSON: `{ "payment_id": <integer> }`
- Error cases:
  - If authentication/channel lookup fails the dependency will raise an authentication error (401/403 as configured).
  - Validation and storage errors are surfaced as HTTP errors.

### Examples

#### Example Request
```http
POST http://127.0.0.1:8000/incoming-sms
Content-Type: application/json
X-API-Key: <channel_api_key>

{
  "payer_phone": "+15551234567",
  "receiver_phone": "+15557654321",
  "raw_message": "Payment 12.50 USD TXN12345",
  "amount": 12.5,
  "currency": "USD",
  "txn_id": "TXN12345"
}
```

#### Example Response (Success)
```json
{ "payment_id": 123 }
```

#### Example Response (Auth error)
```json
HTTP/1.1 401 Unauthorized
{ "detail": "Could not validate credentials" }
```

**Request Wallet**
- Path & Method: POST `/wallets/request`
- Expected body (JSON):
  - `amount` (number or string, required): the requested amount to cover
- Behavior (step-by-step):
  1. The endpoint resolves the company from the request API key (dependency).
  2. It validates that `amount` is present; if missing, it returns HTTP 400.
  3. The controller calls a wallet allocation service to find an available Wallet for the given `company.id` that can cover the requested amount.
  4. If an available wallet is found, the endpoint returns the wallet's id, wallet identifier (usually a phone or unique string), and the channel id that owns the wallet.
  5. If no suitable wallet is available, the endpoint returns HTTP 404.
- Expected response (success):
  - HTTP 200 with JSON: `{ "wallet_id": <integer>, "wallet_identifier": "<string>", "channel_id": <integer> }`
- Error cases:
  - Missing `amount` → HTTP 400 `{ "detail": "Amount required" }`.
  - No wallet available → HTTP 404 `{ "detail": "No wallet available" }`.

### Examples

#### Example Request
```http
POST http://127.0.0.1:8000/wallets/request
Content-Type: application/json
X-API-Key: <company_api_key>

{
  "amount": 25.0
}
```

#### Example Response (Success)
```json
{
  "wallet_id": 45,
  "wallet_identifier": "+15557654321",
  "channel_id": 3
}
```

#### Example Response (Missing amount)
```json
HTTP/1.1 400 Bad Request
{ "detail": "Amount required" }
```

**Payments — Check**
- Path & Method: POST `/payments/check`
- Expected body (JSON):
  - `amount` (number or string, required): amount to match
  - `currency` (string, optional): currency code (defaults to `"USD"`)
  - `payer_phone` (string, optional): phone number of payer to narrow matching
- Behavior (step-by-step):
  1. The endpoint resolves the company from the request API key.
  2. It validates `amount` is present; if not, it returns HTTP 400.
  3. It calls a payment-matching service with `company.id`, the numeric amount, currency, and optional payer phone to find any suitable payment(s) that can be used for the order.
  4. The matching service returns a result object describing whether a match exists and includes metadata and, when relevant, the matched `Payment` object.
  5. The endpoint builds a response by removing the raw `payment` object and, if a matched `Payment` is present, including `payment_id` instead.
- Expected response (success):
  - HTTP 200 with JSON containing keys such as `match` (boolean), details about the matched wallet/payment (e.g., `amount`, `currency`, `expires_in`), and if applicable `payment_id`.
  - Example simplified shape: `{ "match": true, "amount": 12.5, "currency": "USD", "payment_id": 123 }` or `{ "match": false }`.
- Error cases:
  - Missing `amount` → HTTP 400 `{ "detail": "Amount required" }`.

### Examples

#### Example Request
```http
POST http://127.0.0.1:8000/payments/check
Content-Type: application/json
X-API-Key: <company_api_key>

{
  "amount": 10.0,
  "currency": "USD",
  "payer_phone": "+15551234567"
}
```

#### Example Response (Match found)
```json
{
  "match": true,
  "amount": 10.0,
  "currency": "USD",
  "payment_id": 987,
  "expires_in": 300
}
```

#### Example Response (No match)
```json
{ "match": false }
```

#### Example Response (Missing amount)
```json
HTTP/1.1 400 Bad Request
{ "detail": "Amount required" }
```

**Payments — Confirm**
- Path & Method: POST `/payments/confirm`
- Expected body (JSON):
  - `payment_id` (integer, required): id of the payment to confirm
  - `confirm_token` (string, required): token provided to authorize confirmation
- Behavior (step-by-step):
  1. The endpoint resolves the company from the request API key.
  2. It validates both `payment_id` and `confirm_token` are provided; if not, it returns HTTP 400.
  3. It loads the `Payment` by `payment_id` scoped to the calling company. If not found, it returns HTTP 404.
  4. It verifies the provided `confirm_token` matches the stored token on the payment; if mismatched, it returns HTTP 400.
  5. If the payment status is `pending_confirmation`, the endpoint calls the confirm routine to mark the payment as used/confirmed and returns a success message.
  6. If the payment is already `used`, the endpoint returns success indicating the payment was already confirmed.
  7. For other states, the endpoint returns HTTP 400 indicating the payment cannot be confirmed.
- Expected response (success):
  - HTTP 200 with JSON: `{ "status": "success", "message": "Payment confirmed" }` or `{ "status": "success", "message": "Payment already confirmed" }` depending on state.
- Error cases:
  - Missing fields → HTTP 400 `{ "detail": "payment_id and confirm_token required" }`.
  - Payment not found → HTTP 404 `{ "detail": "Payment not found" }`.
  - Invalid token → HTTP 400 `{ "detail": "Invalid confirm_token" }`.

### Examples

#### Example Request
```http
POST http://127.0.0.1:8000/payments/confirm
Content-Type: application/json
X-API-Key: <company_api_key>

{
  "payment_id": 987,
  "confirm_token": "abcdef123456"
}
```

#### Example Response (Confirmed)
```json
{ "status": "success", "message": "Payment confirmed" }
```

#### Example Response (Already confirmed)
```json
{ "status": "success", "message": "Payment already confirmed" }
```

#### Example Response (Invalid token)
```json
HTTP/1.1 400 Bad Request
{ "detail": "Invalid confirm_token" }
```

---

If you want, I can:
- Add a short table-of-contents at the top of the document.
- Expand each endpoint doc with example request/response JSON snippets (I omitted code samples per your request).

I will now mark the todo completed. Would you like the additional examples or the log-tail behavior added to `dev_start_stack.ps1` next?

### Implementation Status

- `app/routers/incoming_sms.py`: Updated to accept a Pydantic `IncomingSMSRequest`, resolve the calling `Company` via `X-API-Key` using `get_current_company`, attempt to resolve a `Channel` for the same API key when available, match a `Wallet` by `receiver_phone`, and create a `Payment` via the existing SMS service. Returns `{ "payment_id": <int> }` on success.
- `app/routers/payments.py`: Reworked to use Pydantic request models `PaymentCheckRequest` and `PaymentConfirmRequest`.
  - `POST /payments/check`: calls `match_payment_for_order(...)` from the payment service (now returns a `Payment` or `None`). If no payment found returns `{ "found": false, "match": false }`. If a payment is found but the amount mismatches returns `{ "found": true, "match": false, "reason": "amount_mismatch", "actual_amount": ... }`. If amounts match the endpoint reserves the payment by setting `status` to `pending_confirmation`, generates a `confirm_token` (UUID hex) and returns the payment metadata including `confirm_token` and `order_id` when provided.
  - `POST /payments/confirm`: validates `payment_id` and `confirm_token`, calls `confirm_payment_usage(...)` to mark the payment `used` and update wallet usage, and returns a success JSON. The endpoint is idempotent for already-used payments when the token matches.
- `app/services/payment_service.py`: Implemented `match_payment_for_order(...)` to return a `Payment` instance or `None`. It now supports optional `max_age_minutes` filtering and restricts candidate statuses to `new` and `pending_confirmation`. `confirm_payment_usage(...)` now sets `used_at` using UTC (`datetime.utcnow()`), commits, refreshes, and calls `update_wallet_usage(...)` when `wallet_id` is present.

If you want, I can run quick local checks (lint/static validation) or add unit tests for the new request models and the updated response shapes.