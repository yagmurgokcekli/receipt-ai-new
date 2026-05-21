import asyncio

from sqlalchemy.exc import SQLAlchemyError, OperationalError, DBAPIError
from sqlalchemy.orm import Session

from ..models import User


def get_user_by_azure_oid(db: Session, azure_oid: str) -> User | None:
    return db.query(User).filter(User.azure_oid == azure_oid).first()


def create_user(
    db: Session,
    azure_oid: str,
    email: str | None = None,
    name: str | None = None,
) -> User:
    try:
        user = User(
            azure_oid=azure_oid,
            email=email,
            name=name,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    except (
        SQLAlchemyError,
        OperationalError,
        DBAPIError,
        TimeoutError,
        ConnectionError,
        asyncio.TimeoutError,
    ) as e:
        db.rollback()
        raise RuntimeError(f"Database operation failed: {str(e)}") from e


def get_or_create_user(
    db: Session,
    azure_oid: str,
    email: str | None = None,
    name: str | None = None,
) -> User:
    user = get_user_by_azure_oid(db, azure_oid)

    if user is not None:
        return user

    return create_user(
        db=db,
        azure_oid=azure_oid,
        email=email,
        name=name,
    )
