# Project Tasks Board

## [PHASE 1] Project Setup
- [x] Create project folders: app/, app/core/, app/db/, app/models/, app/schemas/, app/services/, app/routers/, app/utils/, app/dependencies/
- [x] Create main.py inside /app
- [x] Generate requirements.txt
- [x] Create .env.example
- [x] Generate app/core/config.py
- [x] Generate app/db/base.py, app/db/session.py

## [PHASE 2] Database & Models
- [x] Create Company model
- [x] Create Channel model
- [x] Create Wallet model
- [x] Create Payment model
- [x] Add timestamps (created_at, updated_at)
- [x] Add relationships
- [x] Register models in app/db/base.py

## [PHASE 3] Core Logic & Services
- [x] Generate /app/services/wallet_service.py
- [x] Generate /app/services/payment_service.py
- [x] Generate /app/services/sms_service.py

## [PHASE 4] API Routers
- [x] Generate /app/routers/health.py
- [x] Generate /app/routers/incoming_sms.py
- [x] Generate /app/routers/wallets.py
- [x] Generate /app/routers/payments.py
- [x] Ensure all routers use dependencies (get_db, get_current_company, get_current_channel)

## [PHASE 5] Payment Flow Implementation
- [x] Implement Incoming SMS Logic
- [x] Implement Payment Matching State Machine

## [PHASE 6] Wallet Engine Implementation
- [x] Implement Wallet selection algorithm
- [x] Implement Wallet usage update

## [PHASE 7] Incoming SMS Pipeline
- [x] Implement POST /incoming-sms

## [PHASE 8] Payment Verification Logic
- [x] Implement POST /payments/check

## [PHASE 9] Confirmation Flow (Idempotency)
- [x] Implement POST /payments/confirm

## [PHASE 10] Hosted Payment Page (Optional)
- [x] Generate /pay/{session_id} (if instructed)

## [PHASE 11] Final Review & Cleanup
- [x] Validate folder structure
- [x] Remove unused imports
- [x] Ensure routers registered in main.py
- [x] Ensure models imported in base
- [x] Ensure alembic revision is created
 - [x] Add seed_dev_data.py for local dev seeding

## Dev Environment & Run
- **PostgreSQL**: running on `localhost:5432` (database `payment_gateway`, user `postgres`).
- **To launch development server:**
	- Open PowerShell and run:

```powershell
cd C:\Users\zaink\OneDrive\Desktop\api
.\dev_setup_and_run.ps1
```

This script activates the `venv`, installs dependencies, verifies `DATABASE_URL` is visible to Python, and starts the app with `uvicorn` in reload mode.
