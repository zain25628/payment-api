# System Architecture

## Overview

This project follows a layered architecture to keep responsibilities clear and testable.

Layers:
- API: FastAPI routers expose HTTP endpoints.
- Services: Domain logic and orchestration (e.g. `payment_service`, `wallet_service`).
- Repositories: DB access & ORM queries (e.g. `payment_repository`, `wallet_repository`).
- Database: SQLAlchemy models and Alembic migrations.

## Core Domain Components
- Company
- Channel
- Wallet
- Payment

## Typical flow examples
- Incoming SMS flow:
  `/incoming-sms` → `sms_service` → `payment_service` → `payment_repository` → `Payment` table

- Wallet request flow:
  `/wallets/request` → `wallet_service` → `wallet_repository` → `Wallet` table

- Payments flow:
  `/payments/*` → `payment_service` → `payment_repository`

## Testing strategy
- Routers: tested with FastAPI TestClient and dependency overrides.
- Services: unit tests that mock repositories or use lightweight fakes.
- Repositories: tested using SQLite in-memory engines.

## Notes
- Repositories centralize ORM queries so services remain focused on domain rules.
- Timestamps are stored as timezone-aware UTC datetimes where applicable.

## Authentication & Authorization

The project exposes helper dependencies that resolve authentication context for requests:

- `deps.get_current_company` — resolves the `Company` associated with the request (e.g. by API key / header).
- `deps.get_current_channel` — resolves the `Channel` associated with the request (for integration calls).

Headers in use:

- `X-API-Key` — used to authenticate a company-level API key where applicable.
- `channel_api_key` — used for provider integrations (e.g. incoming SMS providers) to identify an active `Channel`.

These dependencies populate the request context and are used by routers (incoming integrations and internal endpoints) to ensure requests are associated with the correct company and channel.

## External Integrations

Integrations are modeled as external callers posting to endpoints which are handled by service-layer parsers. Example:

- SMS Provider → `/incoming-sms` → `sms_service.parse_incoming_sms` → `sms_service.store_payment` → `payment_service.create_payment_from_sms` → `payment_repository`

## Logging & Error Handling

Application-wide logging is configured via `app/core/logging_config.py`. A global exception handler (`app/core/exceptions.py`) is registered in `app/main.py` to produce consistent JSON 500 responses and to log unexpected errors. Validation errors are handled to return structured JSON containing the `detail` list of issues.

## Health & Monitoring

The service exposes an additional DB health endpoint:

- `GET /health/db` — lightweight connectivity check that attempts a trivial query against the configured DB and returns `{"status": "ok", "database": "reachable"}` or `{"status": "error", "database": "unreachable"}` when the DB is not reachable.

