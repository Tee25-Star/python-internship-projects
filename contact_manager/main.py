import os
import sqlite3
import customtkinter as ctk
from tkinter import messagebox


DB_FILE = "contacts.db"


class ContactDatabase:
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    company TEXT,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    tags TEXT,
                    notes TEXT
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def list_contacts(self, query: str | None = None):
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            if query:
                like = f"%{query.lower()}%"
                cur.execute(
                    """
                    SELECT id, full_name, company, phone, email, tags
                    FROM contacts
                    WHERE
                        LOWER(full_name) LIKE ?
                        OR LOWER(company) LIKE ?
                        OR LOWER(tags) LIKE ?
                    ORDER BY LOWER(full_name)
                    """,
                    (like, like, like),
                )
            else:
                cur.execute(
                    """
                    SELECT id, full_name, company, phone, email, tags
                    FROM contacts
                    ORDER BY LOWER(full_name)
                    """
                )
            return cur.fetchall()
        finally:
            conn.close()

    def get_contact(self, contact_id: int):
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, full_name, company, email, phone, address, tags, notes
                FROM contacts
                WHERE id = ?
                """,
                (contact_id,),
            )
            return cur.fetchone()
        finally:
            conn.close()

    def create_contact(self, data: dict):
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO contacts (full_name, company, email, phone, address, tags, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data.get("full_name", "").strip(),
                    data.get("company", "").strip(),
                    data.get("email", "").strip(),
                    data.get("phone", "").strip(),
                    data.get("address", "").strip(),
                    data.get("tags", "").strip(),
                    data.get("notes", "").strip(),
                ),
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def update_contact(self, contact_id: int, data: dict):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                UPDATE contacts
                SET full_name = ?, company = ?, email = ?, phone = ?,
                    address = ?, tags = ?, notes = ?
                WHERE id = ?
                """,
                (
                    data.get("full_name", "").strip(),
                    data.get("company", "").strip(),
                    data.get("email", "").strip(),
                    data.get("phone", "").strip(),
                    data.get("address", "").strip(),
                    data.get("tags", "").strip(),
                    data.get("notes", "").strip(),
                    contact_id,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def delete_contact(self, contact_id: int):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
            conn.commit()
        finally:
            conn.close()


class ContactApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Global appearance
        ctk.set_appearance_mode("dark")  # "light", "dark", "system"
        ctk.set_default_color_theme("blue")  # "blue", "dark-blue", "green"

        self.title("Contact Manager - CRM Lite")
        self.geometry("1080x640")
        self.minsize(960, 580)

        # Database
        self.db = ContactDatabase()
        self.selected_contact_id: int | None = None

        # Configure grid (for responsive layout)
        self.grid_columnconfigure(0, weight=0)  # left sidebar
        self.grid_columnconfigure(1, weight=1)  # main content
        self.grid_rowconfigure(0, weight=1)

        self._build_left_panel()
        self._build_right_panel()
        self.refresh_contact_list()

    # ---------- UI BUILDERS ----------
    def _build_left_panel(self):
        sidebar = ctk.CTkFrame(self, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_rowconfigure(2, weight=1)

        # App branding
        header = ctk.CTkFrame(sidebar, fg_color="transparent")
        header.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header,
            text="Contact Manager",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        subtitle_label = ctk.CTkLabel(
            header,
            text="Your personal CRM lite",
            font=ctk.CTkFont(size=12),
            text_color=("gray30", "gray70"),
        )
        title_label.grid(row=0, column=0, sticky="w")
        subtitle_label.grid(row=1, column=0, sticky="w")

        # Search box
        search_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        search_frame.grid(row=1, column=0, padx=16, pady=(8, 8), sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)

        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Search by name, company, or tags...",
            height=32,
        )
        search_entry.grid(row=0, column=0, sticky="ew")
        search_entry.bind("<KeyRelease>", lambda event: self.refresh_contact_list())

        # Contact list
        list_frame = ctk.CTkFrame(sidebar)
        list_frame.grid(row=2, column=0, padx=8, pady=(4, 8), sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.contact_listbox = ctk.CTkScrollableFrame(
            list_frame,
            fg_color=("gray94", "gray14"),
            corner_radius=10,
            label_text="Contacts",
            label_font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.contact_listbox.grid(row=0, column=0, sticky="nsew")

    def _build_right_panel(self):
        main = ctk.CTkFrame(self, corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # Top bar with actions
        top_bar = ctk.CTkFrame(main, fg_color="transparent")
        top_bar.grid(row=0, column=0, padx=24, pady=(16, 8), sticky="ew")
        top_bar.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            top_bar,
            text="Contact Details",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        title.grid(row=0, column=0, sticky="w")

        btn_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e")

        new_btn = ctk.CTkButton(
            btn_frame,
            text="New",
            width=70,
            command=self.clear_form,
        )
        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save",
            width=70,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            command=self.save_contact,
        )
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete",
            width=70,
            fg_color="#b91c1c",
            hover_color="#7f1d1d",
            command=self.delete_contact,
        )
        new_btn.grid(row=0, column=0, padx=4)
        save_btn.grid(row=0, column=1, padx=4)
        delete_btn.grid(row=0, column=2, padx=4)

        # Detail area
        detail = ctk.CTkFrame(main)
        detail.grid(row=1, column=0, padx=24, pady=(4, 16), sticky="nsew")
        for i in range(4):
            detail.grid_columnconfigure(i, weight=1)
        detail.grid_rowconfigure(6, weight=1)

        # Row 0 - Full Name
        name_label = ctk.CTkLabel(detail, text="Full Name")
        name_label.grid(row=0, column=0, padx=(16, 8), pady=(16, 4), sticky="w")
        self.name_var = ctk.StringVar()
        name_entry = ctk.CTkEntry(
            detail,
            textvariable=self.name_var,
            placeholder_text="e.g. Jane Doe",
        )
        name_entry.grid(
            row=0, column=0, columnspan=2, padx=(16, 8), pady=(0, 8), sticky="ew"
        )

        # Row 1 - Company
        company_label = ctk.CTkLabel(detail, text="Company")
        company_label.grid(row=1, column=0, padx=(16, 8), pady=(4, 4), sticky="w")
        self.company_var = ctk.StringVar()
        company_entry = ctk.CTkEntry(
            detail,
            textvariable=self.company_var,
            placeholder_text="e.g. Acme Inc.",
        )
        company_entry.grid(
            row=1, column=0, columnspan=2, padx=(16, 8), pady=(0, 8), sticky="ew"
        )

        # Row 2 - Email, Phone
        email_label = ctk.CTkLabel(detail, text="Email")
        email_label.grid(row=2, column=0, padx=(16, 8), pady=(4, 4), sticky="w")
        self.email_var = ctk.StringVar()
        email_entry = ctk.CTkEntry(
            detail,
            textvariable=self.email_var,
            placeholder_text="e.g. jane@example.com",
        )
        email_entry.grid(
            row=2, column=0, padx=(16, 8), pady=(0, 8), sticky="ew"
        )

        phone_label = ctk.CTkLabel(detail, text="Phone")
        phone_label.grid(row=2, column=1, padx=(8, 16), pady=(4, 4), sticky="w")
        self.phone_var = ctk.StringVar()
        phone_entry = ctk.CTkEntry(
            detail,
            textvariable=self.phone_var,
            placeholder_text="e.g. +1 555 123 4567",
        )
        phone_entry.grid(
            row=2, column=1, padx=(8, 16), pady=(0, 8), sticky="ew"
        )

        # Row 3 - Tags
        tags_label = ctk.CTkLabel(detail, text="Tags")
        tags_label.grid(row=3, column=0, padx=(16, 8), pady=(4, 4), sticky="w")
        self.tags_var = ctk.StringVar()
        tags_entry = ctk.CTkEntry(
            detail,
            textvariable=self.tags_var,
            placeholder_text="e.g. Client, VIP, Supplier",
        )
        tags_entry.grid(
            row=3, column=0, columnspan=2, padx=(16, 8), pady=(0, 8), sticky="ew"
        )

        # Row 4 & 5 - Address & Notes (multiline)
        address_label = ctk.CTkLabel(detail, text="Address")
        address_label.grid(row=4, column=0, padx=(16, 8), pady=(4, 4), sticky="w")
        self.address_text = ctk.CTkTextbox(detail, height=70)
        self.address_text.grid(
            row=5, column=0, columnspan=2, padx=(16, 8), pady=(0, 8), sticky="nsew"
        )

        notes_label = ctk.CTkLabel(detail, text="Notes")
        notes_label.grid(row=4, column=2, padx=(8, 16), pady=(4, 4), sticky="w")
        self.notes_text = ctk.CTkTextbox(detail, height=70)
        self.notes_text.grid(
            row=5, column=2, columnspan=2, padx=(8, 16), pady=(0, 8), sticky="nsew"
        )

        # Status bar
        self.status_var = ctk.StringVar(value="Ready")
        status_bar = ctk.CTkLabel(
            main,
            textvariable=self.status_var,
            anchor="w",
            font=ctk.CTkFont(size=11),
            text_color=("gray30", "gray70"),
        )
        status_bar.grid(row=2, column=0, padx=24, pady=(0, 8), sticky="ew")

    # ---------- DATA BINDING ----------
    def refresh_contact_list(self):
        # Clear list frame
        for child in self.contact_listbox.winfo_children():
            child.destroy()

        query = self.search_var.get().strip()
        rows = self.db.list_contacts(query or None)

        if not rows:
            empty_label = ctk.CTkLabel(
                self.contact_listbox,
                text="No contacts yet.\nClick 'New' to create one.",
                justify="center",
                text_color=("gray40", "gray70"),
            )
            empty_label.pack(padx=8, pady=16)
            return

        for row in rows:
            contact_id, full_name, company, phone, email, tags = row
            self._create_contact_card(
                self.contact_listbox,
                contact_id,
                full_name,
                company,
                phone,
                email,
                tags,
            )

    def _create_contact_card(
        self,
        parent,
        contact_id: int,
        full_name: str,
        company: str,
        phone: str,
        email: str,
        tags: str,
    ):
        card = ctk.CTkFrame(parent, corner_radius=8)
        card.pack(fill="x", padx=8, pady=4)
        card.bind("<Button-1>", lambda e, cid=contact_id: self.load_contact(cid))

        # Name & company
        name_label = ctk.CTkLabel(
            card,
            text=full_name or "(No name)",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        name_label.grid(row=0, column=0, sticky="w", padx=8, pady=(6, 0))
        name_label.bind("<Button-1>", lambda e, cid=contact_id: self.load_contact(cid))

        company_text = company or ""
        if company_text:
            company_label = ctk.CTkLabel(
                card,
                text=company_text,
                font=ctk.CTkFont(size=11),
                text_color=("gray30", "gray70"),
            )
            company_label.grid(row=1, column=0, sticky="w", padx=8)
            company_label.bind(
                "<Button-1>", lambda e, cid=contact_id: self.load_contact(cid)
            )

        # Contact info row
        # Use simple ASCII separator to avoid encoding issues on some systems.
        info_text_parts = []
        if phone:
            info_text_parts.append(phone)
        if email:
            info_text_parts.append(email)
        info_text = " - ".join(info_text_parts)

        if info_text:
            info_label = ctk.CTkLabel(
                card,
                text=info_text,
                font=ctk.CTkFont(size=11),
                text_color=("gray40", "gray70"),
            )
            info_label.grid(row=2, column=0, sticky="w", padx=8, pady=(0, 4))
            info_label.bind(
                "<Button-1>", lambda e, cid=contact_id: self.load_contact(cid)
            )

        # Tags as chips
        tags = tags or ""
        tags_stripped = [t.strip() for t in tags.split(",") if t.strip()]
        if tags_stripped:
            tags_frame = ctk.CTkFrame(card, fg_color="transparent")
            tags_frame.grid(row=3, column=0, sticky="w", padx=6, pady=(0, 6))
            for tag in tags_stripped[:4]:  # show up to 4 tags
                chip = ctk.CTkLabel(
                    tags_frame,
                    text=tag,
                    font=ctk.CTkFont(size=10),
                    corner_radius=6,
                    fg_color=("gray90", "gray20"),
                    text_color=("gray20", "gray90"),
                    padx=6,
                    pady=2,
                )
                chip.pack(side="left", padx=2)

    def load_contact(self, contact_id: int):
        row = self.db.get_contact(contact_id)
        if not row:
            return

        (
            cid,
            full_name,
            company,
            email,
            phone,
            address,
            tags,
            notes,
        ) = row
        self.selected_contact_id = cid

        self.name_var.set(full_name or "")
        self.company_var.set(company or "")
        self.email_var.set(email or "")
        self.phone_var.set(phone or "")
        self.tags_var.set(tags or "")

        self.address_text.delete("1.0", "end")
        if address:
            self.address_text.insert("1.0", address)

        self.notes_text.delete("1.0", "end")
        if notes:
            self.notes_text.insert("1.0", notes)

        self.status_var.set(f"Loaded contact: {full_name or '(No name)'}")

    def clear_form(self):
        self.selected_contact_id = None
        self.name_var.set("")
        self.company_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.tags_var.set("")
        self.address_text.delete("1.0", "end")
        self.notes_text.delete("1.0", "end")
        self.status_var.set("New contact")

    def _collect_form_data(self) -> dict:
        return {
            "full_name": self.name_var.get().strip(),
            "company": self.company_var.get().strip(),
            "email": self.email_var.get().strip(),
            "phone": self.phone_var.get().strip(),
            "address": self.address_text.get("1.0", "end").strip(),
            "tags": self.tags_var.get().strip(),
            "notes": self.notes_text.get("1.0", "end").strip(),
        }

    def save_contact(self):
        data = self._collect_form_data()
        if not data["full_name"]:
            messagebox.showwarning("Missing Name", "Please enter at least a full name.")
            return

        if self.selected_contact_id is None:
            # Create new
            new_id = self.db.create_contact(data)
            self.selected_contact_id = new_id
            self.status_var.set("Contact created")
        else:
            # Update existing
            self.db.update_contact(self.selected_contact_id, data)
            self.status_var.set("Contact updated")

        self.refresh_contact_list()

    def delete_contact(self):
        if self.selected_contact_id is None:
            messagebox.showinfo("No selection", "Please select a contact to delete.")
            return

        confirm = messagebox.askyesno(
            "Delete Contact",
            "Are you sure you want to permanently delete this contact?",
        )
        if not confirm:
            return

        self.db.delete_contact(self.selected_contact_id)
        self.clear_form()
        self.refresh_contact_list()
        self.status_var.set("Contact deleted")


def main():
    app = ContactApp()
    app.mainloop()


if __name__ == "__main__":
    main()

