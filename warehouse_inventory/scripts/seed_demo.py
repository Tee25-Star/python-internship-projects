"""Populate the warehouse database with vibrant sample data."""

from __future__ import annotations

import random
from typing import Iterable

from faker import Faker

from warehouse_app.services.inventory_service import InventoryCreate, InventoryService

CATEGORIES = [
    "Electronics",
    "Apparel",
    "Home & Living",
    "Sports",
    "Automotive",
    "Beauty",
    "Industrial",
]

LOCATIONS = [
    "Aisle A1",
    "Aisle B4",
    "Cold Storage",
    "Showroom",
    "Receiving Dock",
    "Packaging Zone",
    "Overflow",
]


def _generate_items(fake: Faker, count: int) -> Iterable[InventoryCreate]:
    seen_skus: set[str] = set()
    for _ in range(count):
        sku = fake.unique.bothify(text="SKU-####-??").upper()
        seen_skus.add(sku)
        category = random.choice(CATEGORIES)
        location = random.choice(LOCATIONS)
        quantity = random.randint(5, 120)
        reorder_level = random.randint(10, 40)
        unit_cost = round(random.uniform(8.0, 350.0), 2)
        yield InventoryCreate(
            sku=sku,
            name=fake.catch_phrase(),
            category=category,
            quantity=quantity,
            reorder_level=reorder_level,
            location=location,
            unit_cost=unit_cost,
            description=fake.paragraph(nb_sentences=2),
            image_url=f"https://source.unsplash.com/random/400x300?sig={sku}&{category}",
        )


def seed(count: int = 40) -> None:
    """Seed the database with demo data if empty."""
    service = InventoryService()
    if service.list_items():
        print("Inventory already populated; skipping seed.")
        return
    fake = Faker()
    items = list(_generate_items(fake, count))
    service.bulk_upsert(items)
    print(f"Seeded {len(items)} stylish inventory items.")


if __name__ == "__main__":
    seed()

