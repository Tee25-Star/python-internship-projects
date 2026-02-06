"""Data models for the conference room reservation system."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Room:
    """Represents a conference room."""

    id: str
    name: str
    capacity: int
    amenities: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        amenities_str = ", ".join(self.amenities) if self.amenities else "None"
        return f"{self.name} (ID: {self.id}) - Capacity: {self.capacity} | Amenities: {amenities_str}"


@dataclass
class Reservation:
    """Represents a room reservation."""

    id: str
    room_id: str
    room_name: str
    organizer: str
    title: str
    start_time: datetime
    end_time: datetime
    attendees: Optional[int] = None

    def __str__(self) -> str:
        return (
            f"[{self.id}] {self.title} | Room: {self.room_name} | "
            f"{self.start_time.strftime('%Y-%m-%d %H:%M')} - "
            f"{self.end_time.strftime('%H:%M')} | By: {self.organizer}"
        )

    def overlaps(self, start: datetime, end: datetime) -> bool:
        """Check if this reservation overlaps with the given time range."""
        return self.start_time < end and self.end_time > start
