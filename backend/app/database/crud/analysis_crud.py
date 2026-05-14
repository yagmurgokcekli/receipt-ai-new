import asyncio

from sqlalchemy.exc import SQLAlchemyError, OperationalError, DBAPIError
from sqlalchemy.orm import Session

from ..models import ReceiptAnalysis, ReceiptItem


def create_analysis(
    db: Session,
    receipt_id: int,
    analysis_data,
) -> ReceiptAnalysis:
    try:
        analysis = ReceiptAnalysis(
            receipt_id=receipt_id,
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

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        return analysis

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


def create_receipt_analyses(
    db: Session,
    receipt_id: int,
    analysis_result,
):
    analyses = []

    if analysis_result.di_result is not None:
        analyses.append(create_analysis(db, receipt_id, analysis_result.di_result))

    if analysis_result.openai_result is not None:
        analyses.append(create_analysis(db, receipt_id, analysis_result.openai_result))


def get_analyses_by_receipt_id(
    db: Session,
    receipt_id: int,
) -> list[ReceiptAnalysis]:
    return (
        db.query(ReceiptAnalysis).filter(ReceiptAnalysis.receipt_id == receipt_id).all()
    )


def get_analysis_by_id(
    db: Session,
    analysis_id: int,
) -> ReceiptAnalysis | None:
    return db.get(ReceiptAnalysis, analysis_id)
