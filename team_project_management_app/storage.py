from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat(sep=" ")


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _atomic_write_json(path: str, payload: Dict[str, Any]) -> None:
    folder = os.path.dirname(path)
    _ensure_dir(folder)
    fd, tmp_path = tempfile.mkstemp(prefix="._teamflow_", suffix=".json", dir=folder)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


def default_data() -> Dict[str, Any]:
    # Lightweight sample data so the UI looks populated on first run.
    return {
        "meta": {"app": "TeamFlow", "created_at": now_iso(), "updated_at": now_iso()},
        "next_ids": {"project": 3, "task": 6, "member": 4},
        "members": [
            {"id": 1, "name": "Amina K.", "role": "Project Manager", "email": "amina@example.com", "created_at": now_iso()},
            {"id": 2, "name": "Jay O.", "role": "Backend Dev", "email": "jay@example.com", "created_at": now_iso()},
            {"id": 3, "name": "Lebo S.", "role": "UI/UX", "email": "lebo@example.com", "created_at": now_iso()},
        ],
        "projects": [
            {
                "id": 1,
                "name": "TeamFlow MVP",
                "description": "Build the first working version of the app.",
                "owner_member_id": 1,
                "status": "Active",
                "start_date": "2026-01-10",
                "end_date": "2026-02-10",
                "created_at": now_iso(),
                "updated_at": now_iso(),
            },
            {
                "id": 2,
                "name": "Marketing Website",
                "description": "Landing page + onboarding docs.",
                "owner_member_id": 3,
                "status": "Planning",
                "start_date": "2026-01-20",
                "end_date": "2026-02-05",
                "created_at": now_iso(),
                "updated_at": now_iso(),
            },
        ],
        "tasks": [
            {
                "id": 1,
                "project_id": 1,
                "title": "Define requirements & scope",
                "assignee_member_id": 1,
                "priority": "High",
                "status": "Done",
                "due_date": "2026-01-12",
                "notes": "Capture core flows: projects, tasks, members, dashboard.",
                "created_at": now_iso(),
                "updated_at": now_iso(),
            },
            {
                "id": 2,
                "project_id": 1,
                "title": "Design standout UI layout",
                "assignee_member_id": 3,
                "priority": "High",
                "status": "In Progress",
                "due_date": "2026-01-29",
                "notes": "Sidebar + cards + modern dark theme.",
                "created_at": now_iso(),
                "updated_at": now_iso(),
            },
            {
                "id": 3,
                "project_id": 1,
                "title": "Implement JSON persistence",
                "assignee_member_id": 2,
                "priority": "Medium",
                "status": "Todo",
                "due_date": "2026-01-31",
                "notes": "Atomic writes; safe load fallback.",
                "created_at": now_iso(),
                "updated_at": now_iso(),
            },
            {
                "id": 4,
                "project_id": 2,
                "title": "Write hero copy + feature bullets",
                "assignee_member_id": 1,
                "priority": "Low",
                "status": "Todo",
                "due_date": "2026-02-02",
                "notes": "",
                "created_at": now_iso(),
                "updated_at": now_iso(),
            },
            {
                "id": 5,
                "project_id": 2,
                "title": "Draft onboarding checklist",
                "assignee_member_id": 3,
                "priority": "Medium",
                "status": "Todo",
                "due_date": "2026-02-03",
                "notes": "",
                "created_at": now_iso(),
                "updated_at": now_iso(),
            },
        ],
    }


@dataclass
class DataStore:
    path: str
    data: Dict[str, Any]

    @classmethod
    def open(cls, path: str) -> "DataStore":
        if not os.path.exists(path):
            payload = default_data()
            _atomic_write_json(path, payload)
            return cls(path=path, data=payload)

        try:
            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            if not isinstance(payload, dict):
                raise ValueError("Data file is not a JSON object.")
            return cls(path=path, data=payload)
        except Exception:
            # Back up corrupt file and start fresh.
            bak = path + ".bak"
            try:
                shutil.copyfile(path, bak)
            except Exception:
                pass
            payload = default_data()
            _atomic_write_json(path, payload)
            return cls(path=path, data=payload)

    def save(self) -> None:
        self.data.setdefault("meta", {})
        self.data["meta"]["updated_at"] = now_iso()
        _atomic_write_json(self.path, self.data)

    # ---- helpers for IDs ----
    def _next_id(self, key: str) -> int:
        self.data.setdefault("next_ids", {})
        nxt = int(self.data["next_ids"].get(key, 1))
        self.data["next_ids"][key] = nxt + 1
        return nxt

    # ---- members ----
    def add_member(self, name: str, role: str, email: str) -> Dict[str, Any]:
        m = {"id": self._next_id("member"), "name": name, "role": role, "email": email, "created_at": now_iso()}
        self.data.setdefault("members", []).append(m)
        return m

    # ---- projects ----
    def add_project(
        self,
        name: str,
        description: str,
        owner_member_id: int | None,
        status: str,
        start_date: str,
        end_date: str,
    ) -> Dict[str, Any]:
        p = {
            "id": self._next_id("project"),
            "name": name,
            "description": description,
            "owner_member_id": owner_member_id,
            "status": status,
            "start_date": start_date,
            "end_date": end_date,
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }
        self.data.setdefault("projects", []).append(p)
        return p

    # ---- tasks ----
    def add_task(
        self,
        project_id: int | None,
        title: str,
        assignee_member_id: int | None,
        priority: str,
        status: str,
        due_date: str,
        notes: str,
    ) -> Dict[str, Any]:
        t = {
            "id": self._next_id("task"),
            "project_id": project_id,
            "title": title,
            "assignee_member_id": assignee_member_id,
            "priority": priority,
            "status": status,
            "due_date": due_date,
            "notes": notes,
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }
        self.data.setdefault("tasks", []).append(t)
        return t

