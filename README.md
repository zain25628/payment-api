# Project README

Current version: **0.1.0**

## تشغيل بيئة التطوير على ويندوز (زر واحد)

الطريقة المدعومة لبدء كامل بيئة التطوير (PostgreSQL + migrations + seed + API) هي تشغيل السكрипت `dev_start_stack.ps1` من PowerShell داخل مجلد المشروع.

نفّذ الأوامر التالية بالضبط في نافذة PowerShell:

```powershell
cd "C:\Users\zaink\OneDrive\Desktop\api"
.\venv\Scripts\Activate.ps1
.\dev_start_stack.ps1
```

ماذا يفعل السكрипت:
- يشغّل PostgreSQL باستخدام `pg_ctl` (وليس خدمة ويندوز)
- ينفّذ هجرات Alembic: `alembic upgrade head`
- يشغّل الـ seeder التطويري: `python -m app.seed_dev_data` (يضمن وجود شركة تجريبية، قناة، ومحفظة اختبار)
- يشغّل الخادم: `uvicorn app.main:app --reload` على `http://127.0.0.1:8000`

> ملاحظة: قد تحتاج لتشغيل PowerShell بامتيازات المدير (Run as Administrator) إن تطلب تشغيل `pg_ctl` صلاحيات أعلى للوصول إلى دليل البيانات.

### اختبار سريع

- افتح المتصفح وتوجّه إلى:

```
http://127.0.0.1:8000/docs
```

- مثال لاستدعاء endpoint للحصول على محفظة متاحة (`POST /wallets/request`):

Headers:

```
X-API-Key: test-key-123
Content-Type: application/json
```

JSON body:

```json
{
  "amount": 25.0
}
```

الاستجابة المتوقعة في حالة وجود محفظة:

```json
{
  "wallet_id": 45,
  "wallet_identifier": "+15557654321",
  "channel_id": 3
}
```

--------------------------------------------------

If you need the script to run without elevation or using Docker instead, let me know and I can add alternative instructions.
## Project Overview

- This project is a **Payment Gateway API** built with FastAPI.
- Core domain concepts:
  - **Company / Channel**: who is calling the API and through which integration.
  - **Wallet**: account/number used to receive payments with daily usage limits.
  - **Payment**: normalized representation of an incoming payment (e.g. via SMS).
- Key API endpoints:
  - `GET /health`  health check.
  - `POST /incoming-sms`  receive and normalize inbound payment SMS.
  - `POST /wallets/request`  request an available wallet for a given amount.
  - `POST /payments/match` and `POST /payments/{id}/confirm-usage`  payment matching/confirmation flows.

## Project Structure (high level)

```
app/
  routers/         # FastAPI endpoints (health, incoming-sms, wallets, payments)
  services/        # Domain services (payment_service, wallet_service, sms_service)
  repositories/    # Data access (payment_repository, wallet_repository)
  models/          # SQLAlchemy ORM models (Company, Channel, Wallet, Payment)
  db/              # DB base + session
  dependencies/    # Authentication helpers (X-API-Key, channel_api_key)
docs/
  INDEX.md         # Documentation index
  ARCHITECTURE.md  # System architecture overview
  ...              # API and domain-specific docs
tests/
  ...              # Unit tests for routers, services, repositories, deps
```

## Getting Started

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Apply database migrations (example):

```bash
alembic upgrade head
```

4. Run the API in development mode:

```bash
uvicorn app.main:app --reload
```

## Running Tests

To run the full test suite:

```bash
pytest -q
```

## Documentation

* See `docs/INDEX.md` for a list of more detailed documents:

  * API flows
  * Integration scenarios
  * Services and repositories
  * Architecture overview
