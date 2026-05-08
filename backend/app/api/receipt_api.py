from fastapi import Depends, UploadFile, APIRouter
from sqlalchemy.orm import Session

from ..schemas.receipt_schema import Engine
from ..logic.receipt_logic import process_receipt
from ..database.session import get_db

router = APIRouter()


@router.post("/receipt")
async def upload_receipt(
    engine: Engine,
    file: UploadFile,
    db: Session = Depends(get_db),
):
    return await process_receipt(engine, file, db)
