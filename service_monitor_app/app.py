import time
from urllib.parse import urlparse

import requests
from flask import Flask, jsonify, render_template, request


app = Flask(__name__)


def normalize_url(raw_url: str) -> str:
    """
    Ensure the URL has a scheme and looks minimally valid.
    """
    raw_url = (raw_url or "").strip()
    if not raw_url:
        return ""

    parsed = urlparse(raw_url)
    if not parsed.scheme:
        # Default to http if user omitted scheme
        raw_url = "http://" + raw_url

    return raw_url


def check_website(url: str) -> dict:
    """
    Perform a simple availability check for the given URL.
    """
    url = normalize_url(url)
    if not url:
        return {
            "url": url,
            "status": "invalid",
            "http_status": None,
            "response_time_ms": None,
            "ok": False,
            "error": "Empty or invalid URL",
        }

    start = time.perf_counter()
    try:
        response = requests.get(url, timeout=5)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "url": url,
            "status": "up" if response.ok else "down",
            "http_status": response.status_code,
            "response_time_ms": round(elapsed_ms, 1),
            "ok": bool(response.ok),
            "error": None,
        }
    except requests.RequestException as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "url": url,
            "status": "down",
            "http_status": None,
            "response_time_ms": round(elapsed_ms, 1),
            "ok": False,
            "error": str(exc),
        }


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/api/check", methods=["POST"])
def api_check():
    """
    Accepts JSON: { "urls": ["https://...", "http://..."] }
    Returns JSON with availability info for each URL.
    """
    data = request.get_json(silent=True) or {}
    urls = data.get("urls") or []

    # De-duplicate while preserving order
    seen = set()
    cleaned_urls = []
    for u in urls:
        u_str = str(u).strip()
        if u_str and u_str not in seen:
            seen.add(u_str)
            cleaned_urls.append(u_str)

    results = [check_website(u) for u in cleaned_urls]
    return jsonify({"results": results})


if __name__ == "__main__":
    # For local development
    app.run(debug=True)

