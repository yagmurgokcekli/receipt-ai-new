from fastapi import UploadFile
from ..services.BlobStorageService import blob_storage_service
from ..services.DocumentIntelligenceService import document_intelligence_service
from ..services.OpenAIService import openai_service
from ..schemas.receipt_schema import Engine, Receipt


async def process_receipt(engine: Engine, file: UploadFile) -> Receipt:
    blob = await save_to_blob(file)
    analysis_list = analyze_receipt(engine, blob["sas_url"])

    return Receipt(
        filename=blob["blob_name"],
        blob_url=blob["blob_url"],
        engine=engine,
        analysis=analysis_list,
    )


async def save_to_blob(file: UploadFile):
    return await blob_storage_service.save_to_blob(await file.read())


def analyze_receipt(engine: Engine, sas_url: str):
    if engine == Engine.di:
        return [document_intelligence_service.analyze_receipt(sas_url)]

    elif engine == Engine.openai:
        return [openai_service.analyze_receipt(sas_url)]

    elif engine == Engine.compare:
        di_analysis = document_intelligence_service.analyze_receipt(sas_url)
        openai_analysis = openai_service.analyze_receipt(sas_url)

        return [di_analysis, openai_analysis]

    raise ValueError(f"Unsupported engine: {engine}")
