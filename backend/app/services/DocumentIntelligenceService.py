from typing import Callable, TypeVar
import time

from azure.core.exceptions import (
    HttpResponseError,
    ServiceRequestError,
    ServiceResponseError,
)

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from ..settings import settings
from ..schemas.receipt_schema import ReceiptAnalysis, ReceiptItem, Source

T = TypeVar("T")


class DocumentIntelligenceService:

    def __init__(self):
        self.endpoint = settings.DOCUMENT_INTELLIGENCE_ENDPOINT
        self.key = settings.DOCUMENT_INTELLIGENCE_API_KEY
        self.client = None

    def _get_client(self) -> DocumentIntelligenceClient:
        if self.client is None:
            self.client = DocumentIntelligenceClient(
                endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
            )

        return self.client

    def _retry(
        self,
        operation: Callable[..., T],
        *args,
        max_attempts: int = 3,
        **kwargs,
    ) -> T:
        for attempt in range(1, max_attempts + 1):
            try:
                return operation(*args, **kwargs)

            except (ServiceRequestError, ServiceResponseError) as error:
                if attempt == max_attempts:
                    raise RuntimeError(
                        "Document Intelligence service connection failed"
                    ) from error

                time.sleep(attempt)

            except HttpResponseError as error:
                if error.status_code in [408, 429, 500, 502, 503, 504]:
                    if attempt == max_attempts:
                        raise RuntimeError(
                            "Document Intelligence temporary service error"
                        ) from error

                    time.sleep(attempt)
                    continue

                raise RuntimeError("Document Intelligence request failed") from error

        raise RuntimeError("Retry failed")

    def _receipt_parser(self, receipt) -> ReceiptAnalysis:
        if not receipt or not getattr(receipt, "fields", None):
            return ReceiptAnalysis(source=Source.di)

        total_field = receipt.fields.get("Total")
        items_field = receipt.fields.get("Items")

        items: list[ReceiptItem] = []

        if items_field and items_field.value_array:
            for item in items_field.value_array:
                item_fields = item.value_object or {}
                items.append(
                    ReceiptItem(
                        item_name=self._field_parser(item_fields.get("Description")),
                        item_quantity=self._field_parser(item_fields.get("Quantity")),
                        line_price=self._field_parser(item_fields.get("TotalPrice")),
                    )
                )

        return ReceiptAnalysis(
            source=Source.di,
            merchant_name=self._field_parser(receipt.fields.get("MerchantName")),
            transaction_date=self._field_parser(receipt.fields.get("TransactionDate")),
            tax=self._field_parser(receipt.fields.get("TotalTax")),
            total_price=self._field_parser(total_field),
            currency=(
                total_field.value_currency.currency_code
                if total_field and total_field.value_currency
                else None
            ),
            items=items or None,
        )

    def _field_parser(self, field):
        if field:
            if field.value_string is not None:
                return field.value_string
            if field.value_date is not None:
                return field.value_date
            if field.value_currency is not None:
                return field.value_currency.amount
            if field.value_number is not None:
                return field.value_number
            if field.content is not None:
                return field.content

        return None

    def analyze_receipt(self, sas_url: str) -> ReceiptAnalysis:
        try:
            client = self._get_client()

            poller = self._retry(
                client.begin_analyze_document,
                "prebuilt-receipt",
                AnalyzeDocumentRequest(url_source=sas_url),
            )

            receipts = self._retry(poller.result)

            receipt = receipts.documents[0] if receipts and receipts.documents else None

            return self._receipt_parser(receipt)

        except RuntimeError:
            raise

        except Exception as error:
            raise RuntimeError("Unexpected error while analyzing receipt") from error


document_intelligence_service = DocumentIntelligenceService()
