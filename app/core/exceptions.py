# Refactored by Copilot – Exception Handling

import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

logger = logging.getLogger("payment_gateway")


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global fallback exception handler.
    Logs the error and returns a generic JSON 500 response.
    """
    logger.exception("Unhandled error: %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
