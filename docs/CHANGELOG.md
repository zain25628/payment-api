# Changelog

## Unreleased

- Refactored project into `app/` package with routers/services/repositories.
- Introduced `payment_repository` and `wallet_repository` for DB access.
- Unified configuration using Pydantic settings.
- Added unit tests covering routers, services, repositories, deps, and SMS flows (~27 tests).
- Normalized timestamps to timezone-aware UTC in payment flows.
- Documented architecture and integration flows under `docs/`.

## 0.1.0

- Restructured project into `app/` package with routers, services, and repositories.
- Introduced `payment_repository` and `wallet_repository` with dedicated unit tests.
- Added comprehensive tests for routers, services, repositories, dependencies, and SMS service (≈ 30+ tests).
- Normalized timestamps to timezone-aware UTC in payment and repository logic.
- Documented architecture and API flows under `docs/` (ARCHITECTURE, INDEX, service docs).
- Added Dockerfile + docker-compose for local development.
- Added GitHub Actions CI workflow to run the test suite.
- Implemented centralized logging and global error handling (JSON 500 + validation errors).
- Added `/health/db` endpoint and related tests for health monitoring.

