from fastapi import UploadFile
from ..services.BlobStorageService import blob_storage_service
from ..schemas.receipt_schema import Engine


async def process_receipt(engine: Engine, file: UploadFile):

    blob = await save_to_blob(file)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "blob": blob,
        "engine": engine,
    }


async def save_to_blob(file: UploadFile):
    sonuc = await blob_storage_service.save_to_blob(await file.read())
    return sonuc
