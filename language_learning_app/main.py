"""
LinguaFlash - A visually stunning language learning app with flashcard system
"""

import json
import random
import os
from pathlib import Path

import customtkinter as ctk
from PIL import Image

# ═══════════════════════════════════════════════════════════════════════════════
# THEME & STYLING - Custom color palette for stunning visuals
# ═══════════════════════════════════════════════════════════════════════════════
COLORS = {
    "bg_dark": "#0f0e17",           # Deep space black
    "bg_card": "#1a1825",           # Elevated card background
    "bg_elevated": "#242230",       # Slightly elevated surfaces
    "accent_primary": "#7c3aed",    # Vibrant violet
    "accent_secondary": "#06b6d4",  # Cyan teal
    "accent_warm": "#f59e0b",       # Amber for highlights
    "accent_success": "#10b981",    # Emerald
    "accent_danger": "#ef4444",     # Coral red
    "text_primary": "#f8fafc",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    "border_subtle": "#2d2a3d",
}

FONTS = {
    "display": ("Segoe UI", 28, "bold"),
    "heading": ("Segoe UI", 20, "bold"),
    "subheading": ("Segoe UI", 16, "bold"),
    "body": ("Segoe UI", 14),
    "caption": ("Segoe UI", 12),
}

DATA_FILE = Path(__file__).parent / "flashcard_data.json"


# ═══════════════════════════════════════════════════════════════════════════════
# DATA LAYER
# ═══════════════════════════════════════════════════════════════════════════════
def load_data():
    """Load flashcards and decks from JSON file."""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # Return sample data for first-time users
    return get_sample_data()


def get_sample_data():
    """Return sample decks and cards for demo."""
    deck_id = "deck_sample_spanish"
    return {
        "decks": {
            deck_id: {
                "name": "Spanish Basics",
                "from_lang": "English",
                "to_lang": "Spanish",
            }
        },
        "cards": {
            deck_id: [
                {"front": "Hello", "back": "Hola"},
                {"front": "Goodbye", "back": "Adiós"},
                {"front": "Thank you", "back": "Gracias"},
                {"front": "Please", "back": "Por favor"},
                {"front": "Yes", "back": "Sí"},
                {"front": "No", "back": "No"},
                {"front": "Water", "back": "Agua"},
                {"front": "Food", "back": "Comida"},
                {"front": "I love you", "back": "Te quiero"},
                {"front": "How are you?", "back": "¿Cómo estás?"},
            ]
        },
    }


def save_data(data):
    """Save flashcards and decks to JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════
class LinguaFlashApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LinguaFlash — Language Learning")
        self.geometry("1100x720")
        self.minsize(900, 600)

        # Set dark theme with custom appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.configure(fg_color=COLORS["bg_dark"])
        self.data = load_data()

        # Track current deck for study mode
        self.current_deck_id = None
        self.study_cards = []
        self.study_index = 0
        self.showing_answer = False
        self.correct_count = 0

        self._setup_ui()

    def _setup_ui(self):
        """Initialize main container and show dashboard."""
        self.main_container = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        self.main_container.pack(fill="both", expand=True, padx=24, pady=24)
        self.show_dashboard()

    def _clear_main(self):
        """Clear all widgets from main container."""
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def _create_header(self, title: str, subtitle: str = None):
        """Create a styled header section."""
        header = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        title_label = ctk.CTkLabel(
            header,
            text=title,
            font=FONTS["display"],
            text_color=COLORS["text_primary"],
        )
        title_label.pack(anchor="w")

        if subtitle:
            sub_label = ctk.CTkLabel(
                header,
                text=subtitle,
                font=FONTS["caption"],
                text_color=COLORS["text_secondary"],
            )
            sub_label.pack(anchor="w", pady=(4, 0))

        return header

    def _create_back_button(self, parent, command):
        """Create a styled back button."""
        btn = ctk.CTkButton(
            parent,
            text="← Back",
            font=FONTS["body"],
            fg_color=COLORS["bg_elevated"],
            hover_color=COLORS["border_subtle"],
            text_color=COLORS["text_secondary"],
            width=100,
            height=36,
            corner_radius=10,
            command=command,
        )
        return btn

    def _create_card_frame(self, parent, **kwargs):
        """Create a visually appealing card container."""
        return ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["border_subtle"],
            **kwargs
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # DASHBOARD
    # ═══════════════════════════════════════════════════════════════════════════
    def show_dashboard(self):
        """Display the main dashboard with deck overview."""
        self._clear_main()

        header = self._create_header(
            "LinguaFlash",
            "Master languages one card at a time"
        )

        # Stats row
        decks = self.data.get("decks", {})
        all_cards = self.data.get("cards", {})
        total_cards = sum(len(c) for c in all_cards.values() if isinstance(c, list))

        stats_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 24))

        stat_cards = [
            ("Decks", str(len(decks)), COLORS["accent_primary"]),
            ("Total Cards", str(total_cards), COLORS["accent_secondary"]),
        ]
        for label, value, color in stat_cards:
            stat = self._create_card_frame(stats_frame)
            stat.pack(side="left", fill="x", expand=True, padx=(0, 16))
            inner = ctk.CTkFrame(stat, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=20, pady=16)
            ctk.CTkLabel(
                inner, text=value, font=("Segoe UI", 24, "bold"),
                text_color=color
            ).pack(anchor="w")
            ctk.CTkLabel(
                inner, text=label, font=FONTS["caption"],
                text_color=COLORS["text_secondary"]
            ).pack(anchor="w")

        # Action buttons
        actions_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(0, 32))

        actions = [
            ("📚 Study Deck", self._show_deck_selector, COLORS["accent_primary"]),
            ("➕ Create Deck", self._show_create_deck, COLORS["accent_secondary"]),
            ("🃏 Add Cards", self._show_add_cards_select, COLORS["accent_warm"]),
        ]
        for text, cmd, color in actions:
            btn = ctk.CTkButton(
                actions_frame,
                text=text,
                font=FONTS["subheading"],
                fg_color=color,
                hover_color=self._darken(color, 0.15),
                height=56,
                corner_radius=14,
                command=cmd,
            )
            btn.pack(side="left", padx=(0, 16), pady=4)

        # Decks list
        decks_label = ctk.CTkLabel(
            self.main_container,
            text="Your Decks",
            font=FONTS["heading"],
            text_color=COLORS["text_primary"],
        )
        decks_label.pack(anchor="w", pady=(24, 12))

        scroll_frame = ctk.CTkScrollableFrame(
            self.main_container,
            fg_color="transparent",
            scrollbar_button_color=COLORS["bg_elevated"],
            scrollbar_button_hover_color=COLORS["border_subtle"],
        )
        scroll_frame.pack(fill="both", expand=True)

        if not decks:
            empty = self._create_card_frame(scroll_frame)
            empty.pack(fill="x", pady=8)
            ctk.CTkLabel(
                empty,
                text="No decks yet. Create your first deck to get started!",
                font=FONTS["body"],
                text_color=COLORS["text_muted"],
            ).pack(pady=24, padx=24)
        else:
            for deck_id, deck in decks.items():
                card_count = len(self.data.get("cards", {}).get(deck_id, []))
                deck_card = self._create_deck_card(
                    scroll_frame, deck_id, deck, card_count
                )
                deck_card.pack(fill="x", pady=8)

    def _create_deck_card(self, parent, deck_id, deck, card_count):
        """Create a deck item card."""
        card = self._create_card_frame(parent)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=16)

        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            left, text=deck.get("name", "Unnamed"), font=FONTS["subheading"],
            text_color=COLORS["text_primary"]
        ).pack(anchor="w")

        lang = deck.get("from_lang", "?") + " → " + deck.get("to_lang", "?")
        ctk.CTkLabel(
            left, text=lang, font=FONTS["caption"],
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            left, text=f"{card_count} cards", font=FONTS["caption"],
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", pady=(2, 0))

        btn_study = ctk.CTkButton(
            inner,
            text="Study",
            font=FONTS["body"],
            fg_color=COLORS["accent_primary"],
            hover_color=self._darken(COLORS["accent_primary"], 0.15),
            width=100,
            height=40,
            corner_radius=10,
            command=lambda: self._start_study(deck_id),
        )
        btn_study.pack(side="right", padx=(0, 8))

        btn_manage = ctk.CTkButton(
            inner,
            text="Add Cards",
            font=FONTS["body"],
            fg_color=COLORS["bg_elevated"],
            hover_color=COLORS["border_subtle"],
            text_color=COLORS["text_secondary"],
            width=100,
            height=40,
            corner_radius=10,
            command=lambda: self._show_add_cards(deck_id),
        )
        btn_manage.pack(side="right")

        return card

    def _darken(self, hex_color: str, factor: float):
        """Darken a hex color by factor (0-1)."""
        hex_color = hex_color.lstrip("#")
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
        return f"#{r:02x}{g:02x}{b:02x}"

    # ═══════════════════════════════════════════════════════════════════════════
    # CREATE DECK
    # ═══════════════════════════════════════════════════════════════════════════
    def _show_create_deck(self):
        """Show create deck form."""
        self._clear_main()

        top = ctk.CTkFrame(self.main_container, fg_color="transparent")
        top.pack(fill="x", pady=(0, 20))
        self._create_back_button(top, self.show_dashboard).pack(side="left")
        self._create_header("Create New Deck", "Add a new language deck").pack(side="left", padx=20)

        form = self._create_card_frame(self.main_container)
        form.pack(fill="x", pady=20)
        form_inner = ctk.CTkFrame(form, fg_color="transparent")
        form_inner.pack(fill="x", padx=32, pady=32)

        ctk.CTkLabel(form_inner, text="Deck Name", font=FONTS["body"], text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 8))
        entry_name = ctk.CTkEntry(form_inner, height=44, corner_radius=10, font=FONTS["body"], placeholder_text="e.g. Spanish Basics")
        entry_name.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(form_inner, text="From Language", font=FONTS["body"], text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 8))
        entry_from = ctk.CTkEntry(form_inner, height=44, corner_radius=10, font=FONTS["body"], placeholder_text="e.g. English")
        entry_from.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(form_inner, text="To Language", font=FONTS["body"], text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 8))
        entry_to = ctk.CTkEntry(form_inner, height=44, corner_radius=10, font=FONTS["body"], placeholder_text="e.g. Spanish")
        entry_to.pack(fill="x", pady=(0, 24))

        def create():
            name = entry_name.get().strip()
            from_lang = entry_from.get().strip() or "Language 1"
            to_lang = entry_to.get().strip() or "Language 2"
            if not name:
                return
            deck_id = f"deck_{len(self.data['decks']) + 1}_{random.randint(1000, 9999)}"
            self.data.setdefault("decks", {})[deck_id] = {
                "name": name,
                "from_lang": from_lang,
                "to_lang": to_lang,
            }
            self.data.setdefault("cards", {})[deck_id] = []
            save_data(self.data)
            self.show_dashboard()

        ctk.CTkButton(
            form_inner, text="Create Deck",
            font=FONTS["subheading"],
            fg_color=COLORS["accent_primary"],
            hover_color=self._darken(COLORS["accent_primary"], 0.15),
            height=48,
            corner_radius=12,
            command=create,
        ).pack(fill="x")

    # ═══════════════════════════════════════════════════════════════════════════
    # DECK SELECTOR (for study)
    # ═══════════════════════════════════════════════════════════════════════════
    def _show_deck_selector(self):
        """Show deck selection for study mode."""
        decks = self.data.get("decks", {})
        if not decks:
            self.show_dashboard()
            return

        self._clear_main()
        top = ctk.CTkFrame(self.main_container, fg_color="transparent")
        top.pack(fill="x", pady=(0, 20))
        self._create_back_button(top, self.show_dashboard).pack(side="left")
        self._create_header("Choose Deck to Study", "Select a deck to start practicing").pack(side="left", padx=20)

        scroll = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        scroll.pack(fill="both", expand=True, pady=20)

        for deck_id, deck in decks.items():
            cards = self.data.get("cards", {}).get(deck_id, [])
            if not cards:
                continue
            card = self._create_card_frame(scroll)
            card.pack(fill="x", pady=8)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=20, pady=16)
            ctk.CTkLabel(inner, text=deck.get("name", "?"), font=FONTS["subheading"], text_color=COLORS["text_primary"]).pack(side="left")
            ctk.CTkLabel(inner, text=f"{len(cards)} cards", font=FONTS["caption"], text_color=COLORS["text_secondary"]).pack(side="left", padx=12)
            ctk.CTkButton(
                inner, text="Study →", font=FONTS["body"],
                fg_color=COLORS["accent_primary"], hover_color=self._darken(COLORS["accent_primary"], 0.15),
                width=100, height=40, corner_radius=10,
                command=lambda d=deck_id: self._start_study(d),
            ).pack(side="right")

    # ═══════════════════════════════════════════════════════════════════════════
    # ADD CARDS - SELECT DECK
    # ═══════════════════════════════════════════════════════════════════════════
    def _show_add_cards_select(self):
        """Show deck selector for adding cards."""
        decks = self.data.get("decks", {})
        if not decks:
            self._show_create_deck()
            return

        self._clear_main()
        top = ctk.CTkFrame(self.main_container, fg_color="transparent")
        top.pack(fill="x", pady=(0, 20))
        self._create_back_button(top, self.show_dashboard).pack(side="left")
        self._create_header("Add Cards", "Choose which deck to add cards to").pack(side="left", padx=20)

        scroll = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        scroll.pack(fill="both", expand=True, pady=20)

        for deck_id, deck in decks.items():
            card = self._create_card_frame(scroll)
            card.pack(fill="x", pady=8)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=20, pady=16)
            ctk.CTkLabel(inner, text=deck.get("name", "?"), font=FONTS["subheading"], text_color=COLORS["text_primary"]).pack(side="left")
            ctk.CTkButton(
                inner, text="Add Cards →", font=FONTS["body"],
                fg_color=COLORS["accent_warm"], hover_color=self._darken(COLORS["accent_warm"], 0.15),
                width=120, height=40, corner_radius=10,
                command=lambda d=deck_id: self._show_add_cards(d),
            ).pack(side="right")

    def _show_add_cards(self, deck_id: str):
        """Show add cards form for a specific deck."""
        self._clear_main()
        self.current_deck_id = deck_id
        deck = self.data["decks"].get(deck_id, {})
        from_lang = deck.get("from_lang", "Front")
        to_lang = deck.get("to_lang", "Back")

        top = ctk.CTkFrame(self.main_container, fg_color="transparent")
        top.pack(fill="x", pady=(0, 20))
        self._create_back_button(top, self.show_dashboard).pack(side="left")
        self._create_header(f"Add Cards to {deck.get('name', 'Deck')}", f"{from_lang} → {to_lang}").pack(side="left", padx=20)

        form = self._create_card_frame(self.main_container)
        form.pack(fill="x", pady=20)
        form_inner = ctk.CTkFrame(form, fg_color="transparent")
        form_inner.pack(fill="x", padx=32, pady=32)

        ctk.CTkLabel(form_inner, text=f"Front ({from_lang})", font=FONTS["body"], text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 8))
        entry_front = ctk.CTkEntry(form_inner, height=44, corner_radius=10, font=FONTS["body"], placeholder_text="Word or phrase")
        entry_front.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(form_inner, text=f"Back ({to_lang})", font=FONTS["body"], text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 8))
        entry_back = ctk.CTkEntry(form_inner, height=44, corner_radius=10, font=FONTS["body"], placeholder_text="Translation")
        entry_back.pack(fill="x", pady=(0, 24))

        def add():
            front = entry_front.get().strip()
            back = entry_back.get().strip()
            if not front or not back:
                return
            self.data.setdefault("cards", {})
            if deck_id not in self.data["cards"]:
                self.data["cards"][deck_id] = []
            self.data["cards"][deck_id].append({"front": front, "back": back})
            save_data(self.data)
            entry_front.delete(0, "end")
            entry_back.delete(0, "end")
            entry_front.focus()

        ctk.CTkButton(
            form_inner, text="Add Card",
            font=FONTS["subheading"],
            fg_color=COLORS["accent_warm"],
            hover_color=self._darken(COLORS["accent_warm"], 0.15),
            height=48,
            corner_radius=12,
            command=add,
        ).pack(fill="x")

    # ═══════════════════════════════════════════════════════════════════════════
    # STUDY MODE
    # ═══════════════════════════════════════════════════════════════════════════
    def _start_study(self, deck_id: str):
        """Start study session for a deck."""
        cards = self.data.get("cards", {}).get(deck_id, [])
        if not cards:
            self.show_dashboard()
            return

        self.current_deck_id = deck_id
        self.study_cards = random.sample(cards, len(cards))
        self.study_index = 0
        self.showing_answer = False
        self.correct_count = 0
        self._show_study_screen()

    def _show_study_screen(self):
        """Display current flashcard in study mode."""
        self._clear_main()

        deck = self.data["decks"].get(self.current_deck_id, {})
        total = len(self.study_cards)
        current = self.study_index + 1

        if self.study_index >= total:
            self._show_study_complete()
            return

        card_data = self.study_cards[self.study_index]
        top = ctk.CTkFrame(self.main_container, fg_color="transparent")
        top.pack(fill="x", pady=(0, 20))
        self._create_back_button(top, lambda: self._confirm_exit_study()).pack(side="left")

        progress_text = f"Card {current} of {total}"
        ctk.CTkLabel(top, text=progress_text, font=FONTS["body"], text_color=COLORS["text_secondary"]).pack(side="right")

        # Progress bar
        progress = current / total
        pb = ctk.CTkProgressBar(
            self.main_container,
            height=8,
            corner_radius=4,
            progress_color=COLORS["accent_primary"],
            fg_color=COLORS["bg_elevated"],
        )
        pb.pack(fill="x", pady=(0, 24))
        pb.set(progress)

        # Flashcard display - large, centered
        flashcard = self._create_card_frame(self.main_container)
        flashcard.pack(fill="both", expand=True, pady=20)
        flashcard_inner = ctk.CTkFrame(flashcard, fg_color="transparent")
        flashcard_inner.pack(fill="both", expand=True, padx=48, pady=48)

        self.card_content_label = ctk.CTkLabel(
            flashcard_inner,
            text=card_data["front"] if not self.showing_answer else card_data["back"],
            font=("Segoe UI", 22, "bold"),
            text_color=COLORS["text_primary"],
            wraplength=700,
            justify="center",
        )
        self.card_content_label.pack(expand=True, fill="both")

        hint = "Click to reveal answer" if not self.showing_answer else f"Translation ({deck.get('to_lang', '')})"
        self.card_hint_label = ctk.CTkLabel(
            flashcard_inner,
            text=hint,
            font=FONTS["caption"],
            text_color=COLORS["text_muted"],
        )
        self.card_hint_label.pack(pady=(0, 8))

        flashcard.bind("<Button-1>", lambda e: self._flip_card())
        flashcard_inner.bind("<Button-1>", lambda e: self._flip_card())
        self.card_content_label.bind("<Button-1>", lambda e: self._flip_card())
        self.card_hint_label.bind("<Button-1>", lambda e: self._flip_card())

        # Buttons
        btn_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=24)

        if self.showing_answer:
            ctk.CTkButton(
                btn_frame,
                text="✗ Again",
                font=FONTS["body"],
                fg_color=COLORS["accent_danger"],
                hover_color=self._darken(COLORS["accent_danger"], 0.15),
                width=120,
                height=48,
                corner_radius=12,
                command=lambda: self._next_card(False),
            ).pack(side="left", padx=4)

            ctk.CTkButton(
                btn_frame,
                text="✓ Got it!",
                font=FONTS["body"],
                fg_color=COLORS["accent_success"],
                hover_color=self._darken(COLORS["accent_success"], 0.15),
                width=120,
                height=48,
                corner_radius=12,
                command=lambda: self._next_card(True),
            ).pack(side="left", padx=4)
        else:
            ctk.CTkButton(
                btn_frame,
                text="Reveal Answer",
                font=FONTS["subheading"],
                fg_color=COLORS["accent_primary"],
                hover_color=self._darken(COLORS["accent_primary"], 0.15),
                width=180,
                height=52,
                corner_radius=12,
                command=self._flip_card,
            ).pack()

    def _flip_card(self):
        """Flip the card to show answer."""
        self.showing_answer = True
        self._show_study_screen()  # Rebuild with answer and rating buttons

    def _next_card(self, correct: bool):
        """Advance to next card."""
        if correct:
            self.correct_count += 1
        self.study_index += 1
        self.showing_answer = False
        self._show_study_screen()

    def _show_study_complete(self):
        """Show study session complete screen."""
        self._clear_main()

        total = len(self.study_cards)
        pct = (self.correct_count / total * 100) if total else 0

        self._create_header("Session Complete! 🎉", "Great job practicing today").pack(pady=(0, 24))

        stats = self._create_card_frame(self.main_container)
        stats.pack(fill="x", pady=20)
        stats_inner = ctk.CTkFrame(stats, fg_color="transparent")
        stats_inner.pack(fill="x", padx=48, pady=48)

        ctk.CTkLabel(stats_inner, text=f"{self.correct_count} / {total} correct", font=("Segoe UI", 28, "bold"), text_color=COLORS["accent_success"]).pack(pady=(0, 8))
        ctk.CTkLabel(stats_inner, text=f"{pct:.0f}% mastery", font=FONTS["subheading"], text_color=COLORS["text_secondary"]).pack(pady=(0, 24))

        ctk.CTkButton(
            stats_inner,
            text="Study Again",
            font=FONTS["subheading"],
            fg_color=COLORS["accent_primary"],
            hover_color=self._darken(COLORS["accent_primary"], 0.15),
            height=52,
            corner_radius=12,
            command=lambda: self._start_study(self.current_deck_id),
        ).pack(pady=(0, 12))

        ctk.CTkButton(
            stats_inner,
            text="Back to Dashboard",
            font=FONTS["body"],
            fg_color=COLORS["bg_elevated"],
            hover_color=COLORS["border_subtle"],
            text_color=COLORS["text_secondary"],
            height=48,
            corner_radius=12,
            command=self.show_dashboard,
        ).pack()

    def _confirm_exit_study(self):
        """Return to dashboard from study."""
        self.show_dashboard()


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = LinguaFlashApp()
    app.mainloop()
