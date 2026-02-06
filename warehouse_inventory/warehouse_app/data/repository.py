"""Inventory repository wrapping SQLAlchemy persistence."""

from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Callable, Iterable, Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from warehouse_app.data.models import InventoryItem


class RepositoryError(RuntimeError):
    """Raised when an unexpected persistence-layer issue occurs."""


class InventoryRepository:
    """Encapsulates CRUD and query logic for inventory data."""

    def __init__(self, session_factory: Callable[[], AbstractContextManager[Session]]) -> None:
        self._session_factory = session_factory

    def list_items(self) -> list[InventoryItem]:
        """Return all items ordered by name."""
        with self._session_factory() as session:
            return list(session.scalars(select(InventoryItem).order_by(InventoryItem.name)))

    def get_item(self, item_id: int) -> InventoryItem | None:
        """Fetch a single item by primary key."""
        with self._session_factory() as session:
            return session.get(InventoryItem, item_id)

    def get_item_by_sku(self, sku: str) -> InventoryItem | None:
        """Fetch an item by SKU."""
        with self._session_factory() as session:
            stmt = select(InventoryItem).where(InventoryItem.sku == sku)
            return session.scalars(stmt).first()

    def create_item(self, **data) -> InventoryItem:
        """Persist a new inventory item."""
        with self._session_factory() as session:
            item = InventoryItem(**data)
            session.add(item)
            session.flush()
            session.refresh(item)
            return item

    def update_item(self, item_id: int, **updates) -> InventoryItem:
        """Update an existing inventory item."""
        with self._session_factory() as session:
            item = session.get(InventoryItem, item_id)
            if item is None:
                raise RepositoryError(f"Inventory item {item_id} not found.")
            for field, value in updates.items():
                if hasattr(item, field):
                    setattr(item, field, value)
            session.add(item)
            session.flush()
            session.refresh(item)
            return item

    def delete_item(self, item_id: int) -> None:
        """Remove an inventory item."""
        with self._session_factory() as session:
            item = session.get(InventoryItem, item_id)
            if item is None:
                raise RepositoryError(f"Inventory item {item_id} not found.")
            session.delete(item)
            session.flush()

    def adjust_stock(self, item_id: int, delta: int) -> InventoryItem:
        """Increment or decrement stock by delta."""
        with self._session_factory() as session:
            item = session.get(InventoryItem, item_id)
            if item is None:
                raise RepositoryError(f"Inventory item {item_id} not found.")
            new_quantity = item.quantity + delta
            if new_quantity < 0:
                raise RepositoryError("Cannot reduce stock below zero.")
            item.quantity = new_quantity
            session.add(item)
            session.flush()
            session.refresh(item)
            return item

    def search(self, query: str) -> list[InventoryItem]:
        """Perform a fuzzy search across key fields."""
        like_value = f"%{query.lower()}%"
        with self._session_factory() as session:
            stmt = select(InventoryItem).where(
                or_(
                    func.lower(InventoryItem.name).like(like_value),
                    func.lower(InventoryItem.sku).like(like_value),
                    func.lower(InventoryItem.category).like(like_value),
                    func.lower(InventoryItem.location).like(like_value),
                )
            )
            return list(session.scalars(stmt))

    def low_stock_items(self) -> list[InventoryItem]:
        """Return items where quantity <= reorder level."""
        with self._session_factory() as session:
            stmt = select(InventoryItem).where(InventoryItem.quantity <= InventoryItem.reorder_level)
            return list(session.scalars(stmt))

    def bulk_upsert(self, items: Iterable[dict]) -> Sequence[InventoryItem]:
        """Insert or update many items in a single transaction."""
        with self._session_factory() as session:
            persisted: list[InventoryItem] = []
            for data in items:
                sku = data.get("sku")
                if not sku:
                    raise RepositoryError("Bulk upsert requires SKU for each item.")
                existing = session.scalars(select(InventoryItem).where(InventoryItem.sku == sku)).first()
                if existing:
                    for field, value in data.items():
                        if hasattr(existing, field):
                            setattr(existing, field, value)
                    persisted.append(existing)
                else:
                    item = InventoryItem(**data)
                    session.add(item)
                    persisted.append(item)
            session.flush()
            for item in persisted:
                session.refresh(item)
            return persisted

    def inventory_totals(self) -> dict[str, float]:
        """Aggregate headline metrics for the dashboard."""
        with self._session_factory() as session:
            stmt = select(
                func.count(InventoryItem.id),
                func.sum(InventoryItem.quantity),
                func.sum(InventoryItem.quantity * InventoryItem.unit_cost),
            )
            count, total_qty, total_value = session.execute(stmt).one()
            return {
                "total_sku": int(count or 0),
                "total_quantity": int(total_qty or 0),
                "inventory_value": float(total_value or 0.0),
            }

