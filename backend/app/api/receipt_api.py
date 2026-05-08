from fastapi import Depends, HTTPException, UploadFile, APIRouter
from sqlalchemy.orm import Session

from ..schemas.receipt_schema import Engine
from ..logic.receipt_logic import process_receipt
from ..database.session import get_db
from ..database.crud import (
    get_receipt_by_id,
    get_receipts,
    delete_receipt,
)

router = APIRouter()


@router.post("/receipt")
async def upload_receipt(
    engine: Engine,
    file: UploadFile,
    db: Session = Depends(get_db),
):
    return await process_receipt(engine, file, db)


@router.get("/receipt/{receipt_id}")
def read_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
):
    receipt = get_receipt_by_id(db, receipt_id)

    if receipt is None:
        raise HTTPException(
            status_code=404,
            detail="Receipt not found",
        )

    return receipt


@router.get("/receipts")
def read_receipts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return get_receipts(db, skip, limit)


@router.delete("/receipt/{receipt_id}")
def remove_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
):
    deleted = delete_receipt(db, receipt_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Receipt not found",
        )

    return {"message": "Receipt deleted successfully"}
