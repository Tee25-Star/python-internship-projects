import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class MedicalAppointmentApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window config
        self.title("MediConnect - Appointment Booking System")
        self.geometry("1050x650")
        self.minsize(1000, 620)
        self.configure(bg="#0f172a")  # Deep navy background

        # Data storage (in-memory)
        self.appointments = []
        self.doctors = [
            {"name": "Dr. Amelia Carter", "specialty": "Cardiologist", "room": "203A"},
            {"name": "Dr. Liam Patel", "specialty": "Dermatologist", "room": "115B"},
            {"name": "Dr. Sophia Nguyen", "specialty": "Pediatrician", "room": "310"},
            {"name": "Dr. Noah Johnson", "specialty": "General Physician", "room": "101"},
            {"name": "Dr. Isabella Rossi", "specialty": "Neurologist", "room": "412"},
        ]

        self._configure_style()
        self._build_layout()

    # --------------------------- Style & Layout --------------------------- #
    def _configure_style(self):
        style = ttk.Style(self)

        # Use clam theme for more control
        style.theme_use("clam")

        # General styles
        style.configure(
            "TFrame",
            background="#0f172a",
        )

        style.configure(
            "Card.TFrame",
            background="#111827",
            relief="flat",
        )

        style.configure(
            "Accent.TLabel",
            background="#0f172a",
            foreground="#38bdf8",
            font=("Segoe UI Semibold", 11),
        )

        style.configure(
            "Heading.TLabel",
            background="#0f172a",
            foreground="#e5e7eb",
            font=("Segoe UI Semibold", 18),
        )

        style.configure(
            "Muted.TLabel",
            background="#0f172a",
            foreground="#9ca3af",
            font=("Segoe UI", 10),
        )

        style.configure(
            "CardHeading.TLabel",
            background="#111827",
            foreground="#e5e7eb",
            font=("Segoe UI Semibold", 13),
        )

        style.configure(
            "CardMuted.TLabel",
            background="#111827",
            foreground="#9ca3af",
            font=("Segoe UI", 10),
        )

        style.configure(
            "TButton",
            font=("Segoe UI Semibold", 10),
            padding=8,
            background="#0ea5e9",
            foreground="#0b1120",
            borderwidth=0,
            focusthickness=0,
        )
        style.map(
            "TButton",
            background=[("active", "#38bdf8")],
            foreground=[("active", "#020617")],
        )

        style.configure(
            "Primary.TButton",
            font=("Segoe UI Semibold", 10),
            padding=8,
            background="#22c55e",
            foreground="#022c22",
            borderwidth=0,
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#4ade80")],
            foreground=[("active", "#022c22")],
        )

        style.configure(
            "Danger.TButton",
            font=("Segoe UI Semibold", 10),
            padding=8,
            background="#ef4444",
            foreground="#fef2f2",
            borderwidth=0,
        )
        style.map(
            "Danger.TButton",
            background=[("active", "#f97373")],
            foreground=[("active", "#fef2f2")],
        )

        style.configure(
            "TEntry",
            padding=6,
            foreground="#e5e7eb",
            fieldbackground="#020617",
            bordercolor="#1f2937",
        )

        style.configure(
            "TCombobox",
            padding=6,
            foreground="#e5e7eb",
            fieldbackground="#020617",
            background="#020617",
        )

        style.configure(
            "Treeview",
            background="#020617",
            foreground="#e5e7eb",
            fieldbackground="#020617",
            rowheight=26,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background="#111827",
            foreground="#e5e7eb",
            font=("Segoe UI Semibold", 10),
        )

    def _build_layout(self):
        # Top gradient-like header
        header = tk.Canvas(self, height=110, bd=0, highlightthickness=0)
        header.pack(fill="x", side="top")
        # Simple fake gradient using rectangles
        header.create_rectangle(0, 0, 350, 110, fill="#0369a1", width=0)
        header.create_rectangle(350, 0, 750, 110, fill="#0ea5e9", width=0)
        header.create_rectangle(750, 0, 1200, 110, fill="#22c55e", width=0)

        # App title over header
        title_frame = tk.Frame(self, bg="", bd=0, highlightthickness=0)
        title_frame.place(x=26, y=18)

        ttk.Label(
            title_frame,
            text="MediConnect",
            style="Heading.TLabel",
            font=("Segoe UI Black", 22),
            background="",
            foreground="#f9fafb",
        ).pack(anchor="w")

        ttk.Label(
            title_frame,
            text="Modern medical appointment booking system",
            style="Muted.TLabel",
            background="",
            foreground="#e5e7eb",
        ).pack(anchor="w", pady=(4, 0))

        # Main content frame
        content = ttk.Frame(self, padding=20)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)

        # Left side: quick stats & doctor list
        left_frame = ttk.Frame(content)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left_frame.rowconfigure(1, weight=1)
        left_frame.columnconfigure(0, weight=1)

        self._build_stats_cards(left_frame)
        self._build_doctor_list(left_frame)

        # Right side: forms + appointments table
        right_frame = ttk.Frame(content)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        right_frame.rowconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)

        self._build_booking_form(right_frame)
        self._build_appointments_table(right_frame)

    def _build_stats_cards(self, parent):
        cards = ttk.Frame(parent)
        cards.grid(row=0, column=0, sticky="ew")
        for i in range(3):
            cards.columnconfigure(i, weight=1)

        self.total_label = self._create_stat_card(
            cards,
            0,
            "Total Appointments",
            "0",
            accent="#38bdf8",
        )
        self.today_label = self._create_stat_card(
            cards,
            1,
            "Today",
            "0",
            accent="#22c55e",
        )
        self.pending_label = self._create_stat_card(
            cards,
            2,
            "Upcoming",
            "0",
            accent="#f97316",
        )

    def _create_stat_card(self, parent, column, title, value, accent="#38bdf8"):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=(14, 10, 14, 12))
        frame.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 10, 0))

        bar = tk.Frame(frame, bg=accent, height=3)
        bar.pack(fill="x", side="top")

        ttk.Label(frame, text=title, style="CardMuted.TLabel").pack(anchor="w", pady=(6, 0))
        label = ttk.Label(
            frame,
            text=value,
            font=("Segoe UI Semibold", 20),
            background="#111827",
            foreground="#e5e7eb",
        )
        label.pack(anchor="w", pady=(4, 0))
        return label

    def _build_doctor_list(self, parent):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=14)
        frame.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        parent.rowconfigure(1, weight=1)

        ttk.Label(frame, text="Available Doctors", style="CardHeading.TLabel").pack(
            anchor="w", pady=(0, 6)
        )
        ttk.Label(
            frame,
            text="Select a doctor when booking an appointment.",
            style="CardMuted.TLabel",
        ).pack(anchor="w", pady=(0, 10))

        columns = ("name", "specialty", "room")
        self.doctor_tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=6,
        )
        self.doctor_tree.pack(fill="both", expand=True)

        self.doctor_tree.heading("name", text="Doctor")
        self.doctor_tree.heading("specialty", text="Specialty")
        self.doctor_tree.heading("room", text="Room")

        self.doctor_tree.column("name", width=150, anchor="w")
        self.doctor_tree.column("specialty", width=120, anchor="w")
        self.doctor_tree.column("room", width=60, anchor="center")

        for doc in self.doctors:
            self.doctor_tree.insert(
                "", "end", values=(doc["name"], doc["specialty"], doc["room"])
            )

    def _build_booking_form(self, parent):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=16)
        frame.grid(row=0, column=0, sticky="ew")

        ttk.Label(frame, text="Book New Appointment", style="CardHeading.TLabel").grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 4)
        )
        ttk.Label(
            frame,
            text="Fill in patient details and select a doctor, date, and time.",
            style="CardMuted.TLabel",
        ).grid(row=1, column=0, columnspan=4, sticky="w", pady=(0, 10))

        for i in range(4):
            frame.columnconfigure(i, weight=1)

        # Row 2: Patient name, Age
        ttk.Label(frame, text="Patient Name", style="CardMuted.TLabel").grid(
            row=2, column=0, sticky="w"
        )
        self.patient_name_var = tk.StringVar()
        name_entry = ttk.Entry(frame, textvariable=self.patient_name_var)
        name_entry.grid(row=3, column=0, sticky="ew", padx=(0, 8), pady=(0, 8))

        ttk.Label(frame, text="Age", style="CardMuted.TLabel").grid(
            row=2, column=1, sticky="w"
        )
        self.age_var = tk.StringVar()
        age_entry = ttk.Entry(frame, textvariable=self.age_var)
        age_entry.grid(row=3, column=1, sticky="ew", padx=(0, 8), pady=(0, 8))

        ttk.Label(frame, text="Gender", style="CardMuted.TLabel").grid(
            row=2, column=2, sticky="w"
        )
        self.gender_var = tk.StringVar()
        gender_combo = ttk.Combobox(
            frame,
            textvariable=self.gender_var,
            values=["Female", "Male", "Non-binary", "Other"],
            state="readonly",
        )
        gender_combo.grid(row=3, column=2, sticky="ew", padx=(0, 8), pady=(0, 8))

        ttk.Label(frame, text="Contact Number", style="CardMuted.TLabel").grid(
            row=2, column=3, sticky="w"
        )
        self.contact_var = tk.StringVar()
        contact_entry = ttk.Entry(frame, textvariable=self.contact_var)
        contact_entry.grid(row=3, column=3, sticky="ew", pady=(0, 8))

        # Row 4: Doctor, Date, Time, Type
        ttk.Label(frame, text="Doctor", style="CardMuted.TLabel").grid(
            row=4, column=0, sticky="w"
        )
        self.doctor_var = tk.StringVar()
        doctor_values = [d["name"] for d in self.doctors]
        doctor_combo = ttk.Combobox(
            frame,
            textvariable=self.doctor_var,
            values=doctor_values,
            state="readonly",
        )
        doctor_combo.grid(row=5, column=0, sticky="ew", padx=(0, 8), pady=(0, 8))

        ttk.Label(frame, text="Date (YYYY-MM-DD)", style="CardMuted.TLabel").grid(
            row=4, column=1, sticky="w"
        )
        self.date_var = tk.StringVar()
        date_entry = ttk.Entry(frame, textvariable=self.date_var)
        date_entry.grid(row=5, column=1, sticky="ew", padx=(0, 8), pady=(0, 8))

        ttk.Label(frame, text="Time (HH:MM, 24h)", style="CardMuted.TLabel").grid(
            row=4, column=2, sticky="w"
        )
        self.time_var = tk.StringVar()
        time_entry = ttk.Entry(frame, textvariable=self.time_var)
        time_entry.grid(row=5, column=2, sticky="ew", padx=(0, 8), pady=(0, 8))

        ttk.Label(frame, text="Visit Type", style="CardMuted.TLabel").grid(
            row=4, column=3, sticky="w"
        )
        self.type_var = tk.StringVar()
        type_combo = ttk.Combobox(
            frame,
            textvariable=self.type_var,
            values=["Consultation", "Follow-up", "Emergency", "Routine Checkup"],
            state="readonly",
        )
        type_combo.grid(row=5, column=3, sticky="ew", pady=(0, 8))

        # Row 6: Symptoms
        ttk.Label(frame, text="Symptoms / Notes", style="CardMuted.TLabel").grid(
            row=6, column=0, columnspan=4, sticky="w"
        )
        self.symptoms_text = tk.Text(
            frame,
            height=3,
            bg="#020617",
            fg="#e5e7eb",
            insertbackground="#e5e7eb",
            relief="flat",
            wrap="word",
        )
        self.symptoms_text.grid(row=7, column=0, columnspan=4, sticky="ew", pady=(0, 10))

        # Buttons
        button_frame = ttk.Frame(frame, style="Card.TFrame")
        button_frame.grid(row=8, column=0, columnspan=4, sticky="e")

        ttk.Button(
            button_frame,
            text="Clear",
            style="TButton",
            command=self._clear_form,
        ).pack(side="right", padx=(0, 6))

        ttk.Button(
            button_frame,
            text="Book Appointment",
            style="Primary.TButton",
            command=self._book_appointment,
        ).pack(side="right")

    def _build_appointments_table(self, parent):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=14)
        frame.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        parent.rowconfigure(1, weight=1)

        header_frame = ttk.Frame(frame, style="Card.TFrame")
        header_frame.pack(fill="x")

        ttk.Label(header_frame, text="Appointments", style="CardHeading.TLabel").pack(
            anchor="w", side="left"
        )

        # Filter entry
        filter_frame = ttk.Frame(header_frame, style="Card.TFrame")
        filter_frame.pack(side="right")

        ttk.Label(filter_frame, text="Filter by patient/doctor:", style="CardMuted.TLabel").pack(
            side="left", padx=(0, 6)
        )
        self.filter_var = tk.StringVar()
        filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_var, width=22)
        filter_entry.pack(side="left")
        filter_entry.bind("<KeyRelease>", lambda e: self._refresh_appointments())

        # Table
        columns = ("patient", "doctor", "datetime", "type", "status")
        self.appointment_tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
        )
        self.appointment_tree.pack(fill="both", expand=True, pady=(10, 6))

        self.appointment_tree.heading("patient", text="Patient")
        self.appointment_tree.heading("doctor", text="Doctor")
        self.appointment_tree.heading("datetime", text="Date & Time")
        self.appointment_tree.heading("type", text="Visit Type")
        self.appointment_tree.heading("status", text="Status")

        self.appointment_tree.column("patient", width=180, anchor="w")
        self.appointment_tree.column("doctor", width=180, anchor="w")
        self.appointment_tree.column("datetime", width=160, anchor="center")
        self.appointment_tree.column("type", width=120, anchor="center")
        self.appointment_tree.column("status", width=90, anchor="center")

        # Action buttons
        actions = ttk.Frame(frame, style="Card.TFrame")
        actions.pack(fill="x")

        ttk.Button(
            actions,
            text="Mark as Completed",
            style="TButton",
            command=self._mark_completed,
        ).pack(side="left")

        ttk.Button(
            actions,
            text="Cancel Appointment",
            style="Danger.TButton",
            command=self._cancel_appointment,
        ).pack(side="left", padx=(10, 0))

    # --------------------------- Logic --------------------------- #
    def _clear_form(self):
        self.patient_name_var.set("")
        self.age_var.set("")
        self.gender_var.set("")
        self.contact_var.set("")
        self.doctor_var.set("")
        self.date_var.set("")
        self.time_var.set("")
        self.type_var.set("")
        self.symptoms_text.delete("1.0", tk.END)

    def _book_appointment(self):
        name = self.patient_name_var.get().strip()
        age = self.age_var.get().strip()
        gender = self.gender_var.get().strip()
        contact = self.contact_var.get().strip()
        doctor = self.doctor_var.get().strip()
        date_str = self.date_var.get().strip()
        time_str = self.time_var.get().strip()
        visit_type = self.type_var.get().strip()
        symptoms = self.symptoms_text.get("1.0", tk.END).strip()

        if not all([name, age, gender, contact, doctor, date_str, time_str, visit_type]):
            messagebox.showwarning("Missing information", "Please fill in all required fields.")
            return

        # Validate age
        try:
            age_int = int(age)
            if age_int <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid age", "Please enter a valid positive number for age.")
            return

        # Validate date & time
        try:
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror(
                "Invalid date/time",
                "Please use formats:\nDate: YYYY-MM-DD\nTime: HH:MM (24-hour).",
            )
            return

        # Check for double-booking same doctor & datetime
        for appt in self.appointments:
            if appt["doctor"] == doctor and appt["datetime"] == dt and appt["status"] != "Canceled":
                messagebox.showerror(
                    "Slot unavailable",
                    "This doctor already has an appointment at that time.",
                )
                return

        appointment = {
            "patient": name,
            "age": age_int,
            "gender": gender,
            "contact": contact,
            "doctor": doctor,
            "datetime": dt,
            "type": visit_type,
            "symptoms": symptoms,
            "status": "Scheduled",
        }
        self.appointments.append(appointment)

        self._refresh_appointments()
        self._update_stats()

        messagebox.showinfo(
            "Appointment booked",
            f"Appointment booked for {name} with {doctor} on {dt.strftime('%Y-%m-%d at %H:%M')}.",
        )

        self._clear_form()

    def _refresh_appointments(self):
        # Clear
        for item in self.appointment_tree.get_children():
            self.appointment_tree.delete(item)

        query = self.filter_var.get().strip().lower()

        for idx, appt in enumerate(self.appointments):
            if query:
                if query not in appt["patient"].lower() and query not in appt["doctor"].lower():
                    continue

            dt_str = appt["datetime"].strftime("%Y-%m-%d  %H:%M")
            self.appointment_tree.insert(
                "",
                "end",
                iid=str(idx),
                values=(appt["patient"], appt["doctor"], dt_str, appt["type"], appt["status"]),
            )

    def _update_stats(self):
        total = len(self.appointments)
        today = 0
        upcoming = 0
        today_str = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now()

        for appt in self.appointments:
            if appt["status"] == "Canceled":
                continue
            if appt["datetime"].strftime("%Y-%m-%d") == today_str:
                today += 1
            if appt["datetime"] >= now and appt["status"] == "Scheduled":
                upcoming += 1

        self.total_label.config(text=str(total))
        self.today_label.config(text=str(today))
        self.pending_label.config(text=str(upcoming))

    def _get_selected_appointment_index(self):
        selection = self.appointment_tree.selection()
        if not selection:
            messagebox.showinfo("No selection", "Please select an appointment first.")
            return None
        try:
            return int(selection[0])
        except ValueError:
            return None

    def _mark_completed(self):
        idx = self._get_selected_appointment_index()
        if idx is None:
            return

        if self.appointments[idx]["status"] == "Canceled":
            messagebox.showinfo("Not allowed", "Canceled appointments cannot be completed.")
            return

        self.appointments[idx]["status"] = "Completed"
        self._refresh_appointments()
        self._update_stats()

    def _cancel_appointment(self):
        idx = self._get_selected_appointment_index()
        if idx is None:
            return

        if messagebox.askyesno(
            "Confirm cancellation",
            "Are you sure you want to cancel this appointment?",
        ):
            self.appointments[idx]["status"] = "Canceled"
            self._refresh_appointments()
            self._update_stats()


def main():
    app = MedicalAppointmentApp()
    app.mainloop()


if __name__ == "__main__":
    main()

