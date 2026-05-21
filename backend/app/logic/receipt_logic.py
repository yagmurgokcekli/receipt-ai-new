import asyncio

from fastapi import UploadFile
from sqlalchemy.orm import Session

from ..database.crud import analysis_crud, receipt_crud
from ..database.models import Receipt as ReceiptModel
from ..schemas.receipt_schema import AnalysisResult, Engine, Receipt
from ..services.BlobStorageService import blob_storage_service
from ..services.DocumentIntelligenceService import document_intelligence_service
from ..services.OpenAIService import openai_service


async def process_receipt(
    engine: Engine,
    file: UploadFile,
    db: Session,
    user_id: int,
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
        user_id=user_id,
    )

    analysis_crud.create_receipt_analyses(
        db=db,
        receipt_id=created_receipt.id,
        analysis_result=analysis,
    )

    return receipt_crud.get_receipt_by_id(
        db=db,
        receipt_id=created_receipt.id,
        user_id=user_id,
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
            asyncio.to_thread(document_intelligence_service.analyze_receipt, sas_url),
            asyncio.to_thread(openai_service.analyze_receipt, sas_url),
        )
        return AnalysisResult(
            di_result=di_result,
            openai_result=openai_result,
        )

    raise ValueError(f"Unsupported engine: {engine}")


def get_receipt_by_id_logic(
    db: Session,
    receipt_id: int,
    user_id: int,
) -> ReceiptModel | None:
    return receipt_crud.get_receipt_by_id(db, receipt_id, user_id)


def get_receipts_logic(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[ReceiptModel]:
    return receipt_crud.get_receipts(db, user_id, skip, limit)


def delete_receipt_logic(
    db: Session,
    receipt_id: int,
    user_id: int,
) -> bool:
    return receipt_crud.delete_receipt(db, receipt_id, user_id)
