import asyncio

from sqlalchemy.exc import SQLAlchemyError, OperationalError, DBAPIError
from sqlalchemy.orm import Session, selectinload

from ..models import Receipt, ReceiptAnalysis
from ...schemas.receipt_schema import Receipt as ReceiptSchema


def create_receipt(db: Session, receipt_data: ReceiptSchema) -> Receipt:
    try:
        receipt = Receipt(
            filename=receipt_data.filename,
            blob_name=receipt_data.blob.blob_name,
            container_name=receipt_data.blob.container_name,
            engine=receipt_data.engine.value,
        )

        db.add(receipt)
        db.commit()
        db.refresh(receipt)

        return receipt

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

    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Unexpected database-related error: {str(e)}") from e


def get_receipt_by_id(db: Session, receipt_id: int) -> Receipt | None:
    return (
        db.query(Receipt)
        .options(selectinload(Receipt.analyses).selectinload(ReceiptAnalysis.items))
        .filter(Receipt.id == receipt_id)
        .first()
    )


def get_receipts(db: Session, skip: int = 0, limit: int = 100) -> list[Receipt]:
    return (
        db.query(Receipt)
        .options(selectinload(Receipt.analyses).selectinload(ReceiptAnalysis.items))
        .order_by(Receipt.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def delete_receipt(db: Session, receipt_id: int) -> bool:
    try:
        receipt = get_receipt_by_id(db, receipt_id)

        if receipt is None:
            return False

        db.delete(receipt)
        db.commit()

        return True

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
