# Authentication Dependencies

This document describes the authentication dependencies used across the API.

## get_current_company

- Reads `X-API-Key` header.
- Resolution order:
  1. Attempt to find a `Channel` where `channel_api_key == X-API-Key` and `Channel.is_active` is true; return the associated `Company` (requires `Company.is_active`).
  2. Fallback to finding a `Company` where `api_key == X-API-Key` and `Company.is_active` is true.
- If neither is found, the dependency raises `HTTPException(status_code=401)`.

Common usage: routes that are scoped to a company, e.g., `/wallets/request`, `/payments/*`.

## get_current_channel

- Reads `channel_api_key` header.
- Returns the `Channel` when `Channel.is_active` is true; otherwise raises `HTTPException(status_code=401)`.

Common usage: when an incoming provider (SMS) needs to be resolved to a specific channel.
