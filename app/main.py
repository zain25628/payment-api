# Refactored by Copilot
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
import logging

from app.core.logging_config import setup_logging
from app.core.exceptions import unhandled_exception_handler
from app.routers import health, incoming_sms, wallets, payments

# Configure logging early
setup_logging()

app = FastAPI(title="Payment Gateway API")

# Register global exception handlers
logger = logging.getLogger("payment_gateway")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return await unhandled_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Log a concise validation message
    logger.info("Validation error on %s %s: %s", request.method, request.url.path, exc.errors())
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


app.include_router(health.router)
app.include_router(incoming_sms.router)
app.include_router(wallets.router)
app.include_router(payments.router)


@app.get("/")
def read_root():
    logger.info("Application startup")
    return {"message": "Welcome to the Payment Gateway API"}
