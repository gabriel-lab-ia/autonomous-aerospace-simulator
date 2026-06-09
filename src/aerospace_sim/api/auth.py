from __future__ import annotations

import os
import secrets

from dotenv import load_dotenv
from fastapi import Header, HTTPException, status


load_dotenv()


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    configured_key = os.getenv("AEROSPACE_API_KEY")
    if not configured_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API authentication is not configured.",
        )
    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key.",
        )
    if not secrets.compare_digest(x_api_key, configured_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )
