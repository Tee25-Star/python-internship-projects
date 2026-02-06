# -*- coding: utf-8 -*-
"""Conference Room Reservation System - CLI."""

from datetime import datetime
from typing import Optional

from reservation_system import ReservationSystem


def parse_datetime(date_str: str, time_str: str) -> Optional[datetime]:
    """Parse date (YYYY-MM-DD) and time (HH:MM) into datetime."""
    try:
        return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        return None


def print_header(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)


def setup_sample_data(system: ReservationSystem) -> None:
    """Add sample rooms and optionally a demo reservation."""
    if system.list_rooms():
        return  # already has rooms
    system.add_room("Boardroom A", 12, ["Projector", "Whiteboard", "Video Conference"])
    system.add_room("Boardroom B", 8, ["Projector", "Whiteboard"])
    system.add_room("Meeting Room 1", 6, ["TV", "Whiteboard"])
    system.add_room("Meeting Room 2", 4, ["Whiteboard"])
    system.add_room("Small Huddle", 3, [])
    print("  Sample rooms added (Boardroom A/B, Meeting 1/2, Small Huddle).")


def main() -> None:
    system = ReservationSystem()
    setup_sample_data(system)

    while True:
        print_header("Conference Room Reservation System")
        print("  1. View all rooms")
        print("  2. Add a room")
        print("  3. Check availability")
        print("  4. Book a room")
        print("  5. View reservations")
        print("  6. Cancel a reservation")
        print("  0. Exit")
        print("-" * 50)
        choice = input("Select an option: ").strip()

        if choice == "0":
            print("\nGoodbye!")
            break

        if choice == "1":
            print_header("All Rooms")
            rooms = system.list_rooms()
            if not rooms:
                print("  No rooms yet. Add some from the menu.")
            else:
                for r in rooms:
                    print(f"  � {r}")

        elif choice == "2":
            print_header("Add a Room")
            name = input("Room name: ").strip()
            if not name:
                print("  Name cannot be empty.")
                continue
            try:
                cap = int(input("Capacity: ").strip())
            except ValueError:
                print("  Invalid capacity.")
                continue
            amenities = input("Amenities (comma-separated, or leave blank): ").strip()
            am_list = [a.strip() for a in amenities.split(",") if a.strip()]
            room = system.add_room(name, cap, am_list)
            print(f"  Added: {room}")

        elif choice == "3":
            print_header("Check Availability")
            date_str = input("Date (YYYY-MM-DD): ").strip()
            time_start = input("Start time (HH:MM): ").strip()
            time_end = input("End time (HH:MM): ").strip()
            start = parse_datetime(date_str, time_start)
            end = parse_datetime(date_str, time_end)
            if start is None or end is None:
                print("  Invalid date or time. Use YYYY-MM-DD and HH:MM.")
                continue
            if start >= end:
                print("  End must be after start.")
                continue
            available = system.get_available_rooms(start, end)
            if not available:
                print("  No rooms available for that period.")
            else:
                print(f"  Available rooms ({len(available)}):")
                for r in available:
                    print(f"    � {r}")

        elif choice == "4":
            print_header("Book a Room")
            rooms = system.list_rooms()
            if not rooms:
                print("  No rooms. Add rooms first.")
                continue
            print("Rooms:")
            for r in rooms:
                print(f"  {r.id}: {r.name}")
            room_id = input("Room ID (e.g. R001): ").strip()
            organizer = input("Organizer name: ").strip()
            title = input("Meeting title: ").strip()
            date_str = input("Date (YYYY-MM-DD): ").strip()
            time_start = input("Start time (HH:MM): ").strip()
            time_end = input("End time (HH:MM): ").strip()
            start = parse_datetime(date_str, time_start)
            end = parse_datetime(date_str, time_end)
            if start is None or end is None:
                print("  Invalid date or time.")
                continue
            if start >= end:
                print("  End must be after start.")
                continue
            att = input("Number of attendees (optional, press Enter to skip): ").strip()
            attendees = int(att) if att.isdigit() else None
            res = system.book(room_id, organizer, title, start, end, attendees)
            if res:
                print(f"  Booked! Reservation ID: {res.id}")
                print(f"  {res}")
            else:
                print("  Booking failed. Room may be taken or invalid.")

        elif choice == "5":
            print_header("Reservations")
            filters = input("Filter by room ID or date (YYYY-MM-DD)? Leave blank for all: ").strip()
            room_id = None
            date = None
            if filters:
                if filters.upper().startswith("R"):
                    room_id = filters
                else:
                    try:
                        date = datetime.strptime(filters, "%Y-%m-%d")
                    except ValueError:
                        pass
            reservations = system.list_reservations(room_id=room_id, date=date)
            if not reservations:
                print("  No reservations match.")
            else:
                for r in reservations:
                    print(f"  - {r}")

        elif choice == "6":
            print_header("Cancel Reservation")
            res_id = input("Reservation ID: ").strip()
            if system.cancel_reservation(res_id):
                print("  Reservation cancelled.")
            else:
                print("  Reservation not found.")

        else:
            print("  Invalid option. Try again.")


if __name__ == "__main__":
    main()
