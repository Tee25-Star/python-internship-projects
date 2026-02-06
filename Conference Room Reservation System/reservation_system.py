"""Core logic for the conference room reservation system."""

import uuid
from datetime import datetime
from typing import Optional

from models import Reservation, Room


class ReservationSystem:
    """Manages rooms and reservations."""

    def __init__(self) -> None:
        self._rooms: dict[str, Room] = {}
        self._reservations: dict[str, Reservation] = {}

    # --- Room management ---

    def add_room(self, name: str, capacity: int, amenities: Optional[list[str]] = None) -> Room:
        """Add a new conference room."""
        room_id = f"R{len(self._rooms) + 1:03d}"
        room = Room(id=room_id, name=name, capacity=capacity, amenities=amenities or [])
        self._rooms[room_id] = room
        return room

    def get_room(self, room_id: str) -> Optional[Room]:
        """Get a room by ID."""
        return self._rooms.get(room_id)

    def list_rooms(self) -> list[Room]:
        """Return all rooms."""
        return list(self._rooms.values())

    # --- Reservation logic ---

    def is_available(self, room_id: str, start: datetime, end: datetime) -> bool:
        """Check if a room is available for the given time range."""
        if room_id not in self._rooms:
            return False
        for res in self._reservations.values():
            if res.room_id == room_id and res.overlaps(start, end):
                return False
        return True

    def get_available_rooms(self, start: datetime, end: datetime) -> list[Room]:
        """Return all rooms available for the given time range."""
        return [r for r in self._rooms.values() if self.is_available(r.id, start, end)]

    def book(
        self,
        room_id: str,
        organizer: str,
        title: str,
        start_time: datetime,
        end_time: datetime,
        attendees: Optional[int] = None,
    ) -> Optional[Reservation]:
        """Book a room. Returns the reservation if successful, None otherwise."""
        if room_id not in self._rooms:
            return None
        if start_time >= end_time:
            return None
        if not self.is_available(room_id, start_time, end_time):
            return None

        room = self._rooms[room_id]
        res_id = str(uuid.uuid4())[:8].upper()
        reservation = Reservation(
            id=res_id,
            room_id=room_id,
            room_name=room.name,
            organizer=organizer,
            title=title,
            start_time=start_time,
            end_time=end_time,
            attendees=attendees,
        )
        self._reservations[res_id] = reservation
        return reservation

    def cancel_reservation(self, reservation_id: str) -> bool:
        """Cancel a reservation by ID. Returns True if cancelled."""
        if reservation_id in self._reservations:
            del self._reservations[reservation_id]
            return True
        return False

    def get_reservation(self, reservation_id: str) -> Optional[Reservation]:
        """Get a reservation by ID."""
        return self._reservations.get(reservation_id)

    def list_reservations(
        self, room_id: Optional[str] = None, date: Optional[datetime] = None
    ) -> list[Reservation]:
        """List reservations, optionally filtered by room or date."""
        result = list(self._reservations.values())
        if room_id:
            result = [r for r in result if r.room_id == room_id]
        if date:
            result = [
                r
                for r in result
                if r.start_time.date() == date.date()
            ]
        return sorted(result, key=lambda r: r.start_time)

    def list_all_reservations(self) -> list[Reservation]:
        """List all reservations."""
        return self.list_reservations()
