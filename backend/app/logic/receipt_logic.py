import asyncio
from fastapi import UploadFile
from sqlalchemy.orm import Session

from ..services.BlobStorageService import blob_storage_service
from ..services.DocumentIntelligenceService import document_intelligence_service
from ..services.OpenAIService import openai_service
from ..schemas.receipt_schema import Engine, Receipt, AnalysisResult
from ..database.crud import receipt_crud, analysis_crud
from ..database.models import Receipt as ReceiptModel


async def process_receipt(
    engine: Engine, file: UploadFile, db: Session
) -> ReceiptModel | None:
    blob = blob_storage_service.save_to_blob(await file.read())
    analysis = await analyze_receipt(engine, blob.sas_url)

    receipt_response = Receipt(
        filename=file.filename,
        blob=blob,
        engine=engine,
        analysis=analysis,
    )

    created_receipt = receipt_crud.create_receipt(
        db=db,
        receipt_data=receipt_response,
    )

    analysis_crud.create_receipt_analyses(
        db=db,
        receipt_id=created_receipt.id,
        analysis_result=analysis,
    )

    return receipt_crud.get_receipt_by_id(
        db=db,
        receipt_id=created_receipt.id,
    )


async def analyze_receipt(engine: Engine, sas_url: str) -> AnalysisResult:
    if engine == Engine.di:
        return AnalysisResult(
            di_result=document_intelligence_service.analyze_receipt(sas_url)
        )

    elif engine == Engine.openai:
        return AnalysisResult(openai_result=openai_service.analyze_receipt(sas_url))

    elif engine == Engine.compare:
        di_result, openai_result = await asyncio.gather(
            asyncio.to_thread(
                document_intelligence_service.analyze_receipt,
                sas_url,
            ),
            asyncio.to_thread(
                openai_service.analyze_receipt,
                sas_url,
            ),
        )
        return AnalysisResult(
            di_result=di_result,
            openai_result=openai_result,
        )

    raise ValueError(f"Unsupported engine: {engine}")


def get_receipt_by_id_logic(db: Session, receipt_id: int):
    return receipt_crud.get_receipt_by_id(db, receipt_id)


def get_receipts_logic(db: Session, skip: int = 0, limit: int = 100):
    return receipt_crud.get_receipts(db, skip, limit)


def delete_receipt_logic(db: Session, receipt_id: int) -> bool:
    return receipt_crud.delete_receipt(db, receipt_id)
