import asyncio
from fastapi import UploadFile

from ..services.BlobStorageService import blob_storage_service
from ..services.DocumentIntelligenceService import document_intelligence_service
from ..services.OpenAIService import openai_service
from ..schemas.receipt_schema import Engine, Receipt, AnalysisResult


async def process_receipt(engine: Engine, file: UploadFile) -> Receipt:
    blob = blob_storage_service.save_to_blob(await file.read())
    analysis = await analyze_receipt(engine, blob.sas_url)

    return Receipt(
        blob=blob,
        engine=engine,
        analysis=analysis,
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
