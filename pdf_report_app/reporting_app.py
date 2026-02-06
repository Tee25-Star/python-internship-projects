import csv
import os
from datetime import datetime

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


APP_PRIMARY = "#4C6FFF"
APP_BG_DARK = "#0F172A"
APP_BG_LIGHT = "#111827"
APP_CARD_BG = "#1F2937"
APP_TEXT = "#E5E7EB"
APP_MUTED = "#9CA3AF"


class PDFReportApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Data → PDF Report Studio")
        self.geometry("1100x650")
        self.minsize(900, 550)
        self.configure(bg=APP_BG_DARK)

        self.data = []
        self.headers = []

        self._configure_style()
        self._build_layout()

    # ---------- UI SETUP ----------
    def _configure_style(self) -> None:
        style = ttk.Style(self)
        # Use a modern theme if available
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "App.TFrame",
            background=APP_BG_DARK,
        )
        style.configure(
            "Card.TFrame",
            background=APP_CARD_BG,
            borderwidth=0,
        )
        style.configure(
            "Accent.TButton",
            font=("Segoe UI Semibold", 10),
            foreground="white",
            padding=8,
            background=APP_PRIMARY,
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#3246D3")],
        )
        style.configure(
            "Ghost.TButton",
            font=("Segoe UI", 10),
            foreground=APP_TEXT,
            padding=7,
            background=APP_BG_LIGHT,
            relief="flat",
        )
        style.map(
            "Ghost.TButton",
            background=[("active", "#111827")],
        )
        style.configure(
            "Treeview",
            background=APP_BG_LIGHT,
            fieldbackground=APP_BG_LIGHT,
            foreground=APP_TEXT,
            rowheight=26,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=APP_BG_DARK,
            foreground=APP_TEXT,
            font=("Segoe UI Semibold", 9),
        )
        style.map(
            "Treeview",
            background=[("selected", "#1D4ED8")],
            foreground=[("selected", "white")],
        )

    def _build_layout(self) -> None:
        root = ttk.Frame(self, style="App.TFrame")
        root.pack(fill="both", expand=True)

        # Header
        header = tk.Canvas(
            root,
            height=80,
            highlightthickness=0,
            bd=0,
            bg=APP_BG_DARK,
        )
        header.pack(fill="x", side="top")

        # Gradient-esque blocks
        header.create_rectangle(0, 0, 260, 80, fill="#1F2937", outline="")
        header.create_rectangle(260, 0, 560, 80, fill="#111827", outline="")
        header.create_rectangle(560, 0, 1100, 80, fill="#020617", outline="")

        header.create_text(
            30,
            24,
            anchor="w",
            text="Data → PDF Report Studio",
            fill=APP_TEXT,
            font=("Segoe UI Semibold", 16),
        )
        header.create_text(
            30,
            52,
            anchor="w",
            text="Load your data, preview it, and craft beautiful PDF reports.",
            fill=APP_MUTED,
            font=("Segoe UI", 10),
        )

        # Sub header stats card
        sub_header = ttk.Frame(root, style="App.TFrame")
        sub_header.pack(fill="x", padx=20, pady=(10, 0))

        self.status_label = tk.Label(
            sub_header,
            text="No dataset loaded",
            bg=APP_BG_DARK,
            fg=APP_MUTED,
            font=("Segoe UI", 10),
        )
        self.status_label.pack(side="left")

        timestamp_label = tk.Label(
            sub_header,
            text=f"Today · {datetime.now().strftime('%b %d, %Y')}",
            bg=APP_BG_DARK,
            fg=APP_MUTED,
            font=("Segoe UI", 9),
        )
        timestamp_label.pack(side="right")

        # Main content area
        main = ttk.Frame(root, style="App.TFrame")
        main.pack(fill="both", expand=True, padx=20, pady=15)

        left = ttk.Frame(main, style="Card.TFrame")
        left.pack(side="left", fill="y", padx=(0, 10))

        right = ttk.Frame(main, style="Card.TFrame")
        right.pack(side="left", fill="both", expand=True)

        self._build_left_panel(left)
        self._build_table_panel(right)

    def _build_left_panel(self, container: ttk.Frame) -> None:
        for i in range(2):
            container.rowconfigure(i, weight=0)
        container.rowconfigure(3, weight=1)
        container.columnconfigure(0, weight=1)

        title = tk.Label(
            container,
            text="Workflow",
            bg=APP_CARD_BG,
            fg=APP_TEXT,
            font=("Segoe UI Semibold", 12),
            pady=12,
        )
        title.grid(row=0, column=0, sticky="ew")

        description = tk.Label(
            container,
            text="1. Load a CSV file\n2. Inspect the preview\n3. Export a polished PDF report",
            bg=APP_CARD_BG,
            fg=APP_MUTED,
            justify="left",
            font=("Segoe UI", 9),
        )
        description.grid(row=1, column=0, sticky="ew", padx=16)

        buttons_frame = ttk.Frame(container, style="Card.TFrame")
        buttons_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(12, 8))
        buttons_frame.columnconfigure(0, weight=1)

        load_btn = ttk.Button(
            buttons_frame,
            text="Browse CSV…",
            style="Accent.TButton",
            command=self.load_csv,
        )
        load_btn.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        pdf_btn = ttk.Button(
            buttons_frame,
            text="Generate PDF Report",
            style="Ghost.TButton",
            command=self.generate_pdf,
        )
        pdf_btn.grid(row=1, column=0, sticky="ew")

        helper = tk.Label(
            container,
            text="Tip: Numeric columns will automatically get summary statistics in your report.",
            wraplength=220,
            bg=APP_CARD_BG,
            fg=APP_MUTED,
            justify="left",
            font=("Segoe UI", 8),
            pady=8,
        )
        helper.grid(row=3, column=0, sticky="nsew", padx=16, pady=(4, 12))

    def _build_table_panel(self, container: ttk.Frame) -> None:
        container.rowconfigure(1, weight=1)
        container.columnconfigure(0, weight=1)

        header_frame = ttk.Frame(container, style="Card.TFrame")
        header_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 2))
        header_frame.columnconfigure(0, weight=1)

        title = tk.Label(
            header_frame,
            text="Dataset Preview",
            bg=APP_CARD_BG,
            fg=APP_TEXT,
            font=("Segoe UI Semibold", 11),
        )
        title.grid(row=0, column=0, sticky="w")

        self.rows_label = tk.Label(
            header_frame,
            text="0 rows",
            bg=APP_CARD_BG,
            fg=APP_MUTED,
            font=("Segoe UI", 9),
        )
        self.rows_label.grid(row=0, column=1, sticky="e")

        # Table
        table_frame = ttk.Frame(container, style="Card.TFrame")
        table_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            table_frame,
            columns=[],
            show="headings",
            selectmode="browse",
        )
        vsb = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview,
        )
        hsb = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.tree.xview,
        )
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        empty_label = tk.Label(
            table_frame,
            text="Load a CSV file to see a live preview of your data.",
            bg=APP_CARD_BG,
            fg=APP_MUTED,
            font=("Segoe UI", 9),
        )
        empty_label.place(relx=0.5, rely=0.5, anchor="center")
        self.empty_label = empty_label

    # ---------- DATA HANDLING ----------
    def load_csv(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not file_path:
            return

        try:
            with open(file_path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                self.headers = reader.fieldnames or []
                self.data = [row for row in reader]
        except Exception as e:  # noqa: BLE001
            messagebox.showerror(
                "Failed to load CSV",
                f"Could not read file:\n{e}",
            )
            return

        if not self.headers:
            messagebox.showwarning(
                "No headers",
                "The selected CSV file does not appear to contain a header row.",
            )

        self._refresh_table()
        file_name = os.path.basename(file_path)
        self.status_label.configure(text=f"Loaded dataset: {file_name}")

    def _refresh_table(self) -> None:
        # Clear existing table structure
        for col in self.tree["columns"]:
            self.tree.heading(col, text="")
            self.tree.column(col, width=0)
        self.tree.delete(*self.tree.get_children())

        if not self.data:
            self.tree["columns"] = []
            self.empty_label.lift()
            self.rows_label.configure(text="0 rows")
            return

        self.empty_label.lower()

        self.tree["columns"] = self.headers
        for header in self.headers:
            self.tree.heading(header, text=header)
            self.tree.column(header, anchor="w", width=max(80, len(header) * 9))

        for row in self.data[:500]:  # soft cap to keep UI snappy
            values = [row.get(header, "") for header in self.headers]
            self.tree.insert("", "end", values=values)

        total_rows = len(self.data)
        suffix = "rows" if total_rows != 1 else "row"
        self.rows_label.configure(text=f"{total_rows} {suffix}")

    # ---------- PDF GENERATION ----------
    def generate_pdf(self) -> None:
        if not self.data:
            messagebox.showinfo(
                "No data",
                "Load a CSV file before generating a PDF report.",
            )
            return

        default_name = f"data-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.pdf"
        output_path = filedialog.asksaveasfilename(
            title="Save PDF report as",
            defaultextension=".pdf",
            initialfile=default_name,
            filetypes=[("PDF files", "*.pdf")],
        )
        if not output_path:
            return

        try:
            self._build_pdf(output_path)
        except Exception as e:  # noqa: BLE001
            messagebox.showerror(
                "Failed to generate PDF",
                f"An error occurred while generating the PDF:\n{e}",
            )
            return

        messagebox.showinfo(
            "Report created",
            f"PDF report successfully generated:\n{output_path}",
        )

    def _build_pdf(self, output_path: str) -> None:
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            title="Data Report",
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "Title",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            textColor=colors.HexColor(APP_PRIMARY),
            alignment=0,
        )
        meta_style = ParagraphStyle(
            "Meta",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.grey,
        )
        heading_style = ParagraphStyle(
            "Heading",
            parent=styles["Heading2"],
            textColor=colors.HexColor("#111827"),
            fontSize=13,
        )

        story = []

        story.append(Paragraph("Data Report", title_style))
        story.append(
            Paragraph(
                f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}",
                meta_style,
            )
        )
        story.append(Spacer(1, 16))

        # High-level summary
        story.append(Paragraph("Overview", heading_style))
        story.append(Spacer(1, 6))

        total_rows = len(self.data)
        total_cols = len(self.headers)
        summary_items = [
            f"Total rows: <b>{total_rows}</b>",
            f"Total columns: <b>{total_cols}</b>",
        ]

        numeric_stats = self._compute_numeric_stats()
        if numeric_stats:
            bullet_lines = []
            for col, stats in numeric_stats.items():
                bullet_lines.append(
                    f"&bull; <b>{col}</b>: mean={stats['mean']:.2f}, "
                    f"min={stats['min']:.2f}, max={stats['max']:.2f} "
                    f"(n={stats['count']})"
                )
            stats_html = "<br/>".join(bullet_lines)
            summary_items.append(f"Numeric columns summary:<br/>{stats_html}")

        for item in summary_items:
            story.append(Paragraph(item, styles["Normal"]))
            story.append(Spacer(1, 2))

        story.append(Spacer(1, 12))

        # Table section
        story.append(Paragraph("Data Table (first 50 rows)", heading_style))
        story.append(Spacer(1, 6))

        table_data = [self.headers]
        for row in self.data[:50]:
            table_data.append([str(row.get(h, "")) for h in self.headers])

        table = Table(table_data, repeatRows=1)

        table_style = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(APP_PRIMARY)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("ALIGN", (0, 0), (-1, 0), "LEFT"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F9FAFB")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("ALIGN", (0, 1), (-1, -1), "LEFT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
        table.setStyle(table_style)

        story.append(table)
        story.append(Spacer(1, 20))

        # Footer note
        story.append(
            Paragraph(
                "This report was generated automatically from your CSV dataset.",
                styles["Italic"],
            )
        )

        doc.build(story)

    def _compute_numeric_stats(self):
        numeric_stats = {}
        for header in self.headers:
            values = []
            for row in self.data:
                cell = row.get(header)
                if cell is None or str(cell).strip() == "":
                    continue
                try:
                    values.append(float(str(cell).replace(",", "")))
                except ValueError:
                    continue

            if not values:
                continue

            count = len(values)
            col_min = min(values)
            col_max = max(values)
            col_mean = sum(values) / count

            numeric_stats[header] = {
                "count": count,
                "min": col_min,
                "max": col_max,
                "mean": col_mean,
            }

        return numeric_stats


def main() -> None:
    app = PDFReportApp()
    app.mainloop()


if __name__ == "__main__":
    main()

