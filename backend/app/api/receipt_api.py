from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..auth.current_user import get_current_user
from ..database.models import User
from ..database.session import get_db
from ..logic.receipt_logic import (
    delete_receipt_logic,
    get_receipt_by_id_logic,
    get_receipts_logic,
    process_receipt,
)
from ..schemas.receipt_schema import Engine

router = APIRouter()


@router.post("/receipt")
async def upload_receipt(
    engine: Engine,
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await process_receipt(
        engine=engine,
        file=file,
        db=db,
        user_id=current_user.id,
    )


@router.get("/receipt/{receipt_id}")
def read_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    receipt = get_receipt_by_id_logic(
        db=db,
        receipt_id=receipt_id,
        user_id=current_user.id,
    )

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
    current_user: User = Depends(get_current_user),
):
    return get_receipts_logic(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )


@router.delete("/receipt/{receipt_id}")
def remove_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = delete_receipt_logic(
        db=db,
        receipt_id=receipt_id,
        user_id=current_user.id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Receipt not found",
        )

    return {"message": "Receipt deleted successfully"}
