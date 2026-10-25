

import logging
import secrets
from typing import Annotated

from fastapi import HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader

from app.config import settings
from app.rate_limit import RateLimiter

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

failed_logins = RateLimiter(
    max_attempts=settings.max_failed_logins,
    window_seconds=settings.failed_login_window_seconds,
)


def require_api_key(
    request: Request,
    api_key: Annotated[str | None, Security(api_key_header)],
) -> None:
    client_ip = request.client.host if request.client else "unknown"

    if failed_logins.is_blocked(client_ip):
        logger.warning("blocked client after too many failed attempts", extra={"client_ip": client_ip})
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts, try again later",
            headers={"Retry-After": str(settings.failed_login_window_seconds)},
        )

    if api_key is None or not secrets.compare_digest(
        api_key.encode(), settings.api_key.encode()
    ):
        failed_logins.register(client_ip)
        logger.warning("rejected request with invalid or missing api key", extra={"client_ip": client_ip})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )