import secrets

from fastapi import Header, HTTPException, status

from app.config import settings


async def verify_internal_token(
    x_internal_token: str = Header(
        ...,
        alias="X-Internal-Token"
    )
) -> None:

    if not secrets.compare_digest(
        x_internal_token,
        settings.internal_secret_token
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )