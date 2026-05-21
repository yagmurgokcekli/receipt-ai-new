import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from sqlalchemy.orm import Session

from ..database.crud import user_crud
from ..database.models import User
from ..database.session import get_db
from ..settings import settings

security = HTTPBearer()

JWKS_URL = (
    f"https://login.microsoftonline.com/"
    f"{settings.AZURE_TENANT_ID}/discovery/v2.0/keys"
)


def get_signing_key(token: str):
    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")

    jwks = requests.get(JWKS_URL, timeout=10).json()

    for key in jwks["keys"]:
        if key["kid"] == kid:
            return key

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token signing key",
    )


def verify_token(token: str) -> dict:
    key = get_signing_key(token)

    try:
        return jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=settings.AZURE_AUDIENCE,
            issuer=settings.AZURE_ISSUER,
        )
    except Exception as exc:
        print("JWT decode error:", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    payload = verify_token(credentials.credentials)

    azure_oid = payload.get("oid")
    email = (
        payload.get("preferred_username")
        or payload.get("upn")
        or payload.get("unique_name")
    )
    name = payload.get("name")

    if not azure_oid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not contain user id",
        )

    return user_crud.get_or_create_user(
        db=db,
        azure_oid=azure_oid,
        email=email,
        name=name,
    )
