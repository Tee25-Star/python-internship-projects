import os
import json
import datetime

import customtkinter as ctk


# -----------------------------
# Data: Example training plans
# -----------------------------

TRAINING_PLANS = [
    {
        "name": "Lean & Strong - Beginner",
        "level": "Beginner",
        "duration_weeks": 4,
        "goal": "Fat loss, strength foundation",
        "description": "4-week full-body program focused on building a strong base, "
                       "improving posture, and increasing daily activity.",
        "days": [
            {
                "title": "Day 1 - Upper Body Push",
                "focus": "Chest, shoulders, triceps",
                "type": "Strength",
                "exercises": [
                    {"name": "Incline Push-Ups", "sets": "3 x 10–12", "notes": "Hands on bench or table."},
                    {"name": "Dumbbell Shoulder Press", "sets": "3 x 10", "notes": "Light to moderate weight."},
                    {"name": "Triceps Dips (Bench)", "sets": "3 x 8–10", "notes": "Keep shoulders away from ears."},
                    {"name": "Plank Hold", "sets": "3 x 30s", "notes": "Neutral spine, squeeze glutes."},
                ],
            },
            {
                "title": "Day 2 - Lower Body & Core",
                "focus": "Quads, glutes, abs",
                "type": "Strength",
                "exercises": [
                    {"name": "Bodyweight Squats", "sets": "3 x 12", "notes": "Slow and controlled."},
                    {"name": "Reverse Lunges", "sets": "3 x 10/leg", "notes": "Step back softly."},
                    {"name": "Glute Bridge", "sets": "3 x 12–15", "notes": "Hold 2s at top."},
                    {"name": "Dead Bug", "sets": "3 x 10/side", "notes": "Lower back stays on floor."},
                ],
            },
            {
                "title": "Day 3 - Cardio & Mobility",
                "focus": "Heart health, recovery",
                "type": "Cardio / Mobility",
                "exercises": [
                    {"name": "Brisk Walk", "sets": "20–30 min", "notes": "Comfortable conversation pace."},
                    {"name": "Hip Flexor Stretch", "sets": "2 x 30s/side", "notes": "Gentle stretch, no pain."},
                    {"name": "Chest Opener Stretch", "sets": "2 x 30s", "notes": "Open up the front of shoulders."},
                    {"name": "Cat–Cow Mobilization", "sets": "2 x 10", "notes": "Sync movement with breathing."},
                ],
            },
        ],
    },
    {
        "name": "Athletic Build - Intermediate",
        "level": "Intermediate",
        "duration_weeks": 6,
        "goal": "Build muscle, improve conditioning",
        "description": "A 6-week split that mixes classic strength work with short conditioning blocks.",
        "days": [
            {
                "title": "Day 1 - Push Strength",
                "focus": "Chest, shoulders, triceps",
                "type": "Strength",
                "exercises": [
                    {"name": "Barbell Bench Press", "sets": "4 x 6–8", "notes": "Last reps challenging."},
                    {"name": "Incline DB Press", "sets": "3 x 8–10", "notes": "Control the lowering."},
                    {"name": "Lateral Raises", "sets": "3 x 12–15", "notes": "Light weight, strict form."},
                    {"name": "Triceps Rope Pushdown", "sets": "3 x 10–12", "notes": "Elbows stay tucked."},
                    {"name": "Assault Bike / Row", "sets": "8 x 20s hard / 40s easy", "notes": "Moderate intensity."},
                ],
            },
            {
                "title": "Day 2 - Pull Strength",
                "focus": "Back, biceps, rear delts",
                "type": "Strength",
                "exercises": [
                    {"name": "Deadlift (Hex Bar or Barbell)", "sets": "4 x 5", "notes": "Perfect form > weight."},
                    {"name": "Pull-Ups or Lat Pulldown", "sets": "4 x 6–10", "notes": "Full range of motion."},
                    {"name": "Single-Arm DB Row", "sets": "3 x 8–10/side", "notes": "Squeeze at top."},
                    {"name": "Face Pulls", "sets": "3 x 12–15", "notes": "Elbows high, pull to eye level."},
                ],
            },
            {
                "title": "Day 3 - Lower Body Power",
                "focus": "Legs and power",
                "type": "Strength / Power",
                "exercises": [
                    {"name": "Back Squat", "sets": "4 x 6", "notes": "Solid depth, stable core."},
                    {"name": "Romanian Deadlift", "sets": "3 x 8–10", "notes": "Hinge at hips, soft knees."},
                    {"name": "Walking Lunges", "sets": "3 x 10/leg", "notes": "Long stride, upright torso."},
                    {"name": "Box Jumps", "sets": "3 x 5", "notes": "Step down between reps."},
                ],
            },
        ],
    },
    {
        "name": "High-Performance - Advanced",
        "level": "Advanced",
        "duration_weeks": 8,
        "goal": "Performance, strength, and body composition",
        "description": "An 8-week high-performance block with focused strength work, "
                       "conditioning, and dedicated recovery sessions.",
        "days": [
            {
                "title": "Day 1 - Heavy Lower",
                "focus": "Max strength",
                "type": "Strength",
                "exercises": [
                    {"name": "Back Squat", "sets": "5 x 3–5", "notes": "Work up to a heavy set."},
                    {"name": "Front Squat", "sets": "3 x 5", "notes": "Stay upright, tight core."},
                    {"name": "Nordic Hamstring Curl", "sets": "3 x 5", "notes": "Control the lowering."},
                    {"name": "Farmer's Carry", "sets": "4 x 30m", "notes": "Heavy dumbbells or farmer handles."},
                ],
            },
            {
                "title": "Day 2 - Upper Power",
                "focus": "Explosive pressing and pulling",
                "type": "Strength / Power",
                "exercises": [
                    {"name": "Push Press", "sets": "5 x 3", "notes": "Dip and drive with legs."},
                    {"name": "Weighted Pull-Ups", "sets": "4 x 4–6", "notes": "Full extension at bottom."},
                    {"name": "Pendlay Rows", "sets": "4 x 6", "notes": "Explosive from floor each rep."},
                    {"name": "Med Ball Chest Pass", "sets": "4 x 5", "notes": "Max intent on each throw."},
                ],
            },
            {
                "title": "Day 3 - Conditioning & Core",
                "focus": "Engine and trunk strength",
                "type": "Conditioning",
                "exercises": [
                    {"name": "Intervals (Run / Bike / Row)", "sets": "10 x 45s hard / 75s easy",
                     "notes": "Hard but repeatable pace."},
                    {"name": "Hanging Leg Raises", "sets": "4 x 8–10", "notes": "No swinging."},
                    {"name": "Side Plank", "sets": "3 x 30–40s/side", "notes": "Hips high, long line."},
                    {"name": "Back Extension", "sets": "3 x 12–15", "notes": "Smooth tempo, no jerking."},
                ],
            },
        ],
    },
]


def get_progress_file() -> str:
    """Return the path to the local JSON file storing progress."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "progress.json")


class FitnessApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Fitness Training Planner")
        self.geometry("1180x720")
        self.minsize(1000, 640)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.progress_data = self._load_progress()
        self.current_plan = None
        self.current_day_index = None
        self.plan_buttons = []
        self.day_buttons = []

        self._build_sidebar()
        self._build_main_area()

        if TRAINING_PLANS:
            self._select_plan(TRAINING_PLANS[0])

    # -----------------------------
    # Data: load & save progress
    # -----------------------------
    def _load_progress(self):
        try:
            with open(get_progress_file(), "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            pass
        return {}

    def _save_progress(self):
        try:
            with open(get_progress_file(), "w", encoding="utf-8") as f:
                json.dump(self.progress_data, f, indent=2)
        except OSError:
            # Fail silently; the app will still work without persistence.
            pass

    def _get_plan_progress_list(self, plan_name: str, num_days: int):
        progress_list = self.progress_data.get(plan_name, [])
        if len(progress_list) < num_days:
            progress_list = list(progress_list) + [False] * (num_days - len(progress_list))
        return progress_list[:num_days]

    def _set_plan_progress_list(self, plan_name: str, progress_list):
        self.progress_data[plan_name] = list(progress_list)
        self._save_progress()

    # -----------------------------
    # UI building
    # -----------------------------
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=250, fg_color="#050816")
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_rowconfigure(3, weight=1)

        # App title / branding
        title_label = ctk.CTkLabel(
            self.sidebar,
            text="FITNESS\nPLANNER",
            justify="left",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.grid(row=0, column=0, padx=20, pady=(24, 8), sticky="w")

        subtitle_label = ctk.CTkLabel(
            self.sidebar,
            text="Design your week.\nOwn your training.",
            justify="left",
            font=ctk.CTkFont(size=11),
            text_color=("gray80", "gray70"),
        )
        subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 18), sticky="w")

        # Date / summary chip
        date_chip = ctk.CTkFrame(self.sidebar, corner_radius=20, fg_color="#111827")
        date_chip.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="ew")
        date_chip.grid_columnconfigure(1, weight=1)
        today = datetime.date.today().strftime("%A, %b %d")
        ctk.CTkLabel(
            date_chip,
            text="Today",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#93c5fd",
        ).grid(row=0, column=0, padx=14, pady=(8, 0), sticky="w")
        ctk.CTkLabel(
            date_chip,
            text=today,
            font=ctk.CTkFont(size=11),
            text_color=("gray90", "gray70"),
        ).grid(row=1, column=0, padx=14, pady=(0, 8), sticky="w")

        # Filter
        filter_label = ctk.CTkLabel(
            self.sidebar,
            text="Filter by level",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        filter_label.grid(row=3, column=0, padx=20, pady=(8, 4), sticky="w")

        self.level_filter = ctk.CTkComboBox(
            self.sidebar,
            values=["All", "Beginner", "Intermediate", "Advanced"],
            command=self._on_filter_changed,
            state="readonly",
            width=200,
        )
        self.level_filter.set("All")
        self.level_filter.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Plan list container
        list_label = ctk.CTkLabel(
            self.sidebar,
            text="Training plans",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        list_label.grid(row=5, column=0, padx=20, pady=(4, 4), sticky="w")

        self.plan_list_frame = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="#020617",
            width=230,
            corner_radius=16,
        )
        self.plan_list_frame.grid(row=6, column=0, padx=12, pady=(0, 12), sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        self._populate_plan_list()

        # Reset progress button at bottom
        reset_button = ctk.CTkButton(
            self.sidebar,
            text="Reset All Progress",
            fg_color="#0f172a",
            hover_color="#1d293b",
            border_width=1,
            border_color="#1e293b",
            command=self._reset_progress,
        )
        reset_button.grid(row=7, column=0, padx=20, pady=(8, 16), sticky="ew")

    def _build_main_area(self):
        self.main = ctk.CTkFrame(self, fg_color="#020617")
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(2, weight=1)
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_columnconfigure(1, weight=1)

        # Top header: plan summary & progress
        self.header_frame = ctk.CTkFrame(self.main, fg_color="#020617")
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(18, 6), padx=18)
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=0)

        self.plan_title_label = ctk.CTkLabel(
            self.header_frame,
            text="",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.plan_title_label.grid(row=0, column=0, padx=(4, 4), pady=(0, 4), sticky="w")

        self.plan_meta_label = ctk.CTkLabel(
            self.header_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=("gray80", "gray70"),
        )
        self.plan_meta_label.grid(row=1, column=0, padx=(4, 4), pady=(0, 8), sticky="w")

        self.plan_desc_label = ctk.CTkLabel(
            self.header_frame,
            text="",
            font=ctk.CTkFont(size=11),
            wraplength=550,
            justify="left",
            text_color=("gray85", "gray70"),
        )
        self.plan_desc_label.grid(row=2, column=0, padx=(4, 4), pady=(0, 10), sticky="w")

        self.progress_text_label = ctk.CTkLabel(
            self.header_frame,
            text="",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#93c5fd",
        )
        self.progress_text_label.grid(row=0, column=1, padx=(10, 0), pady=(0, 4), sticky="e")

        self.progress_bar = ctk.CTkProgressBar(
            self.header_frame,
            width=220,
            height=10,
            corner_radius=10,
            progress_color="#38bdf8",
        )
        self.progress_bar.grid(row=1, column=1, padx=(10, 0), pady=(6, 2), sticky="e")

        self.progress_hint_label = ctk.CTkLabel(
            self.header_frame,
            text="Mark days complete as you go.",
            font=ctk.CTkFont(size=10),
            text_color=("gray75", "gray60"),
        )
        self.progress_hint_label.grid(row=2, column=1, padx=(10, 0), pady=(0, 4), sticky="e")

        # Middle: days list & detail view
        self.days_frame = ctk.CTkFrame(self.main, fg_color="#020617")
        self.days_frame.grid(row=1, column=0, sticky="nsew", padx=(18, 9), pady=(0, 9))
        self.days_frame.grid_rowconfigure(1, weight=1)
        self.days_frame.grid_columnconfigure(0, weight=1)

        days_label = ctk.CTkLabel(
            self.days_frame,
            text="Plan days",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        days_label.grid(row=0, column=0, padx=4, pady=(0, 4), sticky="w")

        self.days_list_frame = ctk.CTkScrollableFrame(
            self.days_frame,
            fg_color="#020617",
            corner_radius=18,
        )
        self.days_list_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 4))

        # Right: detail for selected day
        self.detail_frame = ctk.CTkFrame(self.main, fg_color="#020617")
        self.detail_frame.grid(row=1, column=1, sticky="nsew", padx=(9, 18), pady=(0, 9))
        self.detail_frame.grid_rowconfigure(3, weight=1)
        self.detail_frame.grid_columnconfigure(0, weight=1)

        self.day_title_label = ctk.CTkLabel(
            self.detail_frame,
            text="Select a day to view details",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.day_title_label.grid(row=0, column=0, padx=4, pady=(0, 4), sticky="w")

        self.day_meta_label = ctk.CTkLabel(
            self.detail_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=("gray80", "gray70"),
        )
        self.day_meta_label.grid(row=1, column=0, padx=4, pady=(0, 6), sticky="w")

        self.exercises_frame = ctk.CTkScrollableFrame(
            self.detail_frame,
            fg_color="#020617",
        )
        self.exercises_frame.grid(row=2, column=0, sticky="nsew", pady=(4, 6))

        # Button to mark / unmark completion
        self.complete_button = ctk.CTkButton(
            self.detail_frame,
            text="Mark day as complete",
            fg_color="#22c55e",
            hover_color="#16a34a",
            height=36,
            command=self._toggle_day_complete,
            state="disabled",
        )
        self.complete_button.grid(row=3, column=0, padx=4, pady=(4, 6), sticky="ew")

    # -----------------------------
    # Sidebar helpers
    # -----------------------------
    def _populate_plan_list(self):
        for widget in self.plan_list_frame.winfo_children():
            widget.destroy()
        self.plan_buttons.clear()

        level_filter = self.level_filter.get()
        for plan in TRAINING_PLANS:
            if level_filter != "All" and plan["level"] != level_filter:
                continue

            btn = ctk.CTkButton(
                self.plan_list_frame,
                text=plan["name"],
                corner_radius=16,
                height=60,
                anchor="w",
                fg_color="#020617",
                hover_color="#0f172a",
                border_width=1,
                border_color="#1f2933",
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda p=plan: self._select_plan(p),
            )
            btn.pack(fill="x", padx=8, pady=4)

            subtitle = f"{plan['level']} • {plan['duration_weeks']} weeks"
            small_label = ctk.CTkLabel(
                btn,
                text=subtitle,
                font=ctk.CTkFont(size=10),
                text_color=("gray80", "gray70"),
                anchor="w",
            )
            small_label.place(relx=0.03, rely=0.55)

            self.plan_buttons.append((plan, btn))

    def _on_filter_changed(self, _choice):
        self._populate_plan_list()

    # -----------------------------
    # Plan selection & progress
    # -----------------------------
    def _select_plan(self, plan: dict):
        self.current_plan = plan
        self.current_day_index = None

        # Highlight selected plan
        for p, btn in self.plan_buttons:
            if p is plan:
                btn.configure(fg_color="#0f172a", border_color="#38bdf8")
            else:
                btn.configure(fg_color="#020617", border_color="#1f2933")

        self.plan_title_label.configure(text=plan["name"])

        meta = f"{plan['level']} • {plan['duration_weeks']} weeks • Goal: {plan['goal']}"
        self.plan_meta_label.configure(text=meta)

        self.plan_desc_label.configure(text=plan["description"])

        self._update_progress_ui()
        self._populate_days(plan)

    def _update_progress_ui(self):
        if not self.current_plan:
            return
        plan = self.current_plan
        days_count = len(plan["days"])
        progress_list = self._get_plan_progress_list(plan["name"], days_count)

        done = sum(1 for d in progress_list if d)
        pct = (done / days_count) if days_count > 0 else 0

        self.progress_bar.set(pct)
        self.progress_text_label.configure(
            text=f"{int(pct * 100)}% complete  •  {done}/{days_count} days"
        )

    # -----------------------------
    # Days & detail view
    # -----------------------------
    def _populate_days(self, plan: dict):
        for widget in self.days_list_frame.winfo_children():
            widget.destroy()
        self.day_buttons.clear()

        progress_list = self._get_plan_progress_list(plan["name"], len(plan["days"]))

        for idx, day in enumerate(plan["days"]):
            is_done = progress_list[idx]
            color = "#0f172a" if not is_done else "#065f46"
            hover = "#1e293b" if not is_done else "#047857"

            btn = ctk.CTkButton(
                self.days_list_frame,
                text=f"{idx + 1}. {day['title']}",
                anchor="w",
                height=52,
                corner_radius=16,
                fg_color=color,
                hover_color=hover,
                border_width=1,
                border_color="#1f2933",
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda i=idx: self._select_day(i),
            )
            btn.pack(fill="x", padx=6, pady=4)

            status_text = f"{day['type']} • {day['focus']}"
            if is_done:
                status_text += "  ✓ Completed"
            small_label = ctk.CTkLabel(
                btn,
                text=status_text,
                font=ctk.CTkFont(size=10),
                text_color=("gray85", "gray70"),
                anchor="w",
            )
            small_label.place(relx=0.03, rely=0.55)

            self.day_buttons.append(btn)

        # Clear detail if switching plans
        self.day_title_label.configure(text="Select a day to view details")
        self.day_meta_label.configure(text="")
        for widget in self.exercises_frame.winfo_children():
            widget.destroy()
        self.complete_button.configure(state="disabled", text="Mark day as complete", fg_color="#22c55e")

    def _select_day(self, index: int):
        self.current_day_index = index
        if not self.current_plan:
            return

        plan = self.current_plan
        day = plan["days"][index]
        progress_list = self._get_plan_progress_list(plan["name"], len(plan["days"]))
        is_done = progress_list[index]

        # Update detail header
        self.day_title_label.configure(text=day["title"])
        meta = f"{day['type']} • Focus: {day['focus']}"
        if is_done:
            meta += "  •  Status: Completed"
        else:
            meta += "  •  Status: In progress"
        self.day_meta_label.configure(text=meta)

        # Exercises cards
        for widget in self.exercises_frame.winfo_children():
            widget.destroy()

        for ex in day["exercises"]:
            card = ctk.CTkFrame(self.exercises_frame, corner_radius=14, fg_color="#020617")
            card.pack(fill="x", padx=4, pady=4)

            title_label = ctk.CTkLabel(
                card,
                text=ex["name"],
                font=ctk.CTkFont(size=12, weight="bold"),
            )
            title_label.grid(row=0, column=0, padx=10, pady=(8, 0), sticky="w")

            sets_label = ctk.CTkLabel(
                card,
                text=ex["sets"],
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#38bdf8",
            )
            sets_label.grid(row=0, column=1, padx=10, pady=(8, 0), sticky="e")

            notes_label = ctk.CTkLabel(
                card,
                text=ex["notes"],
                font=ctk.CTkFont(size=10),
                text_color=("gray80", "gray70"),
                wraplength=380,
                justify="left",
            )
            notes_label.grid(row=1, column=0, columnspan=2, padx=10, pady=(2, 8), sticky="w")

        # Completion button
        if is_done:
            self.complete_button.configure(
                text="Mark day as not completed",
                fg_color="#ef4444",
                hover_color="#b91c1c",
                state="normal",
            )
        else:
            self.complete_button.configure(
                text="Mark day as complete",
                fg_color="#22c55e",
                hover_color="#16a34a",
                state="normal",
            )

    def _toggle_day_complete(self):
        if self.current_plan is None or self.current_day_index is None:
            return

        plan = self.current_plan
        day_idx = self.current_day_index
        progress_list = self._get_plan_progress_list(plan["name"], len(plan["days"]))
        progress_list[day_idx] = not progress_list[day_idx]
        self._set_plan_progress_list(plan["name"], progress_list)

        # Refresh UI
        self._update_progress_ui()
        self._populate_days(plan)
        self._select_day(day_idx)

    def _reset_progress(self):
        self.progress_data = {}
        self._save_progress()
        if self.current_plan:
            self._populate_days(self.current_plan)
            self._update_progress_ui()


if __name__ == "__main__":
    app = FitnessApp()
    app.mainloop()

