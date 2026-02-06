"""
IT Support Ticketing System
A modern desktop application with a distinctive interface for managing support tickets.
"""

import json
import os
from datetime import datetime
from pathlib import Path

import customtkinter as ctk
from tkinter import messagebox

# ═══════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM - Standout cyberpunk-inspired color palette
# ═══════════════════════════════════════════════════════════════════════════
COLORS = {
    "bg_dark": "#0d1117",           # Deep space black
    "bg_card": "#161b22",           # Elevated surface
    "bg_hover": "#21262d",          # Interactive hover
    "accent_cyan": "#00d4ff",       # Electric cyan - primary actions
    "accent_amber": "#ffb347",      # Warm amber - alerts & highlights
    "accent_mint": "#39d353",       # Success green
    "accent_coral": "#ff7b72",      # Warning/critical
    "accent_violet": "#a371f7",     # Secondary accent
    "text_primary": "#f0f6fc",      # Bright white
    "text_secondary": "#8b949e",    # Muted gray
    "border": "#30363d",            # Subtle borders
}


class Ticket:
    """Represents a single support ticket."""
    def __init__(self, title: str, description: str, category: str, priority: str, 
                 requester: str, ticket_id: str = None, status: str = "Open",
                 created_at: str = None):
        self.id = ticket_id or f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.title = title
        self.description = description
        self.category = category
        self.priority = priority
        self.requester = requester
        self.status = status
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M")
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "priority": self.priority,
            "requester": self.requester,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            title=data["title"],
            description=data["description"],
            category=data["category"],
            priority=data["priority"],
            requester=data["requester"],
            ticket_id=data["id"],
            status=data.get("status", "Open"),
            created_at=data.get("created_at"),
        )


class TicketStorage:
    """Handles persistent storage of tickets."""
    def __init__(self, filepath: str = "tickets.json"):
        self.filepath = Path(__file__).parent / filepath

    def load(self) -> list[Ticket]:
        if not self.filepath.exists():
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Ticket.from_dict(t) for t in data]
        except (json.JSONDecodeError, KeyError):
            return []

    def save(self, tickets: list[Ticket]):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in tickets], f, indent=2)


class TicketCard(ctk.CTkFrame):
    """A visually striking card displaying a single ticket in the list."""
    def __init__(self, master, ticket: Ticket, on_click, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.ticket = ticket
        self.on_click = on_click

        # Main card container with left accent bar
        self.card = ctk.CTkFrame(
            self, 
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            cursor="hand2"
        )
        self.card.pack(fill="x", pady=(0, 8), padx=2)
        self.card.bind("<Button-1>", lambda e: on_click(ticket))
        self.card.bind("<Enter>", self._on_enter)
        self.card.bind("<Leave>", self._on_leave)

        # Left accent strip based on priority
        priority_colors = {
            "Critical": COLORS["accent_coral"],
            "High": COLORS["accent_amber"],
            "Medium": COLORS["accent_cyan"],
            "Low": COLORS["accent_mint"],
        }
        accent_color = priority_colors.get(ticket.priority, COLORS["accent_violet"])

        inner = ctk.CTkFrame(self.card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=14)

        # Accent indicator
        accent = ctk.CTkFrame(inner, width=4, fg_color=accent_color, corner_radius=2)
        accent.pack(side="left", fill="y", padx=(0, 12))

        # Content
        content = ctk.CTkFrame(inner, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True)

        # Title row
        title_label = ctk.CTkLabel(
            content, 
            text=ticket.title[:60] + ("..." if len(ticket.title) > 60 else ""),
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        title_label.pack(anchor="w")
        title_label.bind("<Button-1>", lambda e: on_click(ticket))

        # Meta row
        meta = f"#{ticket.id}  •  {ticket.requester}  •  {ticket.category}  •  {ticket.created_at}"
        meta_label = ctk.CTkLabel(
            content,
            text=meta,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        meta_label.pack(anchor="w")
        meta_label.bind("<Button-1>", lambda e: on_click(ticket))

        # Badges row
        badges_frame = ctk.CTkFrame(content, fg_color="transparent")
        badges_frame.pack(anchor="w", pady=(6, 0))

        status_colors = {
            "Open": COLORS["accent_cyan"],
            "In Progress": COLORS["accent_amber"],
            "Resolved": COLORS["accent_mint"],
            "Closed": COLORS["text_secondary"],
        }
        status_bg = status_colors.get(ticket.status, COLORS["accent_violet"])

        status_badge = ctk.CTkLabel(
            badges_frame,
            text=f"  {ticket.status}  ",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["bg_dark"],
            fg_color=status_bg,
            corner_radius=6,
            padx=8,
            pady=2
        )
        status_badge.pack(side="left", padx=(0, 6))
        status_badge.bind("<Button-1>", lambda e: on_click(ticket))

        priority_badge = ctk.CTkLabel(
            badges_frame,
            text=f"  {ticket.priority}  ",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_primary"],
            fg_color=COLORS["bg_hover"],
            corner_radius=6,
            padx=8,
            pady=2
        )
        priority_badge.pack(side="left")
        priority_badge.bind("<Button-1>", lambda e: on_click(ticket))

        # Propagate click to children
        for child in [self.card, content, title_label, meta_label, badges_frame, status_badge, priority_badge]:
            if hasattr(child, 'bind'):
                child.bind("<Button-1>", lambda e: on_click(ticket))

    def _on_enter(self, event):
        self.card.configure(fg_color=COLORS["bg_hover"], border_color=COLORS["accent_cyan"])

    def _on_leave(self, event):
        self.card.configure(fg_color=COLORS["bg_card"], border_color=COLORS["border"])


class StatCard(ctk.CTkFrame):
    """Dashboard statistics card with icon and value."""
    def __init__(self, master, label: str, value: str, icon: str, accent_color: str, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.card = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["border"],
        )
        self.card.pack(fill="both", expand=True, padx=4, pady=4)

        inner = ctk.CTkFrame(self.card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        # Icon with colored background (use solid color - Tk doesn't support hex alpha)
        icon_frame = ctk.CTkFrame(inner, fg_color=COLORS["bg_hover"], corner_radius=12, width=48, height=48)
        icon_frame.pack(side="left", padx=(0, 16))
        icon_frame.pack_propagate(False)

        icon_label = ctk.CTkLabel(
            icon_frame,
            text=icon,
            font=ctk.CTkFont(size=24),
            text_color=accent_color
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")

        # Value and label
        value_label = ctk.CTkLabel(
            inner,
            text=value,
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        value_label.pack(anchor="w")

        label_ctk = ctk.CTkLabel(
            inner,
            text=label,
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"]
        )
        label_ctk.pack(anchor="w")


class ITSupportApp(ctk.CTk):
    """Main application window."""
    def __init__(self):
        super().__init__()

        self.title("⚡ IT Support Ticketing System")
        self.geometry("1200x780")
        self.minsize(900, 600)

        # Apply standout theme
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=COLORS["bg_dark"])

        self.storage = TicketStorage()
        self.tickets: list[Ticket] = self.storage.load()
        self.selected_ticket: Ticket | None = None

        self._build_ui()

    def _build_ui(self):
        # Main container
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=24, pady=24)

        # ═══ HEADER ═══
        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(fill="x", pady=(0, 24))

        # Logo / Title area
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="⚡ HELPDESK",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color=COLORS["accent_cyan"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="IT Support Ticketing System",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w")

        # New Ticket button - prominent CTA
        self.new_btn = ctk.CTkButton(
            header,
            text="  ＋  New Ticket",
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=COLORS["accent_cyan"],
            hover_color="#00a8cc",
            text_color=COLORS["bg_dark"],
            corner_radius=10,
            height=44,
            width=160,
            command=self._show_new_ticket_dialog
        )
        self.new_btn.pack(side="right", padx=(12, 0))

        # ═══ CONTENT AREA ═══
        content = ctk.CTkFrame(main, fg_color="transparent")
        content.pack(fill="both", expand=True)

        # Left panel - Dashboard + Ticket list
        left_panel = ctk.CTkFrame(content, fg_color="transparent", width=450)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 16))
        left_panel.pack_propagate(False)

        # Stats row (container for refreshable stats)
        self.stats_container = ctk.CTkFrame(left_panel, fg_color="transparent")
        self.stats_container.pack(fill="x", pady=(0, 20))
        self._refresh_stats()

        # Search and filter
        filter_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 12))

        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *a: self._refresh_ticket_list())

        self.search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="🔍 Search tickets...",
            textvariable=self.search_var,
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=10,
            fg_color=COLORS["bg_card"],
            border_color=COLORS["border"],
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.filter_var = ctk.StringVar(value="All")
        self.filter_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=["All", "Open", "In Progress", "Resolved", "Closed"],
            variable=self.filter_var,
            command=lambda _: self._refresh_ticket_list(),
            width=140,
            height=40,
            corner_radius=10,
            fg_color=COLORS["bg_card"],
        )
        self.filter_menu.pack(side="right")

        # Ticket list - scrollable
        list_label = ctk.CTkLabel(
            left_panel,
            text="Tickets",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_secondary"]
        )
        list_label.pack(anchor="w", pady=(8, 6))

        self.ticket_list_frame = ctk.CTkScrollableFrame(
            left_panel,
            fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent_cyan"],
        )
        self.ticket_list_frame.pack(fill="both", expand=True)

        # Right panel - Ticket detail
        right_panel = ctk.CTkFrame(content, fg_color=COLORS["bg_card"], corner_radius=16, 
                                   border_width=1, border_color=COLORS["border"], width=480)
        right_panel.pack(side="right", fill="both", expand=True, padx=(16, 0))
        right_panel.pack_propagate(False)

        self.detail_inner = ctk.CTkFrame(right_panel, fg_color="transparent")
        self.detail_inner.pack(fill="both", expand=True, padx=28, pady=28)

        # Empty state for detail panel
        self.detail_empty = ctk.CTkFrame(self.detail_inner, fg_color="transparent")
        self.detail_empty.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self.detail_empty,
            text="👆",
            font=ctk.CTkFont(size=48),
            text_color=COLORS["text_secondary"]
        ).pack(pady=(80, 12))

        ctk.CTkLabel(
            self.detail_empty,
            text="Select a ticket",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack()

        ctk.CTkLabel(
            self.detail_empty,
            text="Choose a ticket from the list to view details\nand update its status.",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"],
            justify="center"
        ).pack(pady=(8, 0))

        self.detail_content = None  # Will hold the detailed view when a ticket is selected

        self._refresh_ticket_list()

    def _get_filtered_tickets(self) -> list[Ticket]:
        search = self.search_var.get().lower().strip()
        status_filter = self.filter_var.get()

        result = self.tickets
        if status_filter != "All":
            result = [t for t in result if t.status == status_filter]
        if search:
            result = [
                t for t in result
                if search in t.title.lower() or search in t.description.lower()
                or search in t.requester.lower() or search in t.id.lower()
            ]
        return sorted(result, key=lambda t: t.created_at, reverse=True)

    def _refresh_ticket_list(self):
        for widget in self.ticket_list_frame.winfo_children():
            widget.destroy()

        for ticket in self._get_filtered_tickets():
            card = TicketCard(self.ticket_list_frame, ticket, self._on_ticket_click)
            card.pack(fill="x")

        if not self.ticket_list_frame.winfo_children():
            ctk.CTkLabel(
                self.ticket_list_frame,
                text="No tickets found",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_secondary"]
            ).pack(pady=40, anchor="center")

    def _on_ticket_click(self, ticket: Ticket):
        self.selected_ticket = ticket
        self._show_ticket_detail(ticket)

    def _show_ticket_detail(self, ticket: Ticket):
        if self.detail_content:
            self.detail_content.destroy()

        self.detail_content = ctk.CTkFrame(self.detail_inner, fg_color="transparent")
        self.detail_content.pack(fill="both", expand=True)

        # Title
        ctk.CTkLabel(
            self.detail_content,
            text=ticket.title,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"],
            wraplength=400,
            justify="left"
        ).pack(anchor="w", pady=(0, 8))

        # ID and dates
        meta = f"#{ticket.id}  •  Created {ticket.created_at}  •  Updated {ticket.updated_at}"
        ctk.CTkLabel(
            self.detail_content,
            text=meta,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", pady=(0, 16))

        # Info grid
        info_frame = ctk.CTkFrame(self.detail_content, fg_color=COLORS["bg_dark"], corner_radius=10, padx=16, pady=12)
        info_frame.pack(fill="x", pady=(0, 16))

        for label, value in [
            ("Requester", ticket.requester),
            ("Category", ticket.category),
            ("Priority", ticket.priority),
        ]:
            row = ctk.CTkFrame(info_frame, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=f"{label}:", font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=COLORS["text_secondary"], width=80, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=value, font=ctk.CTkFont(size=12),
                         text_color=COLORS["text_primary"], anchor="w").pack(side="left", fill="x", expand=True)

        # Description
        ctk.CTkLabel(
            self.detail_content,
            text="Description",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", pady=(8, 4))

        desc_frame = ctk.CTkFrame(self.detail_content, fg_color=COLORS["bg_dark"], corner_radius=10, padx=16, pady=12)
        desc_frame.pack(fill="both", expand=True, pady=(0, 16))

        ctk.CTkLabel(
            desc_frame,
            text=ticket.description,
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_primary"],
            wraplength=400,
            justify="left"
        ).pack(anchor="nw", fill="both", expand=True)

        # Status update
        ctk.CTkLabel(
            self.detail_content,
            text="Update Status",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", pady=(8, 6))

        status_frame = ctk.CTkFrame(self.detail_content, fg_color="transparent")
        status_frame.pack(fill="x")

        for status in ["Open", "In Progress", "Resolved", "Closed"]:
            btn = ctk.CTkButton(
                status_frame,
                text=status,
                font=ctk.CTkFont(size=12),
                fg_color=COLORS["accent_cyan"] if ticket.status == status else COLORS["bg_hover"],
                hover_color=COLORS["accent_cyan"],
                text_color=COLORS["bg_dark"] if ticket.status == status else COLORS["text_primary"],
                corner_radius=8,
                height=36,
                width=100,
                command=lambda s=status: self._update_ticket_status(s)
            )
            btn.pack(side="left", padx=(0, 8), pady=(0, 8))

        self.detail_empty.pack_forget()

    def _update_ticket_status(self, new_status: str):
        if not self.selected_ticket:
            return
        self.selected_ticket.status = new_status
        self.selected_ticket.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.storage.save(self.tickets)
        self._show_ticket_detail(self.selected_ticket)
        self._refresh_ticket_list()
        self._refresh_stats()

    def _refresh_stats(self):
        for w in self.stats_container.winfo_children():
            w.destroy()
        total = len(self.tickets)
        open_count = sum(1 for t in self.tickets if t.status == "Open")
        progress = sum(1 for t in self.tickets if t.status == "In Progress")
        resolved = sum(1 for t in self.tickets if t.status in ("Resolved", "Closed"))
        stats_frame = ctk.CTkFrame(self.stats_container, fg_color="transparent")
        stats_frame.pack(fill="x")
        stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_grid.pack(fill="x")
        StatCard(stats_grid, "Total Tickets", str(total), "📋", COLORS["accent_cyan"]).pack(side="left", fill="both", expand=True)
        StatCard(stats_grid, "Open", str(open_count), "🔓", COLORS["accent_amber"]).pack(side="left", fill="both", expand=True)
        stats_grid2 = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_grid2.pack(fill="x", pady=(8, 0))
        StatCard(stats_grid2, "In Progress", str(progress), "⚙️", COLORS["accent_violet"]).pack(side="left", fill="both", expand=True)
        StatCard(stats_grid2, "Resolved", str(resolved), "✓", COLORS["accent_mint"]).pack(side="left", fill="both", expand=True)

    def _show_new_ticket_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Create New Ticket")
        dialog.geometry("500x520")
        dialog.configure(fg_color=COLORS["bg_dark"])
        dialog.transient(self)
        dialog.grab_set()

        # Center on parent
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 500) // 2
        y = self.winfo_y() + (self.winfo_height() - 520) // 2
        dialog.geometry(f"+{x}+{y}")

        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=32, pady=32)

        ctk.CTkLabel(frame, text="New Support Ticket", font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=COLORS["accent_cyan"]).pack(anchor="w", pady=(0, 24))

        entries = {}

        def add_field(label: str, widget_func, **kwargs):
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(12, 4))
            w = widget_func(frame, **kwargs)
            w.pack(fill="x", pady=(0, 4))
            return w

        entries["title"] = add_field("Title", ctk.CTkEntry, placeholder_text="Brief summary of the issue",
                                    height=40, corner_radius=10, fg_color=COLORS["bg_card"])
        entries["requester"] = add_field("Requester", ctk.CTkEntry, placeholder_text="Your name or email",
                                        height=40, corner_radius=10, fg_color=COLORS["bg_card"])
        entries["category"] = add_field("Category", ctk.CTkOptionMenu,
                                       values=["Hardware", "Software", "Network", "Access", "Other"],
                                       width=200, height=40, corner_radius=10, fg_color=COLORS["bg_card"])
        entries["priority"] = add_field("Priority", ctk.CTkOptionMenu,
                                       values=["Low", "Medium", "High", "Critical"],
                                       width=200, height=40, corner_radius=10, fg_color=COLORS["bg_card"])
        entries["description"] = add_field("Description", ctk.CTkTextbox,
                                          height=120, corner_radius=10, fg_color=COLORS["bg_card"])

        def submit():
            title = entries["title"].get().strip()
            requester = entries["requester"].get().strip()
            description = entries["description"].get("1.0", "end").strip()

            if not title:
                messagebox.showwarning("Validation", "Please enter a title.")
                return
            if not requester:
                messagebox.showwarning("Validation", "Please enter the requester name.")
                return
            if not description:
                messagebox.showwarning("Validation", "Please enter a description.")
                return

            ticket = Ticket(
                title=title,
                description=description,
                category=entries["category"].get(),
                priority=entries["priority"].get(),
                requester=requester
            )
            self.tickets.append(ticket)
            self.storage.save(self.tickets)
            self._refresh_ticket_list()
            self._refresh_stats()
            dialog.destroy()
            messagebox.showinfo("Success", f"Ticket #{ticket.id} created successfully!")

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(24, 0))

        ctk.CTkButton(
            btn_frame,
            text="Create Ticket",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["accent_cyan"],
            hover_color="#00a8cc",
            text_color=COLORS["bg_dark"],
            corner_radius=10,
            height=44,
            command=submit
        ).pack(side="right")

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_secondary"],
            corner_radius=10,
            height=44,
            command=dialog.destroy
        ).pack(side="right", padx=(0, 12))


def main():
    app = ITSupportApp()
    app.mainloop()


if __name__ == "__main__":
    main()
