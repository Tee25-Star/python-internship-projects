"""
Local Events Calendar (Desktop App)
----------------------------------
Standalone Tkinter/ttk app with a modern-looking interface:
- Add / Edit / Delete events
- Search + filter (date range + category)
- Persistent storage (local JSON next to this script)
- Export to .ics (calendar file)
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass, asdict
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Iterable, Optional

import tkinter as tk
from tkinter import ttk, messagebox, filedialog


APP_TITLE = "Local Events Calendar"
DATA_FILE = Path(__file__).with_name("local_events_calendar_events.json")

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^\d{2}:\d{2}$")

CATEGORIES = [
    "Community",
    "Music",
    "Sports",
    "Food",
    "Arts",
    "Education",
    "Family",
    "Networking",
    "Other",
]


def _parse_date(s: str) -> date:
    s = s.strip()
    if not s:
        raise ValueError("Date is required.")
    if not DATE_RE.match(s):
        raise ValueError("Date must be in YYYY-MM-DD format.")
    return datetime.strptime(s, "%Y-%m-%d").date()


def _parse_time(s: str, label: str) -> time:
    s = s.strip()
    if not s:
        raise ValueError(f"{label} time is required.")
    if not TIME_RE.match(s):
        raise ValueError(f"{label} time must be in HH:MM (24h) format.")
    return datetime.strptime(s, "%H:%M").time()


def _safe(s: str) -> str:
    return (s or "").strip()


def _now_local() -> datetime:
    # naive local datetime (good enough for this simple app)
    return datetime.now()


@dataclass(frozen=True)
class Event:
    id: str
    title: str
    event_date: str  # YYYY-MM-DD
    start_time: str  # HH:MM
    end_time: str  # HH:MM
    location: str
    category: str
    description: str

    def starts_at(self) -> datetime:
        d = datetime.strptime(self.event_date, "%Y-%m-%d").date()
        t = datetime.strptime(self.start_time, "%H:%M").time()
        return datetime.combine(d, t)

    def ends_at(self) -> datetime:
        d = datetime.strptime(self.event_date, "%Y-%m-%d").date()
        t = datetime.strptime(self.end_time, "%H:%M").time()
        return datetime.combine(d, t)


class EventStore:
    def __init__(self, path: Path):
        self.path = path
        self.events: list[Event] = []

    def load(self) -> None:
        if not self.path.exists():
            self.events = []
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(raw, list):
                raise ValueError("Invalid data format.")
            events: list[Event] = []
            for item in raw:
                if not isinstance(item, dict):
                    continue
                # best-effort load
                events.append(
                    Event(
                        id=str(item.get("id") or uuid.uuid4()),
                        title=str(item.get("title") or "").strip(),
                        event_date=str(item.get("event_date") or "").strip(),
                        start_time=str(item.get("start_time") or "").strip(),
                        end_time=str(item.get("end_time") or "").strip(),
                        location=str(item.get("location") or "").strip(),
                        category=str(item.get("category") or "Other").strip() or "Other",
                        description=str(item.get("description") or "").strip(),
                    )
                )
            self.events = [e for e in events if e.title and e.event_date and e.start_time and e.end_time]
            self.events.sort(key=lambda e: (e.event_date, e.start_time, e.title.lower()))
        except Exception:
            messagebox.showwarning(
                APP_TITLE,
                f"Couldn't read saved data from:\n{self.path}\n\nStarting with an empty calendar.",
            )
            self.events = []

    def save(self) -> None:
        payload = [asdict(e) for e in self.events]
        self.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def upsert(self, event: Event) -> None:
        idx = next((i for i, e in enumerate(self.events) if e.id == event.id), None)
        if idx is None:
            self.events.append(event)
        else:
            self.events[idx] = event
        self.events.sort(key=lambda e: (e.event_date, e.start_time, e.title.lower()))
        self.save()

    def delete(self, event_id: str) -> None:
        self.events = [e for e in self.events if e.id != event_id]
        self.save()


class GradientHeader(tk.Canvas):
    def __init__(self, master: tk.Misc, height: int = 78, **kwargs):
        super().__init__(master, height=height, highlightthickness=0, **kwargs)
        self._from = "#6D28D9"  # violet
        self._to = "#06B6D4"  # cyan
        self._title = APP_TITLE
        self._subtitle = "Plan, discover, and track what’s happening near you."
        self.bind("<Configure>", lambda _e: self._redraw())
        self._redraw()

    @staticmethod
    def _hex_to_rgb(h: str) -> tuple[int, int, int]:
        h = h.lstrip("#")
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    @staticmethod
    def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
        r, g, b = rgb
        return f"#{r:02x}{g:02x}{b:02x}"

    def _redraw(self) -> None:
        self.delete("all")
        w = max(1, self.winfo_width())
        h = max(1, self.winfo_height())

        r1, g1, b1 = self._hex_to_rgb(self._from)
        r2, g2, b2 = self._hex_to_rgb(self._to)
        steps = max(32, min(220, w // 6))
        for i in range(steps):
            t = i / max(1, steps - 1)
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            x0 = int(w * i / steps)
            x1 = int(w * (i + 1) / steps) + 1
            self.create_rectangle(x0, 0, x1, h, outline="", fill=self._rgb_to_hex((r, g, b)))

        # subtle diagonal "shine"
        self.create_polygon(
            0,
            0,
            int(w * 0.55),
            0,
            int(w * 0.30),
            h,
            0,
            h,
            outline="",
            fill="#ffffff",
            stipple="gray12",
        )

        self.create_text(
            20,
            22,
            anchor="w",
            text=self._title,
            fill="white",
            font=("Segoe UI", 18, "bold"),
        )
        self.create_text(
            20,
            52,
            anchor="w",
            text=self._subtitle,
            fill="#EAF2FF",
            font=("Segoe UI", 10),
        )


class EventDialog(tk.Toplevel):
    def __init__(
        self,
        master: tk.Misc,
        *,
        title: str,
        initial: Optional[Event] = None,
    ):
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.result: Optional[Event] = None

        pad = 12
        self.configure(bg="#0b1020")

        container = ttk.Frame(self, padding=pad, style="Card.TFrame")
        container.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Fields
        self.var_title = tk.StringVar(value=initial.title if initial else "")
        self.var_date = tk.StringVar(value=initial.event_date if initial else date.today().strftime("%Y-%m-%d"))
        now = _now_local()
        default_start = (now + timedelta(minutes=30)).strftime("%H:%M")
        default_end = (now + timedelta(minutes=90)).strftime("%H:%M")
        self.var_start = tk.StringVar(value=initial.start_time if initial else default_start)
        self.var_end = tk.StringVar(value=initial.end_time if initial else default_end)
        self.var_location = tk.StringVar(value=initial.location if initial else "")
        self.var_category = tk.StringVar(value=initial.category if initial else "Community")
        self.var_desc = tk.StringVar(value=initial.description if initial else "")

        form = ttk.Frame(container, style="Card.TFrame")
        form.grid(row=0, column=0, sticky="nsew")

        def label(text: str, r: int, c: int) -> None:
            ttk.Label(form, text=text, style="FormLabel.TLabel").grid(row=r, column=c, sticky="w", pady=(0, 6))

        label("Event title", 0, 0)
        e_title = ttk.Entry(form, textvariable=self.var_title, width=44, style="Modern.TEntry")
        e_title.grid(row=1, column=0, columnspan=2, sticky="we", pady=(0, 10))

        label("Date (YYYY-MM-DD)", 2, 0)
        label("Category", 2, 1)
        e_date = ttk.Entry(form, textvariable=self.var_date, width=20, style="Modern.TEntry")
        e_date.grid(row=3, column=0, sticky="we", pady=(0, 10), padx=(0, 10))
        cb_cat = ttk.Combobox(form, textvariable=self.var_category, values=CATEGORIES, state="readonly", width=22)
        cb_cat.grid(row=3, column=1, sticky="we", pady=(0, 10))

        label("Start time (HH:MM)", 4, 0)
        label("End time (HH:MM)", 4, 1)
        e_start = ttk.Entry(form, textvariable=self.var_start, width=20, style="Modern.TEntry")
        e_start.grid(row=5, column=0, sticky="we", pady=(0, 10), padx=(0, 10))
        e_end = ttk.Entry(form, textvariable=self.var_end, width=20, style="Modern.TEntry")
        e_end.grid(row=5, column=1, sticky="we", pady=(0, 10))

        label("Location", 6, 0)
        e_loc = ttk.Entry(form, textvariable=self.var_location, width=44, style="Modern.TEntry")
        e_loc.grid(row=7, column=0, columnspan=2, sticky="we", pady=(0, 10))

        label("Description (optional)", 8, 0)
        self.txt_desc = tk.Text(form, height=5, width=52, bg="#0f172a", fg="#e5e7eb", insertbackground="#e5e7eb")
        self.txt_desc.grid(row=9, column=0, columnspan=2, sticky="we")
        if initial and initial.description:
            self.txt_desc.insert("1.0", initial.description)

        # Help row
        help_row = ttk.Frame(container, style="Card.TFrame")
        help_row.grid(row=1, column=0, sticky="we", pady=(12, 0))
        ttk.Label(
            help_row,
            text="Tip: Use 24-hour time. Example: 18:30",
            style="Hint.TLabel",
        ).grid(row=0, column=0, sticky="w")

        # Actions
        actions = ttk.Frame(container, style="Card.TFrame")
        actions.grid(row=2, column=0, sticky="e", pady=(12, 0))
        btn_cancel = ttk.Button(actions, text="Cancel", command=self._cancel, style="Secondary.TButton")
        btn_cancel.grid(row=0, column=0, padx=(0, 10))
        btn_save = ttk.Button(actions, text="Save event", command=lambda: self._save(initial), style="Accent.TButton")
        btn_save.grid(row=0, column=1)

        # Enter focus
        e_title.focus_set()
        self.bind("<Escape>", lambda _e: self._cancel())
        self.bind("<Return>", lambda _e: self._save(initial))

        # Size & center
        self.update_idletasks()
        self._center_over(master)

    def _center_over(self, master: tk.Misc) -> None:
        try:
            mx = master.winfo_rootx()
            my = master.winfo_rooty()
            mw = master.winfo_width()
            mh = master.winfo_height()
            w = self.winfo_width()
            h = self.winfo_height()
            x = mx + (mw - w) // 2
            y = my + (mh - h) // 2
            self.geometry(f"+{max(20, x)}+{max(20, y)}")
        except Exception:
            pass

    def _cancel(self) -> None:
        self.result = None
        self.destroy()

    def _save(self, initial: Optional[Event]) -> None:
        try:
            title = _safe(self.var_title.get())
            if not title:
                raise ValueError("Event title is required.")

            d = _parse_date(self.var_date.get())
            st = _parse_time(self.var_start.get(), "Start")
            et = _parse_time(self.var_end.get(), "End")
            if datetime.combine(d, et) <= datetime.combine(d, st):
                raise ValueError("End time must be after start time.")

            category = _safe(self.var_category.get()) or "Other"
            if category not in CATEGORIES:
                category = "Other"

            location = _safe(self.var_location.get())
            desc = _safe(self.txt_desc.get("1.0", "end").strip())

            self.result = Event(
                id=(initial.id if initial else str(uuid.uuid4())),
                title=title,
                event_date=d.strftime("%Y-%m-%d"),
                start_time=st.strftime("%H:%M"),
                end_time=et.strftime("%H:%M"),
                location=location,
                category=category,
                description=desc,
            )
            self.destroy()
        except Exception as e:
            messagebox.showerror(APP_TITLE, str(e), parent=self)


class App(ttk.Frame):
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self.master.title(APP_TITLE)
        self.master.minsize(1100, 650)
        self.master.configure(bg="#0b1020")

        self.store = EventStore(DATA_FILE)
        self.store.load()
        if not self.store.events:
            self._seed_demo_events()

        self._configure_styles()

        self.grid(row=0, column=0, sticky="nsew")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)

        # Header
        self.header = GradientHeader(self, height=82, bg="#111827")
        self.header.grid(row=0, column=0, columnspan=2, sticky="we")

        # Sidebar
        self.sidebar = ttk.Frame(self, style="Side.TFrame", padding=(14, 14))
        self.sidebar.grid(row=1, column=0, sticky="ns")
        self.sidebar.columnconfigure(0, weight=1)

        ttk.Label(self.sidebar, text="Navigate", style="SideTitle.TLabel").grid(row=0, column=0, sticky="w")

        self.btn_home = ttk.Button(self.sidebar, text="Events", command=self._show_events, style="Side.TButton")
        self.btn_home.grid(row=1, column=0, sticky="we", pady=(10, 8))
        self.btn_add = ttk.Button(self.sidebar, text="Add event", command=self._add_event, style="Accent.TButton")
        self.btn_add.grid(row=2, column=0, sticky="we", pady=(0, 8))
        self.btn_about = ttk.Button(self.sidebar, text="About", command=self._show_about, style="Side.TButton")
        self.btn_about.grid(row=3, column=0, sticky="we")

        ttk.Separator(self.sidebar).grid(row=4, column=0, sticky="we", pady=14)

        self.stats_today = ttk.Label(self.sidebar, text="", style="StatBig.TLabel")
        self.stats_today.grid(row=5, column=0, sticky="w")
        self.stats_week = ttk.Label(self.sidebar, text="", style="StatSmall.TLabel")
        self.stats_week.grid(row=6, column=0, sticky="w", pady=(6, 0))
        self.stats_total = ttk.Label(self.sidebar, text="", style="StatSmall.TLabel")
        self.stats_total.grid(row=7, column=0, sticky="w", pady=(6, 0))

        ttk.Separator(self.sidebar).grid(row=8, column=0, sticky="we", pady=14)

        self.btn_export = ttk.Button(self.sidebar, text="Export .ics", command=self._export_ics, style="Secondary.TButton")
        self.btn_export.grid(row=9, column=0, sticky="we", pady=(0, 8))
        self.btn_open_data = ttk.Button(
            self.sidebar,
            text="Open data file",
            command=self._reveal_data_path,
            style="Secondary.TButton",
        )
        self.btn_open_data.grid(row=10, column=0, sticky="we")

        # Content
        self.content = ttk.Frame(self, style="Main.TFrame", padding=(16, 14))
        self.content.grid(row=1, column=1, sticky="nsew")
        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)

        # Pages
        self.page_events = ttk.Frame(self.content, style="Main.TFrame")
        self.page_about = ttk.Frame(self.content, style="Main.TFrame")

        for p in (self.page_events, self.page_about):
            p.grid(row=0, column=0, sticky="nsew")

        self.content.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)

        self._build_events_page()
        self._build_about_page()
        self._show_events()
        self._refresh_stats()
        self._refresh_tree()

    def _configure_styles(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Base palette
        bg = "#0b1020"
        panel = "#0f172a"
        panel2 = "#111827"
        text = "#e5e7eb"
        muted = "#a7b0bf"
        accent = "#22c55e"  # green
        accent2 = "#8b5cf6"  # purple
        danger = "#ef4444"

        style.configure(".", background=bg, foreground=text, font=("Segoe UI", 10))
        style.configure("Main.TFrame", background=bg)
        style.configure("Side.TFrame", background=panel2)

        style.configure("SideTitle.TLabel", background=panel2, foreground="#c7d2fe", font=("Segoe UI", 11, "bold"))
        style.configure("StatBig.TLabel", background=panel2, foreground="#ffffff", font=("Segoe UI", 14, "bold"))
        style.configure("StatSmall.TLabel", background=panel2, foreground=muted, font=("Segoe UI", 10))

        style.configure("Card.TFrame", background=panel, relief="flat")
        style.configure("CardTitle.TLabel", background=panel, foreground="#ffffff", font=("Segoe UI", 12, "bold"))
        style.configure("Hint.TLabel", background=panel, foreground=muted, font=("Segoe UI", 9))
        style.configure("FormLabel.TLabel", background=panel, foreground="#cbd5e1", font=("Segoe UI", 9, "bold"))

        style.configure("Modern.TEntry", fieldbackground="#0f172a", background="#0f172a", foreground=text)

        # Buttons
        style.configure("Side.TButton", padding=(10, 8), background=panel2, foreground=text)
        style.map("Side.TButton", background=[("active", "#1f2937")])

        style.configure("Accent.TButton", padding=(10, 8), background=accent, foreground="#06210f", font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#16a34a")])

        style.configure("Secondary.TButton", padding=(10, 8), background="#334155", foreground=text)
        style.map("Secondary.TButton", background=[("active", "#475569")])

        style.configure("Danger.TButton", padding=(10, 8), background=danger, foreground="#ffffff", font=("Segoe UI", 10, "bold"))
        style.map("Danger.TButton", background=[("active", "#dc2626")])

        # Treeview
        style.configure(
            "Modern.Treeview",
            background=panel,
            fieldbackground=panel,
            foreground=text,
            bordercolor=panel,
            borderwidth=0,
            rowheight=28,
        )
        style.configure("Modern.Treeview.Heading", background=panel2, foreground="#e2e8f0", font=("Segoe UI", 10, "bold"))
        style.map("Modern.Treeview", background=[("selected", "#1f2a44")], foreground=[("selected", "#ffffff")])

        # Combobox
        style.configure("TCombobox", fieldbackground=panel, background=panel, foreground=text)

        # Small visual accent for separators
        style.configure("TSeparator", background="#1f2937")

        # Store palette for quick access
        self._palette = {
            "bg": bg,
            "panel": panel,
            "panel2": panel2,
            "text": text,
            "muted": muted,
            "accent": accent,
            "accent2": accent2,
        }

    def _seed_demo_events(self) -> None:
        # Demo data (only on first run when no saved events exist)
        today = date.today()
        demo = [
            Event(
                id=str(uuid.uuid4()),
                title="Community Cleanup @ Riverside Park",
                event_date=(today + timedelta(days=1)).strftime("%Y-%m-%d"),
                start_time="09:00",
                end_time="11:30",
                location="Riverside Park",
                category="Community",
                description="Meet at the main gate. Gloves & bags provided. Bring water!",
            ),
            Event(
                id=str(uuid.uuid4()),
                title="Local Food Truck Night",
                event_date=(today + timedelta(days=2)).strftime("%Y-%m-%d"),
                start_time="17:30",
                end_time="21:00",
                location="Downtown Square",
                category="Food",
                description="Live DJ set, family-friendly. Try the new vendors!",
            ),
            Event(
                id=str(uuid.uuid4()),
                title="Open Mic: Poetry & Stories",
                event_date=(today + timedelta(days=4)).strftime("%Y-%m-%d"),
                start_time="19:00",
                end_time="21:00",
                location="Cedar Street Cafe",
                category="Arts",
                description="Sign-up starts at 6:30pm. 5 minutes per performer.",
            ),
        ]
        self.store.events = demo
        self.store.save()

    def _build_events_page(self) -> None:
        self.page_events.columnconfigure(0, weight=1)
        self.page_events.rowconfigure(2, weight=1)

        # Top "cards"
        cards = ttk.Frame(self.page_events, style="Main.TFrame")
        cards.grid(row=0, column=0, sticky="we")
        for i in range(3):
            cards.columnconfigure(i, weight=1, uniform="cards")

        self.card_1 = self._make_card(cards, "Upcoming (7 days)", "0 events", 0)
        self.card_2 = self._make_card(cards, "Happening today", "0 events", 1)
        self.card_3 = self._make_card(cards, "Categories", "0 types", 2)

        # Filter bar
        filter_bar = ttk.Frame(self.page_events, style="Card.TFrame", padding=(12, 12))
        filter_bar.grid(row=1, column=0, sticky="we", pady=(14, 12))
        for i in range(10):
            filter_bar.columnconfigure(i, weight=0)
        filter_bar.columnconfigure(1, weight=1)

        ttk.Label(filter_bar, text="Search", style="FormLabel.TLabel").grid(row=0, column=0, sticky="w")
        self.var_search = tk.StringVar()
        self.ent_search = ttk.Entry(filter_bar, textvariable=self.var_search, style="Modern.TEntry")
        self.ent_search.grid(row=0, column=1, sticky="we", padx=(8, 12))

        ttk.Label(filter_bar, text="From", style="FormLabel.TLabel").grid(row=0, column=2, sticky="w")
        self.var_from = tk.StringVar()
        self.ent_from = ttk.Entry(filter_bar, textvariable=self.var_from, width=12, style="Modern.TEntry")
        self.ent_from.grid(row=0, column=3, sticky="w", padx=(8, 12))

        ttk.Label(filter_bar, text="To", style="FormLabel.TLabel").grid(row=0, column=4, sticky="w")
        self.var_to = tk.StringVar()
        self.ent_to = ttk.Entry(filter_bar, textvariable=self.var_to, width=12, style="Modern.TEntry")
        self.ent_to.grid(row=0, column=5, sticky="w", padx=(8, 12))

        ttk.Label(filter_bar, text="Category", style="FormLabel.TLabel").grid(row=0, column=6, sticky="w")
        self.var_cat = tk.StringVar(value="All")
        self.cb_filter_cat = ttk.Combobox(
            filter_bar,
            textvariable=self.var_cat,
            values=["All"] + CATEGORIES,
            state="readonly",
            width=16,
        )
        self.cb_filter_cat.grid(row=0, column=7, sticky="w", padx=(8, 12))

        btn_apply = ttk.Button(filter_bar, text="Apply", command=self._refresh_tree, style="Accent.TButton")
        btn_apply.grid(row=0, column=8, sticky="e", padx=(0, 10))
        btn_clear = ttk.Button(filter_bar, text="Clear", command=self._clear_filters, style="Secondary.TButton")
        btn_clear.grid(row=0, column=9, sticky="e")

        # Result table
        table_wrap = ttk.Frame(self.page_events, style="Card.TFrame", padding=(10, 10))
        table_wrap.grid(row=2, column=0, sticky="nsew")
        table_wrap.rowconfigure(1, weight=1)
        table_wrap.columnconfigure(0, weight=1)

        title_row = ttk.Frame(table_wrap, style="Card.TFrame")
        title_row.grid(row=0, column=0, sticky="we", pady=(0, 8))
        ttk.Label(title_row, text="Events", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")

        actions = ttk.Frame(title_row, style="Card.TFrame")
        actions.grid(row=0, column=1, sticky="e")
        ttk.Button(actions, text="Add", command=self._add_event, style="Accent.TButton").grid(row=0, column=0, padx=(0, 8))
        ttk.Button(actions, text="Edit", command=self._edit_selected, style="Secondary.TButton").grid(row=0, column=1, padx=(0, 8))
        ttk.Button(actions, text="Delete", command=self._delete_selected, style="Danger.TButton").grid(row=0, column=2)

        cols = ("date", "time", "title", "location", "category")
        self.tree = ttk.Treeview(table_wrap, columns=cols, show="headings", style="Modern.Treeview", selectmode="browse")
        self.tree.grid(row=1, column=0, sticky="nsew")

        self.tree.heading("date", text="Date")
        self.tree.heading("time", text="Time")
        self.tree.heading("title", text="Title")
        self.tree.heading("location", text="Location")
        self.tree.heading("category", text="Category")

        self.tree.column("date", width=110, anchor="w")
        self.tree.column("time", width=110, anchor="w")
        self.tree.column("title", width=360, anchor="w")
        self.tree.column("location", width=250, anchor="w")
        self.tree.column("category", width=140, anchor="w")

        yscroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=1, column=1, sticky="ns")

        # Footer hint
        hint = ttk.Label(
            table_wrap,
            text="Double-click an event to edit. Data saves automatically.",
            style="Hint.TLabel",
        )
        hint.grid(row=2, column=0, sticky="w", pady=(8, 0))

        self.tree.bind("<Double-1>", lambda _e: self._edit_selected())
        self.ent_search.bind("<Return>", lambda _e: self._refresh_tree())

    def _build_about_page(self) -> None:
        self.page_about.columnconfigure(0, weight=1)
        card = ttk.Frame(self.page_about, style="Card.TFrame", padding=(18, 16))
        card.grid(row=0, column=0, sticky="nwe")
        ttk.Label(card, text="About", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            card,
            text=(
                "Local Events Calendar is a simple offline organizer.\n\n"
                "- Your events are stored locally in a JSON file next to this script.\n"
                "- Use Export .ics to import your events into Google Calendar / Outlook.\n\n"
                "Made with Python + Tkinter."
            ),
            style="Hint.TLabel",
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(10, 0))

    def _make_card(self, master: ttk.Frame, title: str, value: str, col: int) -> ttk.Frame:
        f = ttk.Frame(master, style="Card.TFrame", padding=(14, 12))
        f.grid(row=0, column=col, sticky="we", padx=(0 if col == 0 else 12, 0))
        ttk.Label(f, text=title, style="Hint.TLabel").grid(row=0, column=0, sticky="w")
        lbl = ttk.Label(f, text=value, style="CardTitle.TLabel")
        lbl.grid(row=1, column=0, sticky="w", pady=(6, 0))
        f._value_label = lbl  # type: ignore[attr-defined]
        return f

    def _set_card_value(self, card: ttk.Frame, text: str) -> None:
        lbl = getattr(card, "_value_label", None)
        if lbl is not None:
            lbl.configure(text=text)

    def _show_events(self) -> None:
        self.page_events.tkraise()

    def _show_about(self) -> None:
        self.page_about.tkraise()

    def _clear_filters(self) -> None:
        self.var_search.set("")
        self.var_from.set("")
        self.var_to.set("")
        self.var_cat.set("All")
        self._refresh_tree()

    def _filtered_events(self) -> list[Event]:
        q = _safe(self.var_search.get()).lower()
        from_s = _safe(self.var_from.get())
        to_s = _safe(self.var_to.get())
        cat = _safe(self.var_cat.get())

        from_d: Optional[date] = None
        to_d: Optional[date] = None
        try:
            if from_s:
                from_d = _parse_date(from_s)
            if to_s:
                to_d = _parse_date(to_s)
        except Exception:
            # if user is typing partial date, don't block; just ignore range until valid
            from_d = None
            to_d = None

        out: list[Event] = []
        for e in self.store.events:
            if cat and cat != "All" and e.category != cat:
                continue
            if q:
                blob = f"{e.title} {e.location} {e.category} {e.description}".lower()
                if q not in blob:
                    continue
            try:
                ed = datetime.strptime(e.event_date, "%Y-%m-%d").date()
            except Exception:
                continue
            if from_d and ed < from_d:
                continue
            if to_d and ed > to_d:
                continue
            out.append(e)
        return out

    def _refresh_stats(self) -> None:
        today = date.today()
        next_week = today + timedelta(days=7)
        today_count = 0
        week_count = 0
        cats = set()
        for e in self.store.events:
            cats.add(e.category)
            try:
                ed = datetime.strptime(e.event_date, "%Y-%m-%d").date()
            except Exception:
                continue
            if ed == today:
                today_count += 1
            if today <= ed <= next_week:
                week_count += 1

        self.stats_today.configure(text=f"{today_count} today")
        self.stats_week.configure(text=f"{week_count} in the next 7 days")
        self.stats_total.configure(text=f"{len(self.store.events)} total events")

        self._set_card_value(self.card_1, f"{week_count} events")
        self._set_card_value(self.card_2, f"{today_count} events")
        self._set_card_value(self.card_3, f"{len(cats)} types")

    def _refresh_tree(self) -> None:
        self._refresh_stats()
        items = self.tree.get_children()
        if items:
            self.tree.delete(*items)

        for e in self._filtered_events():
            time_range = f"{e.start_time}–{e.end_time}"
            self.tree.insert("", "end", iid=e.id, values=(e.event_date, time_range, e.title, e.location, e.category))

    def _get_selected_id(self) -> Optional[str]:
        sel = self.tree.selection()
        return sel[0] if sel else None

    def _get_event(self, event_id: str) -> Optional[Event]:
        for e in self.store.events:
            if e.id == event_id:
                return e
        return None

    def _add_event(self) -> None:
        dlg = EventDialog(self.master, title="Add a local event")
        self.master.wait_window(dlg)
        if dlg.result:
            self.store.upsert(dlg.result)
            self._refresh_tree()

    def _edit_selected(self) -> None:
        event_id = self._get_selected_id()
        if not event_id:
            messagebox.showinfo(APP_TITLE, "Select an event to edit.")
            return
        ev = self._get_event(event_id)
        if not ev:
            messagebox.showwarning(APP_TITLE, "That event no longer exists.")
            self._refresh_tree()
            return
        dlg = EventDialog(self.master, title="Edit event", initial=ev)
        self.master.wait_window(dlg)
        if dlg.result:
            self.store.upsert(dlg.result)
            self._refresh_tree()

    def _delete_selected(self) -> None:
        event_id = self._get_selected_id()
        if not event_id:
            messagebox.showinfo(APP_TITLE, "Select an event to delete.")
            return
        ev = self._get_event(event_id)
        if not ev:
            self._refresh_tree()
            return
        ok = messagebox.askyesno(APP_TITLE, f"Delete this event?\n\n{ev.title}")
        if ok:
            self.store.delete(event_id)
            self._refresh_tree()

    def _export_ics(self) -> None:
        events = self._filtered_events()
        if not events:
            messagebox.showinfo(APP_TITLE, "No events to export (based on your current filters).")
            return
        default_name = f"local-events-{date.today().strftime('%Y%m%d')}.ics"
        out_path = filedialog.asksaveasfilename(
            title="Export events to .ics",
            defaultextension=".ics",
            initialfile=default_name,
            filetypes=[("iCalendar files", "*.ics")],
        )
        if not out_path:
            return
        try:
            ics = self._build_ics(events)
            Path(out_path).write_text(ics, encoding="utf-8")
            messagebox.showinfo(APP_TITLE, f"Exported {len(events)} event(s) to:\n{out_path}")
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Export failed:\n{e}")

    def _build_ics(self, events: Iterable[Event]) -> str:
        # Basic RFC 5545-ish (good enough for most calendar imports)
        def esc(s: str) -> str:
            s = s.replace("\\", "\\\\")
            s = s.replace("\n", "\\n")
            s = s.replace(",", "\\,")
            s = s.replace(";", "\\;")
            return s

        def dt_local(dt: datetime) -> str:
            # floating time (no Z) to keep local-time behavior on import
            return dt.strftime("%Y%m%dT%H%M%S")

        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Local Events Calendar//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
        ]

        now = _now_local().strftime("%Y%m%dT%H%M%S")
        for e in events:
            uid = f"{e.id}@local-events-calendar"
            start = e.starts_at()
            end = e.ends_at()
            lines.extend(
                [
                    "BEGIN:VEVENT",
                    f"UID:{uid}",
                    f"DTSTAMP:{now}",
                    f"DTSTART:{dt_local(start)}",
                    f"DTEND:{dt_local(end)}",
                    f"SUMMARY:{esc(e.title)}",
                    f"LOCATION:{esc(e.location)}",
                    f"CATEGORIES:{esc(e.category)}",
                ]
            )
            if e.description:
                lines.append(f"DESCRIPTION:{esc(e.description)}")
            lines.append("END:VEVENT")

        lines.append("END:VCALENDAR")
        return "\r\n".join(lines) + "\r\n"

    def _reveal_data_path(self) -> None:
        # Minimal: show path; user can copy/paste
        messagebox.showinfo(APP_TITLE, f"Your events are saved here:\n\n{self.store.path}")


def main() -> None:
    root = tk.Tk()
    # On Windows, try to improve scaling a bit for modern displays
    try:
        root.tk.call("tk", "scaling", 1.1)
    except Exception:
        pass
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
