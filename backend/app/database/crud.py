from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..database.models import Receipt, ReceiptAnalysis, ReceiptItem
from ..schemas.receipt_schema import Receipt as ReceiptSchema


def create_receipt(db: Session, receipt_data: ReceiptSchema) -> Receipt:
    try:
        receipt = Receipt(
            filename=receipt_data.filename,
            blob_name=receipt_data.blob.blob_name,
            container_name=receipt_data.blob.container_name,
            engine=receipt_data.engine.value,
            analyses=[],
        )

        if receipt_data.analysis.di_result is not None:
            receipt.analyses.append(_create_analysis(receipt_data.analysis.di_result))

        if receipt_data.analysis.openai_result is not None:
            receipt.analyses.append(
                _create_analysis(receipt_data.analysis.openai_result)
            )

        db.add(receipt)
        db.commit()
        db.refresh(receipt)

        return receipt

    except SQLAlchemyError as e:
        db.rollback()
        raise RuntimeError(f"Database operation failed: {str(e)}") from e


def _create_analysis(analysis_data) -> ReceiptAnalysis:
    return ReceiptAnalysis(
        source=analysis_data.source.value,
        merchant_name=analysis_data.merchant_name,
        transaction_date=analysis_data.transaction_date,
        tax=analysis_data.tax,
        total_price=analysis_data.total_price,
        currency=analysis_data.currency,
        items=[
            ReceiptItem(
                item_name=item.item_name,
                item_quantity=item.item_quantity,
                line_price=item.line_price,
            )
            for item in (analysis_data.items or [])
        ],
    )


def get_receipt_by_id(db: Session, receipt_id: int) -> Receipt | None:
    return db.query(Receipt).filter(Receipt.id == receipt_id).first()


def get_receipts(db: Session, skip: int = 0, limit: int = 100) -> list[Receipt]:
    return db.query(Receipt).order_by(Receipt.id).offset(skip).limit(limit).all()


def delete_receipt(db: Session, receipt_id: int) -> bool:
    try:
        receipt = get_receipt_by_id(db, receipt_id)

        if receipt is None:
            return False

        db.delete(receipt)
        db.commit()

        return True

    except SQLAlchemyError as e:
        db.rollback()
        raise RuntimeError("Database operation failed") from e
