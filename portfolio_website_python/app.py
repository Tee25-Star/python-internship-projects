from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, redirect, render_template, request, url_for


APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
PROFILE_PATH = DATA_DIR / "profile.json"
PROJECTS_PATH = DATA_DIR / "projects.json"
MESSAGES_PATH = DATA_DIR / "messages.json"

_messages_lock = threading.Lock()


def _read_json(path: Path, default: Any) -> Any:
    try:
        # First, try utf-8 (preferred)
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return default
    except UnicodeDecodeError:
        # Fallback for files saved with Windows-1252 style encoding
        try:
            text = path.read_bytes().decode("cp1252")
        except Exception:
            return default

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return default


def _write_json_atomic(path: Path, data: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def load_profile() -> dict[str, Any]:
    return _read_json(PROFILE_PATH, default={})


def load_projects() -> list[dict[str, Any]]:
    projects = _read_json(PROJECTS_PATH, default=[])
    if not isinstance(projects, list):
        return []
    return projects


def save_message(message: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with _messages_lock:
        existing = _read_json(MESSAGES_PATH, default=[])
        if not isinstance(existing, list):
            existing = []
        existing.append(message)
        _write_json_atomic(MESSAGES_PATH, existing)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    @app.get("/healthz")
    def healthz():
        return {"ok": True}

    @app.get("/")
    def index():
        profile = load_profile()
        projects = load_projects()
        return render_template("index.html", profile=profile, projects=projects)

    @app.get("/api/projects")
    def api_projects():
        return jsonify(load_projects())

    @app.post("/contact")
    def contact():
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip()
        message = (request.form.get("message") or "").strip()

        if not name or not email or not message:
            return (
                render_template(
                    "index.html",
                    profile=load_profile(),
                    projects=load_projects(),
                    form_error="Please fill in your name, email, and message.",
                ),
                400,
            )

        save_message(
            {
                "name": name,
                "email": email,
                "message": message,
                "received_at": datetime.now(timezone.utc).isoformat(),
                "ip": request.headers.get("X-Forwarded-For", request.remote_addr),
                "user_agent": request.user_agent.string,
            }
        )
        return redirect(url_for("thanks"))

    @app.get("/thanks")
    def thanks():
        profile = load_profile()
        return render_template("thanks.html", profile=profile)

    return app


if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    app = create_app()
    # Accessible on your PC at http://127.0.0.1:5000
    app.run(host="127.0.0.1", port=5000, debug=True)
