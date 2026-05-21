from datetime import date, datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    azure_oid: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    receipts: Mapped[list["Receipt"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Receipt(Base):
    __tablename__ = "receipts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    filename: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    blob_name: Mapped[str]
    container_name: Mapped[str]
    engine: Mapped[str]
    user: Mapped["User"] = relationship(back_populates="receipts")
    analyses: Mapped[list["ReceiptAnalysis"]] = relationship(
        back_populates="receipt",
        cascade="all, delete-orphan",
    )


class ReceiptAnalysis(Base):
    __tablename__ = "receipt_analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    receipt_id: Mapped[int] = mapped_column(ForeignKey("receipts.id"))
    source: Mapped[str]
    merchant_name: Mapped[str | None]
    transaction_date: Mapped[date | None]
    tax: Mapped[float | None]
    total_price: Mapped[float | None]
    currency: Mapped[str | None]
    receipt: Mapped["Receipt"] = relationship(back_populates="analyses")
    items: Mapped[list["ReceiptItem"]] = relationship(
        back_populates="analysis",
        cascade="all, delete-orphan",
    )


class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("receipt_analyses.id"))
    item_name: Mapped[str | None]
    item_quantity: Mapped[float | None]
    line_price: Mapped[float | None]
    analysis: Mapped["ReceiptAnalysis"] = relationship(back_populates="items")
