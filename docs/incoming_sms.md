# Incoming SMS Endpoint

## Purpose
The `/incoming-sms` endpoint is the primary entrypoint for payment notifications sent by SMS gateway providers. It accepts a normalized JSON payload representing the SMS content and metadata, delegates parsing and persistence to application services, and returns the created payment id.

## Authentication
Requests must include the header `X-API-Key` which identifies the company making the request. The application resolves the company (and optionally a Channel) using `get_current_company` dependency.

## Request
- Method: `POST`
- Path: `/incoming-sms`
- Body (JSON):
  - `payer_phone` (string, optional)
  - `receiver_phone` (string, optional)
  - `raw_message` (string, required) — full SMS text
  - `amount` (float, optional, > 0)
  - `currency` (string, optional, default `USD`)
  - `txn_id` (string, optional)

### Example Request
```http
POST /incoming-sms HTTP/1.1
Host: example.local:8000
Content-Type: application/json
X-API-Key: <company_api_key>

{
  "payer_phone": "9715xxxxxxx",
  "receiver_phone": "9715yyyyyyy",
  "raw_message": "Your account has been credited with 150.00 AED ...",
  "amount": 150.0,
  "currency": "AED",
  "txn_id": "ABC123"
}
```

## Successful Response
- Status: `200 OK`
- Body (JSON):
```json
{
  "payment_id": 1234
}
```

## Error Responses
- `401/403` — invalid or unauthorized `X-API-Key` (delegated to `get_current_company`).
- `422` — validation errors (e.g., missing `raw_message` or invalid `amount`).
- `4xx/5xx` — other errors depending on service behavior (database, parsing errors, etc.).
