from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class Engine(str, Enum):
    di = "di"
    openai = "openai"


class ReceiptItem(BaseModel):
    item_name: str = Field(
        description="Exact line item name or description as printed on the receipt. Do not normalize, translate, or infer."
    )
    item_quantity: Optional[float] = Field(
        default=None,
        description="Numeric quantity of the item only if it is explicitly shown on the receipt. Return null if quantity is not printed.",
    )
    line_price: Optional[float] = Field(
        default=None,
        description="Total price for this line item, not the unit price unless the receipt explicitly shows only a unit price. Return null if the line price is not clearly visible.",
    )


class ReceiptAnalysis(BaseModel):
    merchant_name: str = Field(
        description="Merchant or store name exactly as printed on the receipt. Do not infer brand names, branches, or locations."
    )
    transaction_date: Optional[str] = Field(
        default=None,
        description="Purchase date shown on the receipt, formatted as YYYY-MM-DD if possible. Return null if the date is missing, unreadable, or cannot be converted confidently.",
    )
    total_price: float = Field(
        description="Grand total amount paid for the receipt. Return the numeric value only, without currency symbols or text."
    )
    currency: Optional[str] = Field(
        default=None,
        description="Currency code such as TRY, USD, or EUR, derived only from currency symbols or text explicitly visible on the receipt. Return null if the currency is not clearly stated.",
    )


class Receipt(BaseModel):
    filename: Optional[str] = None
    content_type: Optional[str] = None
    sas_url: str 
    engine: Engine
    analysis: Optional[ReceiptAnalysis] = None
    items: Optional[list[ReceiptItem]] = None
