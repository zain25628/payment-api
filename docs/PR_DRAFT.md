# PR Draft

**Title:** Refactor API into layered architecture (routers/services/repositories) + tests & docs

## Summary

This PR refactors the project into a layered architecture and improves test coverage, DevOps, and observability. Key goals were clarity of responsibilities (routers → services → repositories), safer DB access, and improved docs/tests. The work in this PR covers multiple phases: core refactor, DevOps (Docker + CI), and observability (logging + error handling + health checks).

## Changes

- Move application code under `app/` with clear subpackages.
- Add `payment_repository` and `wallet_repository` to centralize ORM queries.
- Introduce typed services in `app/services/` and keep router signatures stable.
- Unify configuration using `app/config.py` and Pydantic settings patterns.
- Add tests for routers, services, repositories, deps, and sms handling.
- Make payment timestamps timezone-aware (UTC).
- Add documentation under `docs/` including `ARCHITECTURE.md` and `sms_service.md`.
 - Add Dockerfile and `docker-compose.yml` for local development and testing.
 - Add `dev_help.ps1` helper to simplify common developer workflows.
 - Add GitHub Actions CI workflow to run the test suite automatically.
 - Add centralized logging config and a global exception handler returning JSON 500 responses.
 - Add `/health/db` endpoint to check database connectivity and related tests for health and error handling.

## Testing

Run the test suite locally:

```bash
python -m pytest -q
```

Current status: `34 passed` (see changelog/test report). The test suite includes new tests for logging/error handling and health endpoints.

## Risks / Notes

- Migrations and production environment configuration must be verified before deployment.
- The refactor preserves public function signatures; behavior is covered by tests but please validate in staging.

