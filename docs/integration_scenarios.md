# Integration Scenarios

This document describes three common integration scenarios for external systems (SMS providers, control panels, or bots) to interact with the API. Each scenario explains the caller, the sequence of API calls, internal system logic, and the possible responses.

## 1) Incoming SMS Payment Notification

Who calls the endpoint
1. An SMS gateway or an integration service (middleware) forwards inbound payment SMS messages to your platform.
2. The provider sends an HTTP POST to `/incoming-sms` containing the SMS payload.

Sequence and what happens inside
1. Authentication and routing
   - The caller includes the `X-API-Key` header which maps to a specific `Channel`. The dependency `get_current_channel` validates the API key and resolves the `Channel` and its `company_id`.
2. Parse and normalize
   - The endpoint calls the SMS parsing helper which extracts structured fields from the raw payload: `payer_phone`, `receiver_phone`, `amount`, `currency`, `txn_id`, and `raw_message`.
3. Wallet matching
   - The system attempts to find a `Wallet` record whose `wallet_identifier` equals the parsed `receiver_phone`, constrained to the channel that owns the API key. If found, the wallet id is attached to the payment data so the payment is linked to that wallet.
4. Create payment record
   - A `Payment` record is created with fields from the parsed payload plus `channel_id`, `company_id`, and an initial `status` (e.g., `new`). This record persists metadata used later for matching and confirmation.
5. Return
   - The endpoint returns a minimal success response containing the new `payment_id`.

Responses external integrations should expect
- Success: HTTP 200 with JSON `{ "payment_id": <id> }`.
- Authentication failure: HTTP 401/403 if the `X-API-Key` is invalid.
- Validation/storage failure: HTTP 4xx/5xx with JSON error details. For example, if the SMS payload cannot be parsed or database constraints fail, the integration receives a corresponding error.

Operational notes and best practices
- Idempotency: Providers may resend messages; include logic on their side to detect duplicates or let the backend de-duplicate by `txn_id` when present.
- Logging: Log the incoming raw_message and parsing result for troubleshooting.
- Retries: If the provider retries POSTs, the backend should tolerate repeated identical payloads and avoid duplicate money processing.

## 2) Wallet Creation / Management

Who calls the endpoint
1. An admin console, control dashboard, or bot (for example, a Telegram or Slack bot used by merchants) calls `/wallets/request` to find/allocate a wallet for a requested amount.

Sequence and what happens inside
1. Authenticate
   - The caller provides a company-level API key (`X-API-Key`) resolved to a `Company` by the `get_current_company` dependency.
2. Validate request
   - The controller ensures the `amount` field is present and numeric. If missing, the request fails with HTTP 400.
3. Wallet allocation
   - The controller calls the wallet allocation service (`find_available_wallet`) which runs business logic to pick an appropriate `Wallet` that:
     - Belongs to the requesting `Company`.
     - Is active and not currently reserved.
     - Can cover the requested amount (based on configured limits or balance heuristics).
4. Persisting and response
   - If the allocation service returns a wallet, the controller returns `wallet_id`, `wallet_identifier` (the string used for routing, often a phone number), and `channel_id`.
   - If none are available, the controller returns HTTP 404.

What is stored in the `wallets` table and how it is used
- Typical fields stored for each wallet:
  - `id`: internal identifier
  - `company_id`: owning company
  - `channel_id`: owning channel (the routing channel tied to a provider or phone number)
  - `wallet_identifier`: the external identifier (phone number or token) used to receive money
  - `wallet_label`: human readable label used in UIs (optional)
  - `is_active`, `created_at`, `updated_at`, and any allocation metadata such as `max_amount` or `current_balance` if implemented
- How wallet fields are used:
  - `wallet_identifier` is matched against incoming SMS `receiver_phone` to link inbound payments to a wallet.
  - `channel_id` indicates which provider/channel is responsible for that wallet and which API key will route inbound notifications.
  - Allocation metadata helps the allocation service choose a wallet appropriate for the requested amount.

Integration notes
- Ownership and scoping: wallets are scoped to `Company` and optionally to a `Channel` so a UI or bot should always call with the correct company API key.
- Race conditions: allocation should be atomic — the service should reserve a wallet record or use DB-level locking to prevent simultaneous allocations of the same wallet.

## 3) Payment Check and Confirm Flow

Overview
- This flow is used by downstream services (for example a betting backend, e-commerce checkout, or a Telegram bot) to verify that an externally recorded payment exists and then to confirm its usage (consuming the payment) when the external flow completes.

Who calls `/payments/check`?
1. A consuming backend (e.g., a game server, e-commerce service, or Telegram bot) calls `/payments/check` when it needs to verify whether an incoming payment can be applied to a pending order.

What `/payments/check` verifies internally
1. Authentication: the caller supplies the company API key and the system scopes matches to `company.id`.
2. Amount and optional payer phone: the service searches for recent `Payment` records within the company that match the requested amount (and currency) and, optionally, the `payer_phone` to narrow matches.
3. Eligibility: the matching service checks that the candidate payment is in a usable state (e.g., `new` or `pending_confirmation`) and not already consumed.
4. Results: the matching service returns a result indicating whether there is a usable match and includes metadata (such as `expires_in`, `amount`, and the `Payment` object when applicable).

When and why `/payments/confirm` is called
1. After `/payments/check` returns a usable match, the consumer proceeds with its internal order flow (e.g., finalizes a bet or confirms an order). When the consumer decides to consume the payment, it calls `/payments/confirm` with the `payment_id` and `confirm_token` returned earlier (or delivered via previous flow steps).
2. `/payments/confirm` validates the token and the payment state. If valid and pending, the payment is marked as `used` and any reservation/locking is removed.

Step-by-step combined flow
1. Consumer calls `/payments/check` with `amount` and optional `payer_phone`.
2. If a match is found, the response includes metadata and `payment_id` for the matched payment. The consumer may display this info to a user or immediately reserve/lock the matched payment.
3. The consumer completes its internal operation (for example, confirming a bet or completing a checkout). Before finalizing, it calls `/payments/confirm` with `payment_id` and `confirm_token`.
4. On success `/payments/confirm` marks the payment as used and returns success. The consumer then finalizes the external operation.

Possible outcomes
- Success path:
  1. `/payments/check` → returns `match: true` and `payment_id`.
  2. `/payments/confirm` → returns `{ "status": "success", "message": "Payment confirmed" }` and the payment is consumed.
- Failure modes:
  - `/payments/check` returns `match: false` (no usable payment) and the consumer should retry or prompt the user.
  - `/payments/confirm` fails with `404` if the payment is not found or `400` if the token is invalid or the payment cannot be confirmed.

Implementation and integration tips
- Reservation vs confirmation: consumers should avoid claiming funds before `/payments/confirm` succeeds. Use a short reservation window between check and confirm.
- Idempotency: callers may retry confirm calls — the API responds with success if a payment is already `used`.
- Security: the `confirm_token` is a short-lived secret; ensure it is transported securely (HTTPS) and not logged in plaintext.

---

If you want, I can convert these scenarios into sequence diagrams or add example payloads for each step to make integration easier for external teams.