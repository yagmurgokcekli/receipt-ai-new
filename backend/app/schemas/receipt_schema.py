from datetime import date
from pydantic import BaseModel, Field
from enum import Enum


class Engine(str, Enum):
    di = "di"
    openai = "openai"
    compare = "compare"


class Source(str, Enum):
    di = "di"
    openai = "openai"


class ReceiptItem(BaseModel):
    item_name: str | None = Field(
        default=None,
        description="Exact line item name or description as printed on the receipt. Do not normalize, translate, or infer.",
    )
    item_quantity: float | None = Field(
        default=None,
        description="Numeric quantity of the item only if it is explicitly shown on the receipt. Return null if quantity is not printed.",
    )
    line_price: float | None = Field(
        default=None,
        description="Total price for this line item, not the unit price unless the receipt explicitly shows only a unit price. Return null if the line price is not clearly visible.",
    )


class ReceiptAnalysis(BaseModel):
    source: Source
    merchant_name: str | None = Field(
        default=None,
        description="Merchant or store name exactly as printed on the receipt. Do not infer brand names, branches, or locations.",
    )
    transaction_date: date | None = Field(
        default=None,
        description="Purchase date shown on the receipt, formatted as YYYY-MM-DD if possible. Return null if the date is missing, unreadable, or cannot be converted confidently.",
    )
    tax: float | None = Field(
        default=None,
        description="Total tax amount applied to the receipt. Return only the numeric value, without currency symbols or text.",
    )
    total_price: float | None = Field(
        default=None,
        description="Grand total amount paid for the receipt. Return the numeric value only, without currency symbols or text.",
    )
    currency: str | None = Field(
        default=None,
        description="Currency code such as TRY, USD, or EUR, derived only from currency symbols or text explicitly visible on the receipt. Return null if the currency is not clearly stated.",
    )
    items: list[ReceiptItem] | None = None


class AnalysisResult(BaseModel):
    di_result: ReceiptAnalysis | None = None
    openai_result: ReceiptAnalysis | None = None


class Blob(BaseModel):
    blob_name: str
    sas_url: str
    container_name: str


class Receipt(BaseModel):
    blob: Blob
    engine: Engine
    analysis: AnalysisResult
