from fastapi import UploadFile, APIRouter

from ..schemas.receipt_schema import Engine
from ..logic.receipt_logic import process_receipt

router = APIRouter()


@router.post("/receipt")
async def upload_receipt(engine: Engine, file: UploadFile):
    return await process_receipt(engine, file)