"""SQLAlchemy models for the warehouse application."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base class."""


class InventoryItem(Base):
    """Represents a stock keeping unit within the warehouse."""

    __tablename__ = "inventory_items"
    __table_args__ = (
        UniqueConstraint("sku", name="uq_inventory_sku"),
        Index("idx_inventory_category", "category"),
        Index("idx_inventory_location", "location"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="General")
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reorder_level: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    location: Mapped[str] = mapped_column(String(120), nullable=False, default="Main")
    unit_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    image_url: Mapped[str] = mapped_column(String(300), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:  # pragma: no cover - repr aids debugging
        return (
            f"InventoryItem(id={self.id!r}, sku={self.sku!r}, name={self.name!r}, "
            f"qty={self.quantity!r}, location={self.location!r})"
        )

