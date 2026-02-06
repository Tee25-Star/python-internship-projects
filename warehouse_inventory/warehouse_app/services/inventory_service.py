"""Service layer orchestrating inventory operations."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Iterable, Optional

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from warehouse_app.data.database import get_session, init_db
from warehouse_app.data.models import Base, InventoryItem
from warehouse_app.data.repository import InventoryRepository, RepositoryError


@dataclass(slots=True)
class InventoryCreate:
    """Payload for creating inventory entries."""

    sku: str
    name: str
    category: str
    quantity: int
    reorder_level: int
    location: str
    unit_cost: float
    description: str = ""
    image_url: str = ""


@dataclass(slots=True)
class InventoryUpdate:
    """Payload for editing inventory entries."""

    name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = None
    reorder_level: Optional[int] = None
    location: Optional[str] = None
    unit_cost: Optional[float] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

    def to_updates(self) -> dict:
        """Return only provided fields to avoid overwriting with None."""
        return {field: value for field, value in asdict(self).items() if value is not None}


@dataclass(slots=True)
class InventoryDTO:
    """Normalized representation of inventory items for the UI."""

    id: int
    sku: str
    name: str
    category: str
    quantity: int
    reorder_level: int
    location: str
    unit_cost: float
    description: str
    image_url: str
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class InventorySummary:
    """Aggregated metrics for the dashboard."""

    total_sku: int = 0
    total_quantity: int = 0
    inventory_value: float = 0.0
    low_stock_count: int = 0


class InventoryService:
    """Coordinates repository calls and domain rules."""

    def __init__(self, repository: InventoryRepository | None = None) -> None:
        init_db(Base.metadata)
        self._repository = repository or InventoryRepository(get_session)

    def list_items(self) -> list[InventoryDTO]:
        """Return all inventory items."""
        try:
            items = self._repository.list_items()
        except SQLAlchemyError as exc:  # pragma: no cover - defensive
            raise RepositoryError("Unable to load inventory items.") from exc
        return [self._to_dto(item) for item in items]

    def search_items(self, query: str) -> list[InventoryDTO]:
        """Search across SKU, name, category, and location."""
        if not query:
            return self.list_items()
        return [self._to_dto(item) for item in self._repository.search(query)]

    def create_item(self, payload: InventoryCreate) -> InventoryDTO:
        """Persist a new inventory item."""
        try:
            item = self._repository.create_item(**asdict(payload))
        except IntegrityError as exc:
            raise RepositoryError("SKU already exists. Please choose a unique SKU.") from exc
        except SQLAlchemyError as exc:
            raise RepositoryError("Unable to create inventory item.") from exc
        return self._to_dto(item)

    def update_item(self, item_id: int, payload: InventoryUpdate) -> InventoryDTO:
        """Update an item with new details."""
        updates = payload.to_updates()
        if not updates:
            raise RepositoryError("No updates were provided.")
        try:
            item = self._repository.update_item(item_id, **updates)
        except SQLAlchemyError as exc:
            raise RepositoryError("Unable to update inventory item.") from exc
        return self._to_dto(item)

    def adjust_stock(self, item_id: int, delta: int) -> InventoryDTO:
        """Increment or decrement the stock level."""
        try:
            item = self._repository.adjust_stock(item_id, delta)
        except SQLAlchemyError as exc:
            raise RepositoryError("Unable to adjust stock.") from exc
        return self._to_dto(item)

    def delete_item(self, item_id: int) -> None:
        """Remove an item permanently."""
        try:
            self._repository.delete_item(item_id)
        except SQLAlchemyError as exc:
            raise RepositoryError("Unable to delete inventory item.") from exc

    def low_stock_items(self) -> list[InventoryDTO]:
        """Return items with quantity at or below their reorder point."""
        try:
            low_stock = self._repository.low_stock_items()
        except SQLAlchemyError as exc:
            raise RepositoryError("Unable to load low stock items.") from exc
        return [self._to_dto(item) for item in low_stock]

    def summary(self) -> InventorySummary:
        """Compute dashboard metrics."""
        try:
            totals = self._repository.inventory_totals()
            low_stock = self._repository.low_stock_items()
        except SQLAlchemyError as exc:
            raise RepositoryError("Unable to calculate inventory summary.") from exc
        return InventorySummary(
            total_sku=totals["total_sku"],
            total_quantity=totals["total_quantity"],
            inventory_value=totals["inventory_value"],
            low_stock_count=len(low_stock),
        )

    def bulk_upsert(self, records: Iterable[InventoryCreate]) -> list[InventoryDTO]:
        """Insert or update many items in one go."""
        raw_records = [asdict(record) for record in records]
        try:
            items = self._repository.bulk_upsert(raw_records)
        except SQLAlchemyError as exc:
            raise RepositoryError("Bulk import failed.") from exc
        return [self._to_dto(item) for item in items]

    @staticmethod
    def _to_dto(item: InventoryItem) -> InventoryDTO:
        """Convert ORM entity to DTO."""
        return InventoryDTO(
            id=item.id,
            sku=item.sku,
            name=item.name,
            category=item.category,
            quantity=item.quantity,
            reorder_level=item.reorder_level,
            location=item.location,
            unit_cost=item.unit_cost,
            description=item.description,
            image_url=item.image_url,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

