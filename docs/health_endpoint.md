# Health Endpoint

## Purpose
The `/health` endpoint is a lightweight HTTP endpoint intended for monitoring and uptime checks. It allows load balancers, monitoring systems, and uptime services to validate that the application process is running and to observe the current service name and version.

## Request
- Method: `GET`
- Path: `/health`

## Response
- Content-Type: `application/json`
- Schema:
  - `status`: string — should be `"ok"` when the service is healthy
  - `service`: string — the service name (from configuration)
  - `version`: string — the service version (from configuration)

### Example
Request:
```http
GET /health HTTP/1.1
Host: example.local:8000
```

Response:
```json
{
  "status": "ok",
  "service": "Payment Gateway API",
  "version": "1.0.0"
}
```

## Usage
- Configure your monitoring system to perform a `GET` to `/health` at a suitable interval.
- Treat any non-200 response or a body where `status` is not `"ok"` as a failed health check.
- This endpoint is intentionally minimal — for more detailed diagnostics, create dedicated telemetry endpoints.
