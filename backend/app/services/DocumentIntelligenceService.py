from typing import List

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from ..settings import settings
from ..schemas.receipt_schema import ReceiptAnalysis, ReceiptItem


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

    def _receipt_parser(self, receipt) -> ReceiptAnalysis:
        if not receipt:
            return ReceiptAnalysis(
                merchant_name=None,
                transaction_date=None,
                tax=None,
                total_price=None,
                currency=None,
                items=None,
            )

        merchant_name = self._field_parser(receipt.fields.get("MerchantName"))
        transaction_date = self._field_parser(receipt.fields.get("TransactionDate"))
        tax = self._field_parser(receipt.fields.get("TotalTax"))

        total_field = receipt.fields.get("Total")
        total = self._field_parser(total_field)
        currency = (
            total_field.value_currency.currency_code
            if total_field and total_field.value_currency
            else None
        )

        items: List[ReceiptItem] = []
        if receipt.fields.get("Items"):
            for item in receipt.fields.get("Items").value_array:
                item_description = self._field_parser(
                    item.value_object.get("Description")
                )
                item_quantity = self._field_parser(item.value_object.get("Quantity"))
                item_total_price = self._field_parser(
                    item.value_object.get("TotalPrice")
                )

                items.append(
                    ReceiptItem(
                        item_name=item_description,
                        item_quantity=item_quantity,
                        line_price=item_total_price,
                    )
                )

        return ReceiptAnalysis(
            merchant_name=merchant_name,
            transaction_date=transaction_date,
            tax=tax,
            total_price=total,
            currency=currency,
            items=items or None,
        )

    def _field_parser(self, field):
        if field:
            if field.value_string is not None:
                return field.value_string
            elif field.value_date is not None:
                return field.value_date
            elif field.value_currency is not None:
                return field.value_currency.amount
            elif field.value_number is not None:
                return field.value_number
            elif field.content is not None:
                return field.content

        return None

    def analyze_receipt(self, sas_url: str) -> ReceiptAnalysis:

        client = self._get_client()
        poller = client.begin_analyze_document(
            "prebuilt-receipt", AnalyzeDocumentRequest(url_source=sas_url)
        )
        receipts = poller.result()

        receipt = receipts.documents[0] if receipts and receipts.documents else None

        return self._receipt_parser(receipt)


document_intelligence_service = DocumentIntelligenceService()
