from fastapi import UploadFile
from ..services.BlobStorageService import blob_storage_service
from ..schemas.receipt_schema import Engine, Receipt


async def process_receipt(engine: Engine, file: UploadFile) -> Receipt:
    blob = await save_to_blob(file)

    return Receipt(
        filename=file.filename,
        content_type=file.content_type,
        sas_url=blob["sas_url"],
        engine=engine,
    )


async def save_to_blob(file: UploadFile):
    sonuc = await blob_storage_service.save_to_blob(await file.read())
    return sonuc
