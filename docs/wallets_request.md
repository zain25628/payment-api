# Wallet Request Endpoint

## Purpose
The `/wallets/request` endpoint allows an integrator to request a wallet (an account/identifier) capable of receiving a payment of a specified amount for the company identified by the provided API key.

## Authentication
Requests must include the header `X-API-Key` which identifies the company making the request. The system resolves the company and scopes wallet selection accordingly.

## Request
- Method: `POST`
- Path: `/wallets/request`
- Body (JSON):
  - `amount` (float, > 0) — the requested payment amount

### Example Request
```http
POST /wallets/request HTTP/1.1
Host: example.local:8000
Content-Type: application/json
X-API-Key: <company_api_key>

{
  "amount": 150.0
}
```

## Successful Response
- Status: `200 OK`
- Body (JSON):
```json
{
  "wallet_id": 1,
  "wallet_identifier": "9715xxxxxxx",
  "channel_id": 2
}
```

## Error Responses
- `400` / `422` — invalid input (e.g., missing or non-positive amount)
- `404` — no wallet available for the requested amount

## Notes
- The wallet selection algorithm (`find_available_wallet`) enforces daily limits and selection rules; this endpoint delegates selection to that service and does not implement selection logic itself.
