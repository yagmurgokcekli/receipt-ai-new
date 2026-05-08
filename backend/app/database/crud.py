from sqlalchemy.orm import Session

from ..database.models import Receipt, ReceiptAnalysis, ReceiptItem
from ..schemas.receipt_schema import Receipt as ReceiptSchema


def create_receipt(db: Session, receipt_data: ReceiptSchema) -> Receipt:
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
        receipt.analyses.append(_create_analysis(receipt_data.analysis.openai_result))

    db.add(receipt)
    db.commit()
    db.refresh(receipt)

    return receipt


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
