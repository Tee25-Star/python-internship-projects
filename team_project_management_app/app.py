from __future__ import annotations

import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import customtkinter as ctk
from tkinter import messagebox

from storage import DataStore


APP_NAME = "TeamFlow"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _resource_path(*parts: str) -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, *parts)


def _safe_int(v: Any) -> Optional[int]:
    try:
        if v is None or v == "" or v == "None":
            return None
        return int(v)
    except Exception:
        return None


def _is_valid_date(s: str) -> bool:
    if not s:
        return True
    if not DATE_RE.match(s.strip()):
        return False
    try:
        datetime.strptime(s.strip(), "%Y-%m-%d")
        return True
    except Exception:
        return False


class Badge(ctk.CTkFrame):
    def __init__(self, master, text: str, fg: str, **kwargs):
        super().__init__(master, fg_color=fg, corner_radius=999, **kwargs)
        ctk.CTkLabel(self, text=text, text_color="#0b0f14", font=ctk.CTkFont(size=12, weight="bold")).pack(
            padx=10, pady=4
        )


class StatCard(ctk.CTkFrame):
    def __init__(self, master, title: str, value: str, subtitle: str = "", accent: str = "#3b82f6"):
        super().__init__(master, fg_color="#121826", corner_radius=16)
        self.grid_columnconfigure(0, weight=1)
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 6))
        ctk.CTkLabel(top, text=title, text_color="#aab4c4", font=ctk.CTkFont(size=12)).pack(side="left")
        Badge(top, text="LIVE", fg=accent).pack(side="right")
        ctk.CTkLabel(self, text=value, text_color="#e8eefc", font=ctk.CTkFont(size=26, weight="bold")).grid(
            row=1, column=0, sticky="w", padx=14
        )
        if subtitle:
            ctk.CTkLabel(self, text=subtitle, text_color="#93a4c7", font=ctk.CTkFont(size=12)).grid(
                row=2, column=0, sticky="w", padx=14, pady=(0, 14)
            )
        else:
            ctk.CTkLabel(self, text="", fg_color="transparent").grid(row=2, column=0, pady=(0, 14))


class RowCard(ctk.CTkFrame):
    def __init__(self, master, title: str, subtitle: str, right_text: str = "", pill: Tuple[str, str] | None = None):
        super().__init__(master, fg_color="#0f1522", corner_radius=14)
        self.grid_columnconfigure(0, weight=1)
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="ew", padx=14, pady=12)
        ctk.CTkLabel(left, text=title, text_color="#e8eefc", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w"
        )
        ctk.CTkLabel(left, text=subtitle, text_color="#93a4c7", font=ctk.CTkFont(size=12)).pack(anchor="w")

        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e", padx=14, pady=12)
        if pill:
            Badge(right, text=pill[0], fg=pill[1]).pack(side="right")
        if right_text:
            ctk.CTkLabel(right, text=right_text, text_color="#aab4c4", font=ctk.CTkFont(size=12)).pack(
                side="right", padx=(0, 10)
            )


class TeamFlowApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title(f"{APP_NAME} — Team Project Management")
        self.geometry("1200x720")
        self.minsize(1050, 650)

        self.data_path = _resource_path("data", "teamflow.json")
        self.store = DataStore.open(self.data_path)

        # ---- layout ----
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=250, fg_color="#0b0f14", corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_rowconfigure(99, weight=1)

        self.main = ctk.CTkFrame(self, fg_color="#0a0f18", corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        self._build_sidebar()
        self._build_header()
        self._build_pages()

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.refresh_all()
        self.show_page("Dashboard")

    # ---------- UI BUILDERS ----------
    def _build_sidebar(self) -> None:
        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 10))
        ctk.CTkLabel(brand, text="TEAMFLOW", text_color="#e8eefc", font=ctk.CTkFont(size=18, weight="bold")).pack(
            anchor="w"
        )
        ctk.CTkLabel(
            brand, text="Project Management Suite", text_color="#93a4c7", font=ctk.CTkFont(size=12)
        ).pack(anchor="w", pady=(2, 0))

        nav = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav.grid(row=1, column=0, sticky="ew", padx=14, pady=(8, 0))

        self.nav_buttons: Dict[str, ctk.CTkButton] = {}
        for i, name in enumerate(["Dashboard", "Projects", "Tasks", "Team", "Reports", "Settings"]):
            btn = ctk.CTkButton(
                nav,
                text=name,
                height=42,
                fg_color="#121826",
                hover_color="#1b2840",
                text_color="#e8eefc",
                corner_radius=12,
                anchor="w",
                command=lambda n=name: self.show_page(n),
            )
            btn.grid(row=i, column=0, sticky="ew", pady=7)
            self.nav_buttons[name] = btn

        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.grid(row=99, column=0, sticky="ew", padx=14, pady=16)
        self.autosave_label = ctk.CTkLabel(
            footer, text="Auto-save: ready", text_color="#7ea6ff", font=ctk.CTkFont(size=12)
        )
        self.autosave_label.pack(anchor="w")
        ctk.CTkLabel(
            footer, text="Data: local JSON", text_color="#93a4c7", font=ctk.CTkFont(size=12)
        ).pack(anchor="w", pady=(3, 0))

    def _build_header(self) -> None:
        self.header = ctk.CTkFrame(self.main, fg_color="#0a0f18", corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew", padx=18, pady=18)
        self.header.grid_columnconfigure(1, weight=1)

        self.page_title = ctk.CTkLabel(self.header, text="Dashboard", text_color="#e8eefc", font=ctk.CTkFont(size=24, weight="bold"))
        self.page_title.grid(row=0, column=0, sticky="w")

        self.search_var = ctk.StringVar(value="")
        self.search_entry = ctk.CTkEntry(
            self.header,
            textvariable=self.search_var,
            placeholder_text="Search projects, tasks, members…",
            height=38,
            corner_radius=12,
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(16, 10))
        self.search_entry.bind("<KeyRelease>", lambda _e: self.refresh_active_page())

        self.quick_add_menu = ctk.CTkOptionMenu(
            self.header,
            values=["Quick Add", "New Project", "New Task", "New Member"],
            command=self._on_quick_add,
            height=38,
            corner_radius=12,
        )
        self.quick_add_menu.set("Quick Add")
        self.quick_add_menu.grid(row=0, column=2, sticky="e")

    def _build_pages(self) -> None:
        self.pages: Dict[str, ctk.CTkFrame] = {}
        self.page_container = ctk.CTkFrame(self.main, fg_color="transparent")
        self.page_container.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self.page_container.grid_rowconfigure(0, weight=1)
        self.page_container.grid_columnconfigure(0, weight=1)

        self.pages["Dashboard"] = self._page_dashboard(self.page_container)
        self.pages["Projects"] = self._page_projects(self.page_container)
        self.pages["Tasks"] = self._page_tasks(self.page_container)
        self.pages["Team"] = self._page_team(self.page_container)
        self.pages["Reports"] = self._page_reports(self.page_container)
        self.pages["Settings"] = self._page_settings(self.page_container)

        for p in self.pages.values():
            p.grid(row=0, column=0, sticky="nsew")

    # ---------- PAGES ----------
    def _page_dashboard(self, master) -> ctk.CTkFrame:
        page = ctk.CTkFrame(master, fg_color="transparent")
        page.grid_columnconfigure((0, 1, 2), weight=1)
        page.grid_rowconfigure(1, weight=1)

        self.card_projects = StatCard(page, "Projects", "0", "Total projects in the workspace", accent="#60a5fa")
        self.card_projects.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=(0, 12))

        self.card_tasks = StatCard(page, "Tasks", "0", "Across all projects", accent="#34d399")
        self.card_tasks.grid(row=0, column=1, sticky="nsew", padx=12, pady=(0, 12))

        self.card_due = StatCard(page, "Due Soon", "0", "Next 7 days", accent="#fbbf24")
        self.card_due.grid(row=0, column=2, sticky="nsew", padx=(12, 0), pady=(0, 12))

        lower = ctk.CTkFrame(page, fg_color="#0b1220", corner_radius=16)
        lower.grid(row=1, column=0, columnspan=3, sticky="nsew")
        lower.grid_columnconfigure(0, weight=1)
        lower.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(lower, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=16, pady=14)
        ctk.CTkLabel(top, text="Upcoming Tasks", text_color="#e8eefc", font=ctk.CTkFont(size=16, weight="bold")).pack(
            side="left"
        )
        self.dash_hint = ctk.CTkLabel(
            top, text="Tip: use Quick Add to add items instantly.", text_color="#93a4c7", font=ctk.CTkFont(size=12)
        )
        self.dash_hint.pack(side="right")

        self.dash_list = ctk.CTkScrollableFrame(lower, fg_color="transparent")
        self.dash_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.dash_list.grid_columnconfigure(0, weight=1)
        return page

    def _page_projects(self, master) -> ctk.CTkFrame:
        page = ctk.CTkFrame(master, fg_color="transparent")
        page.grid_columnconfigure(0, weight=1)
        page.grid_columnconfigure(1, weight=0)
        page.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(page, fg_color="#0b1220", corner_radius=16)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(1, weight=1)

        hdr = ctk.CTkFrame(left, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=16, pady=14)
        ctk.CTkLabel(hdr, text="Projects", text_color="#e8eefc", font=ctk.CTkFont(size=16, weight="bold")).pack(
            side="left"
        )
        self.projects_count = ctk.CTkLabel(hdr, text="", text_color="#93a4c7", font=ctk.CTkFont(size=12))
        self.projects_count.pack(side="left", padx=(10, 0))

        self.projects_list = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.projects_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.projects_list.grid_columnconfigure(0, weight=1)

        right = ctk.CTkFrame(page, fg_color="#0b1220", corner_radius=16, width=360)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            right, text="Create Project", text_color="#e8eefc", font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))

        self.p_name = ctk.StringVar()
        self.p_owner = ctk.StringVar(value="None")
        self.p_status = ctk.StringVar(value="Active")
        self.p_start = ctk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.p_end = ctk.StringVar(value="")

        self._field(right, 1, "Project Name", self.p_name)
        self.p_desc = ctk.CTkTextbox(right, height=100, corner_radius=12)
        ctk.CTkLabel(right, text="Description", text_color="#93a4c7", font=ctk.CTkFont(size=12)).grid(
            row=2, column=0, sticky="w", padx=16, pady=(10, 6)
        )
        self.p_desc.grid(row=3, column=0, sticky="ew", padx=16)

        ctk.CTkLabel(right, text="Owner", text_color="#93a4c7", font=ctk.CTkFont(size=12)).grid(
            row=4, column=0, sticky="w", padx=16, pady=(12, 6)
        )
        self.p_owner_menu = ctk.CTkOptionMenu(right, values=["None"], variable=self.p_owner, height=36, corner_radius=12)
        self.p_owner_menu.grid(row=5, column=0, sticky="ew", padx=16)

        ctk.CTkLabel(right, text="Status", text_color="#93a4c7", font=ctk.CTkFont(size=12)).grid(
            row=6, column=0, sticky="w", padx=16, pady=(12, 6)
        )
        ctk.CTkOptionMenu(
            right,
            values=["Planning", "Active", "On Hold", "Done"],
            variable=self.p_status,
            height=36,
            corner_radius=12,
        ).grid(row=7, column=0, sticky="ew", padx=16)

        dates = ctk.CTkFrame(right, fg_color="transparent")
        dates.grid(row=8, column=0, sticky="ew", padx=16, pady=(12, 0))
        dates.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(dates, text="Start (YYYY-MM-DD)", text_color="#93a4c7", font=ctk.CTkFont(size=12)).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(dates, text="End (optional)", text_color="#93a4c7", font=ctk.CTkFont(size=12)).grid(
            row=0, column=1, sticky="w", padx=(12, 0)
        )
        ctk.CTkEntry(dates, textvariable=self.p_start, height=36, corner_radius=12).grid(row=1, column=0, sticky="ew")
        ctk.CTkEntry(dates, textvariable=self.p_end, height=36, corner_radius=12).grid(
            row=1, column=1, sticky="ew", padx=(12, 0)
        )

        ctk.CTkButton(
            right, text="Create Project", height=42, corner_radius=14, command=self.create_project
        ).grid(row=9, column=0, sticky="ew", padx=16, pady=(16, 16))

        return page

    def _page_tasks(self, master) -> ctk.CTkFrame:
        page = ctk.CTkFrame(master, fg_color="transparent")
        page.grid_columnconfigure(0, weight=1)
        page.grid_columnconfigure(1, weight=0)
        page.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(page, fg_color="#0b1220", corner_radius=16)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(2, weight=1)

        hdr = ctk.CTkFrame(left, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=16, pady=14)
        ctk.CTkLabel(hdr, text="Tasks", text_color="#e8eefc", font=ctk.CTkFont(size=16, weight="bold")).pack(
            side="left"
        )
        self.tasks_count = ctk.CTkLabel(hdr, text="", text_color="#93a4c7", font=ctk.CTkFont(size=12))
        self.tasks_count.pack(side="left", padx=(10, 0))

        filters = ctk.CTkFrame(left, fg_color="transparent")
        filters.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 10))
        filters.grid_columnconfigure((0, 1, 2), weight=1)

        self.f_project = ctk.StringVar(value="All Projects")
        self.f_status = ctk.StringVar(value="All Status")
        self.f_assignee = ctk.StringVar(value="All Assignees")

        self.f_project_menu = ctk.CTkOptionMenu(filters, values=["All Projects"], variable=self.f_project, command=lambda _v: self.refresh_tasks())
        self.f_project_menu.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.f_status_menu = ctk.CTkOptionMenu(
            filters, values=["All Status", "Todo", "In Progress", "Blocked", "Done"], variable=self.f_status, command=lambda _v: self.refresh_tasks()
        )
        self.f_status_menu.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.f_assignee_menu = ctk.CTkOptionMenu(filters, values=["All Assignees"], variable=self.f_assignee, command=lambda _v: self.refresh_tasks())
        self.f_assignee_menu.grid(row=0, column=2, sticky="ew")

        self.tasks_list = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.tasks_list.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.tasks_list.grid_columnconfigure(0, weight=1)

        right = ctk.CTkFrame(page, fg_color="#0b1220", corner_radius=16, width=360)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            right, text="Create Task", text_color="#e8eefc", font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))

        self.t_title = ctk.StringVar()
        self.t_project = ctk.StringVar(value="None")
        self.t_assignee = ctk.StringVar(value="None")
        self.t_priority = ctk.StringVar(value="Medium")
        self.t_status = ctk.StringVar(value="Todo")
        self.t_due = ctk.StringVar(value="")

        self._field(right, 1, "Title", self.t_title)

        ctk.CTkLabel(right, text="Project", text_color="#93a4c7", font=ctk.CTkFont(size=12)).grid(
            row=2, column=0, sticky="w", padx=16, pady=(10, 6)
        )
        self.t_project_menu = ctk.CTkOptionMenu(right, values=["None"], variable=self.t_project, height=36, corner_radius=12)
        self.t_project_menu.grid(row=3, column=0, sticky="ew", padx=16)

        ctk.CTkLabel(right, text="Assignee", text_color="#93a4c7", font=ctk.CTkFont(size=12)).grid(
            row=4, column=0, sticky="w", padx=16, pady=(12, 6)
        )
        self.t_assignee_menu = ctk.CTkOptionMenu(right, values=["None"], variable=self.t_assignee, height=36, corner_radius=12)
        self.t_assignee_menu.grid(row=5, column=0, sticky="ew", padx=16)

        grid = ctk.CTkFrame(right, fg_color="transparent")
        grid.grid(row=6, column=0, sticky="ew", padx=16, pady=(12, 0))
        grid.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(grid, text="Priority", text_color="#93a4c7", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(grid, text="Status", text_color="#93a4c7", font=ctk.CTkFont(size=12)).grid(row=0, column=1, sticky="w", padx=(12, 0))
        ctk.CTkOptionMenu(grid, values=["Low", "Medium", "High", "Urgent"], variable=self.t_priority, height=36, corner_radius=12).grid(
            row=1, column=0, sticky="ew"
        )
        ctk.CTkOptionMenu(grid, values=["Todo", "In Progress", "Blocked", "Done"], variable=self.t_status, height=36, corner_radius=12).grid(
            row=1, column=1, sticky="ew", padx=(12, 0)
        )

        ctk.CTkLabel(right, text="Due Date (YYYY-MM-DD, optional)", text_color="#93a4c7", font=ctk.CTkFont(size=12)).grid(
            row=7, column=0, sticky="w", padx=16, pady=(12, 6)
        )
        ctk.CTkEntry(right, textvariable=self.t_due, height=36, corner_radius=12).grid(row=8, column=0, sticky="ew", padx=16)

        ctk.CTkLabel(right, text="Notes", text_color="#93a4c7", font=ctk.CTkFont(size=12)).grid(
            row=9, column=0, sticky="w", padx=16, pady=(12, 6)
        )
        self.t_notes = ctk.CTkTextbox(right, height=110, corner_radius=12)
        self.t_notes.grid(row=10, column=0, sticky="ew", padx=16)

        ctk.CTkButton(right, text="Create Task", height=42, corner_radius=14, command=self.create_task).grid(
            row=11, column=0, sticky="ew", padx=16, pady=(16, 16)
        )
        return page

    def _page_team(self, master) -> ctk.CTkFrame:
        page = ctk.CTkFrame(master, fg_color="transparent")
        page.grid_columnconfigure(0, weight=1)
        page.grid_columnconfigure(1, weight=0)
        page.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(page, fg_color="#0b1220", corner_radius=16)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(1, weight=1)

        hdr = ctk.CTkFrame(left, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=16, pady=14)
        ctk.CTkLabel(hdr, text="Team Members", text_color="#e8eefc", font=ctk.CTkFont(size=16, weight="bold")).pack(
            side="left"
        )
        self.members_count = ctk.CTkLabel(hdr, text="", text_color="#93a4c7", font=ctk.CTkFont(size=12))
        self.members_count.pack(side="left", padx=(10, 0))

        self.members_list = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.members_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.members_list.grid_columnconfigure(0, weight=1)

        right = ctk.CTkFrame(page, fg_color="#0b1220", corner_radius=16, width=360)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            right, text="Add Member", text_color="#e8eefc", font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))

        self.m_name = ctk.StringVar()
        self.m_role = ctk.StringVar()
        self.m_email = ctk.StringVar()
        self._field(right, 1, "Full Name", self.m_name)
        self._field(right, 3, "Role", self.m_role)
        self._field(right, 5, "Email", self.m_email)

        ctk.CTkButton(right, text="Add Member", height=42, corner_radius=14, command=self.create_member).grid(
            row=7, column=0, sticky="ew", padx=16, pady=(16, 16)
        )
        return page

    def _page_reports(self, master) -> ctk.CTkFrame:
        page = ctk.CTkFrame(master, fg_color="transparent")
        page.grid_columnconfigure((0, 1), weight=1)

        left = ctk.CTkFrame(page, fg_color="#0b1220", corner_radius=16)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            left, text="Task Status Breakdown", text_color="#e8eefc", font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 10))

        self.report_status = ctk.CTkFrame(left, fg_color="transparent")
        self.report_status.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.report_status.grid_columnconfigure(0, weight=1)

        right = ctk.CTkFrame(page, fg_color="#0b1220", corner_radius=16)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            right, text="Priority Mix", text_color="#e8eefc", font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 10))

        self.report_priority = ctk.CTkFrame(right, fg_color="transparent")
        self.report_priority.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.report_priority.grid_columnconfigure(0, weight=1)
        return page

    def _page_settings(self, master) -> ctk.CTkFrame:
        page = ctk.CTkFrame(master, fg_color="transparent")
        box = ctk.CTkFrame(page, fg_color="#0b1220", corner_radius=16)
        box.pack(fill="both", expand=True)

        ctk.CTkLabel(box, text="Settings", text_color="#e8eefc", font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=16, pady=(16, 6)
        )
        ctk.CTkLabel(
            box,
            text="This demo focuses on a standout interface + core project/task/member management.\n"
            "You can extend it with edits/deletes, CSV export, and authentication.",
            text_color="#93a4c7",
            font=ctk.CTkFont(size=12),
            justify="left",
        ).pack(anchor="w", padx=16, pady=(0, 12))

        btns = ctk.CTkFrame(box, fg_color="transparent")
        btns.pack(anchor="w", padx=16, pady=(0, 16))
        ctk.CTkButton(btns, text="Open Data Folder", corner_radius=12, command=self.open_data_folder).pack(side="left")
        ctk.CTkButton(btns, text="Reset to Sample Data", corner_radius=12, fg_color="#ef4444", hover_color="#dc2626", command=self.reset_data).pack(
            side="left", padx=10
        )
        return page

    # ---------- SMALL UI HELPERS ----------
    def _field(self, parent: ctk.CTkFrame, row_label: int, label: str, var: ctk.StringVar) -> None:
        ctk.CTkLabel(parent, text=label, text_color="#93a4c7", font=ctk.CTkFont(size=12)).grid(
            row=row_label, column=0, sticky="w", padx=16, pady=(10, 6)
        )
        ctk.CTkEntry(parent, textvariable=var, height=36, corner_radius=12).grid(row=row_label + 1, column=0, sticky="ew", padx=16)

    def _pill_for_status(self, status: str) -> Tuple[str, str]:
        s = (status or "").strip()
        if s == "Done":
            return ("DONE", "#34d399")
        if s == "In Progress":
            return ("IN PROGRESS", "#60a5fa")
        if s == "Blocked":
            return ("BLOCKED", "#fb7185")
        if s == "On Hold":
            return ("ON HOLD", "#fbbf24")
        if s == "Planning":
            return ("PLANNING", "#c084fc")
        if s == "Active":
            return ("ACTIVE", "#22c55e")
        return ("TODO", "#aab4c4")

    def _pill_for_priority(self, priority: str) -> Tuple[str, str]:
        p = (priority or "").strip()
        if p == "Urgent":
            return ("URGENT", "#fb7185")
        if p == "High":
            return ("HIGH", "#fbbf24")
        if p == "Medium":
            return ("MEDIUM", "#60a5fa")
        return ("LOW", "#34d399")

    # ---------- NAV ----------
    def show_page(self, name: str) -> None:
        self.page_title.configure(text=name)
        for n, btn in self.nav_buttons.items():
            btn.configure(fg_color="#1b2840" if n == name else "#121826")
        self.active_page = name
        self.pages[name].tkraise()
        self.refresh_active_page()

    def refresh_active_page(self) -> None:
        if getattr(self, "active_page", "") == "Dashboard":
            self.refresh_dashboard()
        elif self.active_page == "Projects":
            self.refresh_projects()
        elif self.active_page == "Tasks":
            self.refresh_tasks()
        elif self.active_page == "Team":
            self.refresh_team()
        elif self.active_page == "Reports":
            self.refresh_reports()

    def refresh_all(self) -> None:
        self.refresh_picklists()
        self.refresh_dashboard()
        self.refresh_projects()
        self.refresh_tasks()
        self.refresh_team()
        self.refresh_reports()

    # ---------- QUICK ADD ----------
    def _on_quick_add(self, value: str) -> None:
        if value == "New Project":
            self.show_page("Projects")
            self.p_name.set("")
            self.p_desc.delete("1.0", "end")
        elif value == "New Task":
            self.show_page("Tasks")
            self.t_title.set("")
            self.t_notes.delete("1.0", "end")
        elif value == "New Member":
            self.show_page("Team")
            self.m_name.set("")
            self.m_role.set("")
            self.m_email.set("")
        self.quick_add_menu.set("Quick Add")

    # ---------- DATA LOOKUPS ----------
    def members(self) -> List[Dict[str, Any]]:
        return list(self.store.data.get("members", []))

    def projects(self) -> List[Dict[str, Any]]:
        return list(self.store.data.get("projects", []))

    def tasks(self) -> List[Dict[str, Any]]:
        return list(self.store.data.get("tasks", []))

    def member_display(self, member_id: Optional[int]) -> str:
        if member_id is None:
            return "Unassigned"
        for m in self.members():
            if int(m.get("id")) == int(member_id):
                return m.get("name", f"Member {member_id}")
        return f"Member {member_id}"

    def project_display(self, project_id: Optional[int]) -> str:
        if project_id is None:
            return "No Project"
        for p in self.projects():
            if int(p.get("id")) == int(project_id):
                return p.get("name", f"Project {project_id}")
        return f"Project {project_id}"

    def refresh_picklists(self) -> None:
        members = self.members()
        projects = self.projects()

        member_values = ["None"] + [f'{m["id"]} — {m.get("name","")}' for m in members]
        self.p_owner_menu.configure(values=member_values)
        self.t_assignee_menu.configure(values=member_values)

        project_values = ["None"] + [f'{p["id"]} — {p.get("name","")}' for p in projects]
        self.t_project_menu.configure(values=project_values)

        self.f_project_menu.configure(values=["All Projects"] + [f'{p["id"]} — {p.get("name","")}' for p in projects])
        self.f_assignee_menu.configure(values=["All Assignees"] + [f'{m["id"]} — {m.get("name","")}' for m in members])

    # ---------- CREATE ACTIONS ----------
    def create_member(self) -> None:
        name = self.m_name.get().strip()
        role = self.m_role.get().strip()
        email = self.m_email.get().strip()

        if not name:
            messagebox.showerror("Missing info", "Please enter the member's name.")
            return
        if email and ("@" not in email or "." not in email):
            messagebox.showerror("Invalid email", "Please enter a valid email address (or leave blank).")
            return

        self.store.add_member(name=name, role=role or "Member", email=email)
        self._autosave()
        self.m_name.set("")
        self.m_role.set("")
        self.m_email.set("")
        self.refresh_all()
        messagebox.showinfo("Saved", "Team member added.")

    def create_project(self) -> None:
        name = self.p_name.get().strip()
        desc = self.p_desc.get("1.0", "end").strip()
        owner_id = _safe_int((self.p_owner.get() or "").split("—")[0].strip())
        status = self.p_status.get().strip() or "Active"
        start = self.p_start.get().strip()
        end = self.p_end.get().strip()

        if not name:
            messagebox.showerror("Missing info", "Please enter a project name.")
            return
        if not _is_valid_date(start):
            messagebox.showerror("Invalid date", "Start date must be in YYYY-MM-DD format.")
            return
        if not _is_valid_date(end):
            messagebox.showerror("Invalid date", "End date must be in YYYY-MM-DD format (or leave blank).")
            return

        self.store.add_project(name=name, description=desc, owner_member_id=owner_id, status=status, start_date=start, end_date=end)
        self._autosave()
        self.p_name.set("")
        self.p_desc.delete("1.0", "end")
        self.p_end.set("")
        self.refresh_all()
        messagebox.showinfo("Saved", "Project created.")

    def create_task(self) -> None:
        title = self.t_title.get().strip()
        project_id = _safe_int((self.t_project.get() or "").split("—")[0].strip())
        assignee_id = _safe_int((self.t_assignee.get() or "").split("—")[0].strip())
        priority = self.t_priority.get().strip() or "Medium"
        status = self.t_status.get().strip() or "Todo"
        due = self.t_due.get().strip()
        notes = self.t_notes.get("1.0", "end").strip()

        if not title:
            messagebox.showerror("Missing info", "Please enter a task title.")
            return
        if not _is_valid_date(due):
            messagebox.showerror("Invalid date", "Due date must be in YYYY-MM-DD format (or leave blank).")
            return

        self.store.add_task(
            project_id=project_id,
            title=title,
            assignee_member_id=assignee_id,
            priority=priority,
            status=status,
            due_date=due,
            notes=notes,
        )
        self._autosave()
        self.t_title.set("")
        self.t_due.set("")
        self.t_notes.delete("1.0", "end")
        self.refresh_all()
        messagebox.showinfo("Saved", "Task created.")

    # ---------- REFRESH RENDERS ----------
    def _matches_search(self, text: str) -> bool:
        q = self.search_var.get().strip().lower()
        if not q:
            return True
        return q in (text or "").lower()

    def refresh_dashboard(self) -> None:
        projects = self.projects()
        tasks = self.tasks()
        self.card_projects.children["!ctklabel2"].configure(text=str(len(projects)))
        self.card_tasks.children["!ctklabel2"].configure(text=str(len(tasks)))

        due_soon = 0
        today = datetime.now().date()
        for t in tasks:
            d = (t.get("due_date") or "").strip()
            if not d:
                continue
            try:
                dd = datetime.strptime(d, "%Y-%m-%d").date()
            except Exception:
                continue
            if 0 <= (dd - today).days <= 7 and t.get("status") != "Done":
                due_soon += 1
        self.card_due.children["!ctklabel2"].configure(text=str(due_soon))

        for w in list(self.dash_list.winfo_children()):
            w.destroy()

        upcoming = []
        for t in tasks:
            if t.get("status") == "Done":
                continue
            due = (t.get("due_date") or "").strip()
            if not due:
                continue
            try:
                dd = datetime.strptime(due, "%Y-%m-%d").date()
            except Exception:
                continue
            upcoming.append((dd, t))
        upcoming.sort(key=lambda x: x[0])

        if not upcoming:
            ctk.CTkLabel(
                self.dash_list,
                text="No upcoming tasks with due dates yet. Add one using Quick Add → New Task.",
                text_color="#93a4c7",
                font=ctk.CTkFont(size=13),
            ).grid(row=0, column=0, sticky="w", padx=10, pady=10)
            return

        row = 0
        for dd, t in upcoming[:12]:
            title = t.get("title", "Untitled")
            sub = f'{self.project_display(t.get("project_id"))} • {self.member_display(t.get("assignee_member_id"))}'
            right = dd.strftime("%b %d, %Y")
            pill = self._pill_for_status(str(t.get("status", "")))
            card = RowCard(self.dash_list, title=title, subtitle=sub, right_text=right, pill=pill)
            card.grid(row=row, column=0, sticky="ew", padx=10, pady=8)
            row += 1

    def refresh_projects(self) -> None:
        items = self.projects()
        shown = []
        for p in items:
            text = f'{p.get("name","")} {p.get("description","")} {p.get("status","")} {self.member_display(p.get("owner_member_id"))}'
            if self._matches_search(text):
                shown.append(p)

        self.projects_count.configure(text=f"({len(shown)} shown)")
        for w in list(self.projects_list.winfo_children()):
            w.destroy()

        if not shown:
            ctk.CTkLabel(self.projects_list, text="No projects match your search.", text_color="#93a4c7").grid(
                row=0, column=0, sticky="w", padx=10, pady=10
            )
            return

        row = 0
        for p in sorted(shown, key=lambda x: int(x.get("id", 0))):
            status = str(p.get("status", "Active"))
            owner = self.member_display(p.get("owner_member_id"))
            subtitle = f'{owner} • {p.get("start_date","")} → {p.get("end_date","") or "—"}'
            right = f'#{p.get("id")}'
            pill = self._pill_for_status(status)
            card = RowCard(self.projects_list, title=str(p.get("name", "Untitled")), subtitle=subtitle, right_text=right, pill=pill)
            card.grid(row=row, column=0, sticky="ew", padx=10, pady=8)
            row += 1

    def refresh_tasks(self) -> None:
        tasks = self.tasks()
        members = self.members()
        projects = self.projects()

        # keep filters current
        self.refresh_picklists()

        f_proj = self.f_project.get()
        f_status = self.f_status.get()
        f_assignee = self.f_assignee.get()

        proj_id = None
        if f_proj != "All Projects":
            proj_id = _safe_int(f_proj.split("—")[0].strip())

        assignee_id = None
        if f_assignee != "All Assignees":
            assignee_id = _safe_int(f_assignee.split("—")[0].strip())

        shown = []
        for t in tasks:
            if proj_id is not None and _safe_int(t.get("project_id")) != proj_id:
                continue
            if f_status != "All Status" and str(t.get("status")) != f_status:
                continue
            if assignee_id is not None and _safe_int(t.get("assignee_member_id")) != assignee_id:
                continue
            text = f'{t.get("title","")} {t.get("notes","")} {t.get("status","")} {t.get("priority","")} {self.project_display(t.get("project_id"))} {self.member_display(t.get("assignee_member_id"))}'
            if self._matches_search(text):
                shown.append(t)

        self.tasks_count.configure(text=f"({len(shown)} shown)")
        for w in list(self.tasks_list.winfo_children()):
            w.destroy()

        if not shown:
            ctk.CTkLabel(self.tasks_list, text="No tasks match your filters/search.", text_color="#93a4c7").grid(
                row=0, column=0, sticky="w", padx=10, pady=10
            )
            return

        def sort_key(t: Dict[str, Any]) -> Tuple[int, str]:
            due = (t.get("due_date") or "9999-12-31").strip()
            return (0 if due else 1, due)

        row = 0
        for t in sorted(shown, key=sort_key)[:300]:
            title = str(t.get("title", "Untitled"))
            subtitle = f'{self.project_display(t.get("project_id"))} • {self.member_display(t.get("assignee_member_id"))} • Priority: {t.get("priority","")}'
            right = (t.get("due_date") or "No due date").strip()
            pill = self._pill_for_status(str(t.get("status", "")))
            card = RowCard(self.tasks_list, title=title, subtitle=subtitle, right_text=right, pill=pill)
            card.grid(row=row, column=0, sticky="ew", padx=10, pady=8)
            row += 1

    def refresh_team(self) -> None:
        shown = []
        for m in self.members():
            text = f'{m.get("name","")} {m.get("role","")} {m.get("email","")}'
            if self._matches_search(text):
                shown.append(m)

        self.members_count.configure(text=f"({len(shown)} shown)")
        for w in list(self.members_list.winfo_children()):
            w.destroy()

        if not shown:
            ctk.CTkLabel(self.members_list, text="No team members match your search.", text_color="#93a4c7").grid(
                row=0, column=0, sticky="w", padx=10, pady=10
            )
            return

        row = 0
        for m in sorted(shown, key=lambda x: int(x.get("id", 0))):
            title = f'{m.get("name","")}'
            subtitle = f'{m.get("role","")} • {m.get("email","") or "no email"}'
            right = f'#{m.get("id")}'
            pill = ("MEMBER", "#60a5fa")
            card = RowCard(self.members_list, title=title, subtitle=subtitle, right_text=right, pill=pill)
            card.grid(row=row, column=0, sticky="ew", padx=10, pady=8)
            row += 1

    def refresh_reports(self) -> None:
        for w in list(self.report_status.winfo_children()):
            w.destroy()
        for w in list(self.report_priority.winfo_children()):
            w.destroy()

        tasks = self.tasks()
        status_counts = {"Todo": 0, "In Progress": 0, "Blocked": 0, "Done": 0}
        prio_counts = {"Low": 0, "Medium": 0, "High": 0, "Urgent": 0}
        for t in tasks:
            s = str(t.get("status", "Todo"))
            p = str(t.get("priority", "Medium"))
            if s in status_counts:
                status_counts[s] += 1
            if p in prio_counts:
                prio_counts[p] += 1

        total = max(1, len(tasks))
        r = 0
        for s, n in status_counts.items():
            pct = n / total
            bar = ctk.CTkProgressBar(self.report_status, height=14, corner_radius=999)
            bar.set(pct)
            ctk.CTkLabel(self.report_status, text=f"{s} — {n}", text_color="#e8eefc", font=ctk.CTkFont(size=13, weight="bold")).grid(
                row=r, column=0, sticky="w", pady=(6, 2)
            )
            bar.grid(row=r + 1, column=0, sticky="ew", pady=(0, 8))
            r += 2

        total2 = max(1, len(tasks))
        r = 0
        for p, n in prio_counts.items():
            pct = n / total2
            bar = ctk.CTkProgressBar(self.report_priority, height=14, corner_radius=999)
            bar.set(pct)
            ctk.CTkLabel(self.report_priority, text=f"{p} — {n}", text_color="#e8eefc", font=ctk.CTkFont(size=13, weight="bold")).grid(
                row=r, column=0, sticky="w", pady=(6, 2)
            )
            bar.grid(row=r + 1, column=0, sticky="ew", pady=(0, 8))
            r += 2

    # ---------- SETTINGS ACTIONS ----------
    def open_data_folder(self) -> None:
        folder = os.path.dirname(self.data_path)
        try:
            os.startfile(folder)  # Windows
        except Exception:
            messagebox.showinfo("Data folder", f"Data folder is at:\n{folder}")

    def reset_data(self) -> None:
        if not messagebox.askyesno("Reset", "Reset app data to sample data? This will overwrite your current data file."):
            return
        try:
            if os.path.exists(self.data_path):
                os.remove(self.data_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not remove data file:\n{e}")
            return
        self.store = DataStore.open(self.data_path)
        self.refresh_all()
        messagebox.showinfo("Reset", "Data was reset to sample data.")

    # ---------- SAVE ----------
    def _autosave(self) -> None:
        try:
            self.store.save()
            self.autosave_label.configure(text="Auto-save: saved", text_color="#34d399")
            self.after(1200, lambda: self.autosave_label.configure(text="Auto-save: ready", text_color="#7ea6ff"))
        except Exception as e:
            self.autosave_label.configure(text="Auto-save: error", text_color="#fb7185")
            messagebox.showerror("Save failed", str(e))

    def on_close(self) -> None:
        try:
            self.store.save()
        except Exception:
            pass
        self.destroy()


if __name__ == "__main__":
    TeamFlowApp().mainloop()

