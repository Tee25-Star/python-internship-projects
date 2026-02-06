from __future__ import annotations

import json
import math
import sys
import traceback
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import requests
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCharts import QChart, QChartView, QDateTimeAxis, QLineSeries, QValueAxis


# -----------------------------
# Data + "AI" (tiny regression)
# -----------------------------

OPEN_METEO_GEOCODE = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_FORECAST = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"


def _requests_get(url: str, params: Dict[str, Any], timeout: int = 20) -> Dict[str, Any]:
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()


@dataclass(frozen=True)
class Location:
    name: str
    country: str
    admin1: str
    latitude: float
    longitude: float
    timezone: str

    @property
    def label(self) -> str:
        parts = [self.name]
        if self.admin1:
            parts.append(self.admin1)
        if self.country:
            parts.append(self.country)
        return ", ".join([p for p in parts if p])


def geocode_city(query: str) -> Location:
    data = _requests_get(
        OPEN_METEO_GEOCODE,
        params={
            "name": query,
            "count": 1,
            "language": "en",
            "format": "json",
        },
    )
    results = data.get("results") or []
    if not results:
        raise ValueError(f"No results found for '{query}'. Try a nearby major city name.")

    r0 = results[0]
    return Location(
        name=str(r0.get("name") or query),
        country=str(r0.get("country") or ""),
        admin1=str(r0.get("admin1") or ""),
        latitude=float(r0["latitude"]),
        longitude=float(r0["longitude"]),
        timezone=str(r0.get("timezone") or "auto"),
    )


def fetch_forecast(loc: Location, forecast_days: int = 7) -> Dict[str, Any]:
    return _requests_get(
        OPEN_METEO_FORECAST,
        params={
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "timezone": "auto",
            "forecast_days": forecast_days,
            "current": ",".join(
                [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "precipitation",
                    "weather_code",
                    "wind_speed_10m",
                ]
            ),
            "hourly": ",".join(
                [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "wind_speed_10m",
                    "surface_pressure",
                    "cloud_cover",
                    "weather_code",
                ]
            ),
            "daily": ",".join(
                [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_probability_max",
                    "weather_code",
                ]
            ),
        },
    )


def fetch_archive(loc: Location, days_back: int = 21) -> Dict[str, Any]:
    end = date.today()
    start = end - timedelta(days=days_back)
    return _requests_get(
        OPEN_METEO_ARCHIVE,
        params={
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "timezone": "auto",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "hourly": ",".join(
                [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "wind_speed_10m",
                    "surface_pressure",
                    "cloud_cover",
                ]
            ),
        },
    )


def _safe_arr(d: Dict[str, Any], key: str) -> np.ndarray:
    v = (d.get(key) or [])
    return np.asarray(v, dtype=float)


def _time_features(dt_list: List[str]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    # Returns hour_sin, hour_cos, doy_sin, doy_cos
    hours: List[int] = []
    doys: List[int] = []
    for ts in dt_list:
        # Open-Meteo uses ISO local times like "2026-01-28T15:00"
        dt = datetime.fromisoformat(ts)
        hours.append(dt.hour)
        doys.append(dt.timetuple().tm_yday)

    h = np.asarray(hours, dtype=float)
    d = np.asarray(doys, dtype=float)

    hour_sin = np.sin(2 * np.pi * (h / 24.0))
    hour_cos = np.cos(2 * np.pi * (h / 24.0))
    doy_sin = np.sin(2 * np.pi * (d / 365.25))
    doy_cos = np.cos(2 * np.pi * (d / 365.25))
    return hour_sin, hour_cos, doy_sin, doy_cos


def _build_X(times: List[str], rh: np.ndarray, wind: np.ndarray, pressure: np.ndarray, cloud: np.ndarray) -> np.ndarray:
    hs, hc, ds, dc = _time_features(times)

    # Light normalization to keep the numeric scale stable.
    rh_n = np.nan_to_num(rh / 100.0, nan=0.0)
    wind_n = np.nan_to_num(wind / 20.0, nan=0.0)  # typical <= 20 m/s
    pressure_n = np.nan_to_num((pressure - 1013.25) / 20.0, nan=0.0)
    cloud_n = np.nan_to_num(cloud / 100.0, nan=0.0)

    bias = np.ones_like(rh_n)
    X = np.column_stack([bias, hs, hc, ds, dc, rh_n, wind_n, pressure_n, cloud_n])
    return X.astype(float)


@dataclass(frozen=True)
class AiFit:
    weights: np.ndarray
    rmse: float


def fit_ai_temperature_model(archive_hourly: Dict[str, Any]) -> Optional[AiFit]:
    times = (archive_hourly.get("time") or [])
    if len(times) < 48:
        return None

    y = _safe_arr(archive_hourly, "temperature_2m")
    rh = _safe_arr(archive_hourly, "relative_humidity_2m")
    wind = _safe_arr(archive_hourly, "wind_speed_10m")
    pressure = _safe_arr(archive_hourly, "surface_pressure")
    cloud = _safe_arr(archive_hourly, "cloud_cover")

    n = min(len(times), len(y), len(rh), len(wind), len(pressure), len(cloud))
    if n < 48:
        return None

    times = times[:n]
    y = y[:n]
    X = _build_X(times, rh[:n], wind[:n], pressure[:n], cloud[:n])

    # Drop rows where the target is missing.
    mask = np.isfinite(y)
    X = X[mask]
    y = y[mask]
    if len(y) < 48:
        return None

    # Ridge regression closed form: (X^T X + λI)^-1 X^T y
    lam = 1.25
    XtX = X.T @ X
    I = np.eye(X.shape[1])
    w = np.linalg.solve(XtX + lam * I, X.T @ y)

    preds = X @ w
    rmse = float(np.sqrt(np.mean((preds - y) ** 2)))
    return AiFit(weights=w, rmse=rmse)


def ai_predict_temperature(fit: AiFit, forecast_hourly: Dict[str, Any]) -> np.ndarray:
    times = (forecast_hourly.get("time") or [])
    rh = _safe_arr(forecast_hourly, "relative_humidity_2m")
    wind = _safe_arr(forecast_hourly, "wind_speed_10m")
    pressure = _safe_arr(forecast_hourly, "surface_pressure")
    cloud = _safe_arr(forecast_hourly, "cloud_cover")

    n = min(len(times), len(rh), len(wind), len(pressure), len(cloud))
    if n == 0:
        return np.asarray([], dtype=float)

    X = _build_X(times[:n], rh[:n], wind[:n], pressure[:n], cloud[:n])
    return (X @ fit.weights).astype(float)


# -----------------------------
# UI helpers
# -----------------------------


def weather_label(code: int) -> str:
    # Open-Meteo weather code mapping (compact)
    if code == 0:
        return "Clear"
    if code in (1, 2, 3):
        return "Partly cloudy" if code == 1 else ("Cloudy" if code == 2 else "Overcast")
    if code in (45, 48):
        return "Fog"
    if code in (51, 53, 55, 56, 57):
        return "Drizzle"
    if code in (61, 63, 65, 66, 67):
        return "Rain"
    if code in (71, 73, 75, 77):
        return "Snow"
    if code in (80, 81, 82):
        return "Rain showers"
    if code in (85, 86):
        return "Snow showers"
    if code in (95, 96, 99):
        return "Thunderstorm"
    return "Unknown"


def theme_for_weather(code: int) -> Tuple[str, str]:
    # Returns (accent, background gradient)
    if code == 0:
        return "#79C8FF", "qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0B1220, stop:1 #0B3B7A)"
    if code in (1, 2, 3):
        return "#B9D4FF", "qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0B1220, stop:1 #2A3A5C)"
    if code in (61, 63, 65, 80, 81, 82):
        return "#B48CFF", "qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0B1220, stop:1 #2B1B4B)"
    if code in (71, 73, 75, 85, 86):
        return "#CFF6FF", "qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #06101A, stop:1 #12324B)"
    if code in (95, 96, 99):
        return "#FF8AAE", "qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #120915, stop:1 #3A0B2E)"
    return "#7BE6C7", "qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0B1220, stop:1 #123A3A)"


def c_to_f(c: float) -> float:
    return (c * 9.0 / 5.0) + 32.0


def format_temp(value_c: float, use_f: bool) -> str:
    if not math.isfinite(value_c):
        return "—"
    if use_f:
        return f"{c_to_f(value_c):.0f}°F"
    return f"{value_c:.0f}°C"


class GlassCard(QtWidgets.QFrame):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.setObjectName("GlassCard")
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setAutoFillBackground(False)
        effect = QtWidgets.QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(28)
        effect.setOffset(0, 10)
        effect.setColor(QtGui.QColor(0, 0, 0, 180))
        self.setGraphicsEffect(effect)


class DotLoadingLabel(QtWidgets.QLabel):
    def __init__(self, text: str = "Loading", parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self._base = text
        self._i = 0
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.setInterval(250)

    def start(self):
        self._i = 0
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self.setText(self._base)

    def _tick(self):
        self._i = (self._i + 1) % 4
        self.setText(self._base + "." * self._i)


class WorkerSignals(QtCore.QObject):
    result = QtCore.Signal(object)
    error = QtCore.Signal(str)


class Worker(QtCore.QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @QtCore.Slot()
    def run(self):
        try:
            res = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(res)
        except Exception:
            self.signals.error.emit(traceback.format_exc())


class WeatherApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather — AI‑Enhanced Forecast")
        self.setMinimumSize(1100, 720)

        self._use_f = False
        self._thread_pool = QtCore.QThreadPool.globalInstance()

        self._cache_path = Path(__file__).resolve().parent / "cache.json"
        self._active_location: Optional[Location] = None
        self._last_payload: Optional[Dict[str, Any]] = None

        self._build_ui()
        self._apply_theme(accent="#79C8FF", bg_gradient=theme_for_weather(0)[1])

        # Default city (fast first impression)
        self.city_input.setText("Lagos")
        self._start_refresh()

    # ---------- UI ----------
    def _build_ui(self):
        root = QtWidgets.QWidget()
        self.setCentralWidget(root)
        root.setObjectName("Root")

        outer = QtWidgets.QVBoxLayout(root)
        outer.setContentsMargins(18, 18, 18, 18)
        outer.setSpacing(14)

        # Top bar
        top = QtWidgets.QHBoxLayout()
        top.setSpacing(12)

        title_box = QtWidgets.QVBoxLayout()
        title_box.setSpacing(0)
        self.title = QtWidgets.QLabel(" Weather")
        self.title.setObjectName("AppTitle")
        self.subtitle = QtWidgets.QLabel("AI‑enhanced forecast overlay • Open‑Meteo")
        self.subtitle.setObjectName("AppSubtitle")
        title_box.addWidget(self.title)
        title_box.addWidget(self.subtitle)
        top.addLayout(title_box, stretch=1)

        self.city_input = QtWidgets.QLineEdit()
        self.city_input.setPlaceholderText("Search city… (e.g., Lagos, London, Nairobi)")
        self.city_input.setObjectName("CityInput")
        self.city_input.returnPressed.connect(self._start_refresh)
        top.addWidget(self.city_input, stretch=2)

        self.search_btn = QtWidgets.QPushButton("Search")
        self.search_btn.setObjectName("PrimaryButton")
        self.search_btn.clicked.connect(self._start_refresh)
        top.addWidget(self.search_btn)

        self.unit_btn = QtWidgets.QPushButton("°C")
        self.unit_btn.setObjectName("GhostButton")
        self.unit_btn.clicked.connect(self._toggle_units)
        top.addWidget(self.unit_btn)

        outer.addLayout(top)

        # Main grid
        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        outer.addLayout(grid, stretch=1)

        # Left: current card
        self.current_card = GlassCard()
        self.current_card_layout = QtWidgets.QVBoxLayout(self.current_card)
        self.current_card_layout.setContentsMargins(18, 18, 18, 18)
        self.current_card_layout.setSpacing(10)

        self.location_label = QtWidgets.QLabel("—")
        self.location_label.setObjectName("LocationLabel")
        self.current_card_layout.addWidget(self.location_label)

        temp_row = QtWidgets.QHBoxLayout()
        temp_row.setSpacing(10)

        self.big_temp = QtWidgets.QLabel("—°")
        self.big_temp.setObjectName("BigTemp")
        temp_row.addWidget(self.big_temp, stretch=1)

        self.condition = QtWidgets.QLabel("—")
        self.condition.setObjectName("ConditionLabel")
        self.condition.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        temp_row.addWidget(self.condition, stretch=1)
        self.current_card_layout.addLayout(temp_row)

        chips = QtWidgets.QHBoxLayout()
        chips.setSpacing(10)
        self.chip_feels = QtWidgets.QLabel("Feels like —")
        self.chip_wind = QtWidgets.QLabel("Wind —")
        self.chip_hum = QtWidgets.QLabel("Humidity —")
        for w in (self.chip_feels, self.chip_wind, self.chip_hum):
            w.setObjectName("Chip")
            w.setMinimumHeight(30)
            w.setAlignment(QtCore.Qt.AlignCenter)
            chips.addWidget(w, stretch=1)
        self.current_card_layout.addLayout(chips)

        self.ai_badge = QtWidgets.QLabel("AI overlay: —")
        self.ai_badge.setObjectName("AiBadge")
        self.current_card_layout.addWidget(self.ai_badge)

        self.loading = DotLoadingLabel("Loading")
        self.loading.setObjectName("LoadingLabel")
        self.loading.hide()
        self.current_card_layout.addWidget(self.loading)

        self.error_box = QtWidgets.QLabel("")
        self.error_box.setObjectName("ErrorLabel")
        self.error_box.setWordWrap(True)
        self.error_box.hide()
        self.current_card_layout.addWidget(self.error_box)

        self.current_card_layout.addStretch(1)
        grid.addWidget(self.current_card, 0, 0)

        # Right: chart card
        self.chart_card = GlassCard()
        chart_layout = QtWidgets.QVBoxLayout(self.chart_card)
        chart_layout.setContentsMargins(14, 14, 14, 14)
        chart_layout.setSpacing(10)

        header = QtWidgets.QHBoxLayout()
        self.chart_title = QtWidgets.QLabel("Next 48 hours")
        self.chart_title.setObjectName("SectionTitle")
        header.addWidget(self.chart_title)
        header.addStretch(1)
        self.legend_hint = QtWidgets.QLabel("Model vs AI‑Blend")
        self.legend_hint.setObjectName("LegendHint")
        header.addWidget(self.legend_hint)
        chart_layout.addLayout(header)

        self.chart = QChart()
        self.chart.setBackgroundVisible(False)
        self.chart.legend().hide()

        self.series_model = QLineSeries()
        self.series_model.setName("Model")
        self.series_ai = QLineSeries()
        self.series_ai.setName("AI‑Blend")

        self.chart.addSeries(self.series_model)
        self.chart.addSeries(self.series_ai)

        self.axis_x = QDateTimeAxis()
        self.axis_x.setFormat("ddd HH:mm")
        self.axis_x.setTickCount(6)
        self.axis_x.setLabelsColor(QtGui.QColor("#C7D2FE"))

        self.axis_y = QValueAxis()
        self.axis_y.setLabelsColor(QtGui.QColor("#C7D2FE"))
        self.axis_y.setGridLineColor(QtGui.QColor(255, 255, 255, 30))

        self.chart.addAxis(self.axis_x, QtCore.Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, QtCore.Qt.AlignLeft)
        self.series_model.attachAxis(self.axis_x)
        self.series_model.attachAxis(self.axis_y)
        self.series_ai.attachAxis(self.axis_x)
        self.series_ai.attachAxis(self.axis_y)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.chart_view.setObjectName("ChartView")
        chart_layout.addWidget(self.chart_view, stretch=1)

        grid.addWidget(self.chart_card, 0, 1)

        # Bottom: daily forecast row
        self.daily_card = GlassCard()
        daily_layout = QtWidgets.QVBoxLayout(self.daily_card)
        daily_layout.setContentsMargins(14, 14, 14, 14)
        daily_layout.setSpacing(10)

        daily_header = QtWidgets.QHBoxLayout()
        daily_title = QtWidgets.QLabel("7‑Day Outlook")
        daily_title.setObjectName("SectionTitle")
        daily_header.addWidget(daily_title)
        daily_header.addStretch(1)
        self.updated_label = QtWidgets.QLabel("—")
        self.updated_label.setObjectName("Muted")
        daily_header.addWidget(self.updated_label)
        daily_layout.addLayout(daily_header)

        self.daily_scroll = QtWidgets.QScrollArea()
        self.daily_scroll.setWidgetResizable(True)
        self.daily_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.daily_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.daily_scroll.setObjectName("DailyScroll")

        self.daily_inner = QtWidgets.QWidget()
        self.daily_row = QtWidgets.QHBoxLayout(self.daily_inner)
        self.daily_row.setContentsMargins(2, 2, 2, 2)
        self.daily_row.setSpacing(10)
        self.daily_scroll.setWidget(self.daily_inner)
        daily_layout.addWidget(self.daily_scroll)

        grid.addWidget(self.daily_card, 1, 0, 1, 2)

        self._apply_styles()

    def _apply_styles(self):
        self.setStyleSheet(
            """
            QWidget#Root {
                background: transparent;
            }
            QLabel {
                color: #E9EEFF;
                font-family: "Segoe UI";
            }
            QLabel#AppTitle {
                font-size: 26px;
                font-weight: 800;
                letter-spacing: 0.5px;
            }
            QLabel#AppSubtitle {
                font-size: 12px;
                color: rgba(233, 238, 255, 0.70);
            }
            QLineEdit#CityInput {
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.14);
                border-radius: 14px;
                padding: 10px 12px;
                font-size: 13px;
            }
            QLineEdit#CityInput:focus {
                border: 1px solid rgba(121,200,255,0.85);
                background: rgba(255,255,255,0.10);
            }
            QPushButton#PrimaryButton {
                background: rgba(121,200,255,0.95);
                color: #0B1220;
                border: none;
                border-radius: 14px;
                padding: 10px 16px;
                font-weight: 800;
            }
            QPushButton#PrimaryButton:hover {
                background: rgba(151,216,255,0.98);
            }
            QPushButton#GhostButton {
                background: rgba(255,255,255,0.07);
                border: 1px solid rgba(255,255,255,0.14);
                border-radius: 14px;
                padding: 10px 14px;
                font-weight: 700;
            }
            QFrame#GlassCard {
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.14);
                border-radius: 18px;
            }
            QLabel#LocationLabel {
                font-size: 14px;
                color: rgba(233,238,255,0.80);
                font-weight: 650;
            }
            QLabel#BigTemp {
                font-size: 62px;
                font-weight: 900;
                letter-spacing: -1px;
            }
            QLabel#ConditionLabel {
                font-size: 16px;
                color: rgba(233,238,255,0.85);
                font-weight: 700;
            }
            QLabel#Chip {
                background: rgba(0,0,0,0.18);
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 12px;
                padding: 6px 10px;
                font-size: 12px;
                color: rgba(233,238,255,0.90);
            }
            QLabel#AiBadge {
                background: rgba(0,0,0,0.22);
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 12px;
                padding: 8px 10px;
                font-size: 12px;
                color: rgba(233,238,255,0.88);
            }
            QLabel#SectionTitle {
                font-size: 14px;
                font-weight: 800;
                color: rgba(233,238,255,0.92);
            }
            QLabel#LegendHint {
                font-size: 12px;
                color: rgba(233,238,255,0.65);
            }
            QLabel#Muted {
                font-size: 12px;
                color: rgba(233,238,255,0.60);
            }
            QLabel#LoadingLabel {
                font-size: 12px;
                color: rgba(233,238,255,0.75);
            }
            QLabel#ErrorLabel {
                font-size: 12px;
                color: #FFB4C6;
                background: rgba(255, 17, 102, 0.12);
                border: 1px solid rgba(255, 180, 198, 0.35);
                border-radius: 12px;
                padding: 10px 10px;
            }
            QChartView#ChartView {
                background: transparent;
            }
            QScrollArea#DailyScroll {
                background: transparent;
                border: none;
            }
            """
        )

    def _apply_theme(self, accent: str, bg_gradient: str):
        # Set app background + dynamic accent
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor("#0B1220"))
        self.setPalette(palette)

        self.centralWidget().setStyleSheet(
            self.centralWidget().styleSheet()
            + f"\nQWidget#Root {{ background: {bg_gradient}; }}\n"
        )

        # Accent-tint the search button + chart lines
        self.search_btn.setStyleSheet(
            self.search_btn.styleSheet()
            + f"\nQPushButton#PrimaryButton {{ background: {accent}; color: #0B1220; }}\n"
        )
        pen_model = QtGui.QPen(QtGui.QColor(accent))
        pen_model.setWidthF(2.6)
        pen_ai = QtGui.QPen(QtGui.QColor("#7BE6C7"))
        pen_ai.setWidthF(2.6)
        self.series_model.setPen(pen_model)
        self.series_ai.setPen(pen_ai)

    # ---------- Actions ----------
    def _toggle_units(self):
        self._use_f = not self._use_f
        self.unit_btn.setText("°F" if self._use_f else "°C")
        if self._last_payload:
            self._render(self._last_payload)

    def _set_loading(self, loading: bool):
        self.search_btn.setEnabled(not loading)
        self.city_input.setEnabled(not loading)
        if loading:
            self.error_box.hide()
            self.loading.show()
            self.loading.start()
        else:
            self.loading.stop()
            self.loading.hide()

    def _start_refresh(self):
        q = (self.city_input.text() or "").strip()
        if not q:
            return

        self._set_loading(True)
        worker = Worker(self._fetch_all, q)
        worker.signals.result.connect(self._on_fetch_ok)
        worker.signals.error.connect(self._on_fetch_err)
        self._thread_pool.start(worker)

    def _fetch_all(self, query: str) -> Dict[str, Any]:
        loc = geocode_city(query)
        forecast = fetch_forecast(loc)
        archive = fetch_archive(loc)
        payload = {"location": loc.__dict__, "forecast": forecast, "archive": archive}
        try:
            self._cache_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
        return payload

    def _on_fetch_ok(self, payload: Dict[str, Any]):
        self._set_loading(False)
        self._last_payload = payload
        self._render(payload)

    def _on_fetch_err(self, tb: str):
        self._set_loading(False)
        self.error_box.setText(
            "Couldn’t load live weather right now.\n"
            "If you’re offline, the app will try to show the last cached data.\n\n"
            + tb.splitlines()[-1]
        )
        self.error_box.show()

        # Fallback: cached payload
        try:
            if self._cache_path.exists():
                payload = json.loads(self._cache_path.read_text(encoding="utf-8"))
                self._last_payload = payload
                self._render(payload)
        except Exception:
            pass

    # ---------- Rendering ----------
    def _render(self, payload: Dict[str, Any]):
        loc_d = payload.get("location") or {}
        loc = Location(
            name=str(loc_d.get("name") or ""),
            country=str(loc_d.get("country") or ""),
            admin1=str(loc_d.get("admin1") or ""),
            latitude=float(loc_d.get("latitude") or 0.0),
            longitude=float(loc_d.get("longitude") or 0.0),
            timezone=str(loc_d.get("timezone") or "auto"),
        )
        self._active_location = loc
        self.location_label.setText(loc.label)

        forecast = payload.get("forecast") or {}
        archive = payload.get("archive") or {}

        current = forecast.get("current") or {}
        code = int(current.get("weather_code") or 0)
        accent, bg = theme_for_weather(code)
        self._apply_theme(accent=accent, bg_gradient=bg)

        temp_c = float(current.get("temperature_2m") or float("nan"))
        feels_c = float(current.get("apparent_temperature") or float("nan"))
        rh = float(current.get("relative_humidity_2m") or float("nan"))
        wind = float(current.get("wind_speed_10m") or float("nan"))

        self.big_temp.setText(format_temp(temp_c, self._use_f))
        self.condition.setText(weather_label(code))
        self.chip_feels.setText(f"Feels like {format_temp(feels_c, self._use_f)}")
        self.chip_wind.setText("Wind —" if not math.isfinite(wind) else f"Wind {wind:.0f} m/s")
        self.chip_hum.setText("Humidity —" if not math.isfinite(rh) else f"Humidity {rh:.0f}%")

        # AI overlay
        ai_fit = fit_ai_temperature_model((archive.get("hourly") or {}))
        hourly = (forecast.get("hourly") or {})
        times = hourly.get("time") or []
        model_temp = _safe_arr(hourly, "temperature_2m")

        ai_temp = None
        ai_blend = None
        ai_rmse = None
        if ai_fit is not None and len(times) > 0:
            ai_pred = ai_predict_temperature(ai_fit, hourly)
            n = min(len(model_temp), len(ai_pred))
            ai_temp = ai_pred[:n]
            model_temp = model_temp[:n]
            ai_blend = (0.70 * model_temp) + (0.30 * ai_temp)
            ai_rmse = ai_fit.rmse

        self._render_chart(times, model_temp, ai_blend)
        self._render_daily(forecast.get("daily") or {})

        if ai_blend is None or ai_rmse is None:
            self.ai_badge.setText("AI overlay: unavailable (not enough history yet)")
        else:
            # Lower RMSE => higher confidence (simple heuristic)
            conf = max(0.15, min(0.95, 1.0 - (ai_rmse / 6.0)))
            self.ai_badge.setText(f"AI overlay: blended • confidence {conf*100:.0f}% • fit RMSE {ai_rmse:.1f}°C")

        self.updated_label.setText(f"Updated {datetime.now().strftime('%a %H:%M')}")

    def _render_chart(self, times: List[str], model_temp_c: np.ndarray, ai_blend_c: Optional[np.ndarray]):
        self.series_model.clear()
        self.series_ai.clear()

        if not times or len(model_temp_c) == 0:
            return

        # Plot next 48 hours
        max_points = min(len(times), len(model_temp_c), 48)
        xs: List[QtCore.QDateTime] = []
        vals: List[float] = []
        vals_ai: List[float] = []

        for i in range(max_points):
            dt = datetime.fromisoformat(times[i])
            qdt = QtCore.QDateTime(dt)
            xs.append(qdt)

            v = float(model_temp_c[i])
            v_plot = c_to_f(v) if self._use_f else v
            vals.append(v_plot)
            self.series_model.append(qdt.toMSecsSinceEpoch(), v_plot)

            if ai_blend_c is not None and i < len(ai_blend_c):
                va = float(ai_blend_c[i])
                va_plot = c_to_f(va) if self._use_f else va
                vals_ai.append(va_plot)
                self.series_ai.append(qdt.toMSecsSinceEpoch(), va_plot)

        # Axis ranges
        self.axis_x.setMin(xs[0])
        self.axis_x.setMax(xs[-1])

        combined = vals + (vals_ai if vals_ai else [])
        ymin = min(combined) - 2.0
        ymax = max(combined) + 2.0
        self.axis_y.setRange(ymin, ymax)
        self.axis_y.setTitleText("°F" if self._use_f else "°C")
        self.axis_y.setTitleBrush(QtGui.QBrush(QtGui.QColor("#C7D2FE")))

    def _clear_daily_cards(self):
        while self.daily_row.count():
            item = self.daily_row.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    def _render_daily(self, daily: Dict[str, Any]):
        self._clear_daily_cards()

        times = daily.get("time") or []
        tmax = daily.get("temperature_2m_max") or []
        tmin = daily.get("temperature_2m_min") or []
        pmax = daily.get("precipitation_probability_max") or []
        wcode = daily.get("weather_code") or []

        n = min(len(times), len(tmax), len(tmin), len(pmax), len(wcode), 7)
        for i in range(n):
            card = QtWidgets.QFrame()
            card.setObjectName("MiniDayCard")
            card.setFixedWidth(150)
            card.setStyleSheet(
                """
                QFrame#MiniDayCard {
                    background: rgba(0,0,0,0.16);
                    border: 1px solid rgba(255,255,255,0.10);
                    border-radius: 16px;
                }
                """
            )
            lay = QtWidgets.QVBoxLayout(card)
            lay.setContentsMargins(12, 12, 12, 12)
            lay.setSpacing(6)

            dt = date.fromisoformat(times[i])
            day = QtWidgets.QLabel(dt.strftime("%a"))
            day.setObjectName("DayName")
            day.setStyleSheet("font-weight: 900; font-size: 13px; color: rgba(233,238,255,0.92);")

            desc = QtWidgets.QLabel(weather_label(int(wcode[i])))
            desc.setWordWrap(True)
            desc.setStyleSheet("font-size: 11px; color: rgba(233,238,255,0.70);")

            hi = float(tmax[i]) if tmax[i] is not None else float("nan")
            lo = float(tmin[i]) if tmin[i] is not None else float("nan")
            temps = QtWidgets.QLabel(f"{format_temp(hi, self._use_f)}  /  {format_temp(lo, self._use_f)}")
            temps.setStyleSheet("font-size: 13px; font-weight: 800;")

            rain = QtWidgets.QLabel(f"Rain {float(pmax[i]):.0f}%")
            rain.setStyleSheet("font-size: 11px; color: rgba(199,210,254,0.85);")

            lay.addWidget(day)
            lay.addWidget(desc)
            lay.addStretch(1)
            lay.addWidget(temps)
            lay.addWidget(rain)

            self.daily_row.addWidget(card)

        self.daily_row.addStretch(1)


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Aurora Weather")
    app.setOrganizationName("AuroraLabs")

    # Smoother fonts on Windows
    font = app.font()
    font.setFamily("Segoe UI")
    app.setFont(font)

    w = WeatherApp()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

