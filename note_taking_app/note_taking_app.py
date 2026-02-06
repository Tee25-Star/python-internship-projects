import customtkinter as ctk
from tkinter import filedialog, messagebox
import json
import os
from datetime import datetime
from PIL import Image, ImageTk
import easyocr
import threading
import cv2
import numpy as np

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class NoteTakingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Note-Taking System with OCR")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Initialize OCR reader (lazy loading)
        self.reader = None
        self.ocr_loading = False
        
        # Storage for notes
        self.notes_dir = "notes"
        self.current_note = None
        self.notes_data = {}
        
        # Create notes directory if it doesn't exist
        os.makedirs(self.notes_dir, exist_ok=True)
        self.load_notes()
        
        # Create UI
        self.create_ui()
        
    def create_ui(self):
        # Main container with padding
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left sidebar for note list
        sidebar = ctk.CTkFrame(main_frame, width=300, corner_radius=15)
        sidebar.pack(side="left", fill="y", padx=(0, 15))
        sidebar.pack_propagate(False)
        
        # Sidebar header
        header_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=15)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="My Notes",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack()
        
        # New note button
        new_note_btn = ctk.CTkButton(
            header_frame,
            text="+ New Note",
            command=self.create_new_note,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        new_note_btn.pack(fill="x", pady=(10, 0))
        
        # OCR button
        ocr_btn = ctk.CTkButton(
            header_frame,
            text="Extract Text from Image",
            command=self.open_ocr_dialog,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        ocr_btn.pack(fill="x", pady=(10, 0))
        
        # Search box
        search_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=(15, 0))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search notes...",
            height=35
        )
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", self.filter_notes)
        
        # Notes list scrollable frame
        self.notes_scroll = ctk.CTkScrollableFrame(sidebar, fg_color="transparent")
        self.notes_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Right side - note editor
        editor_frame = ctk.CTkFrame(main_frame, corner_radius=15)
        editor_frame.pack(side="right", fill="both", expand=True)
        
        # Editor header
        editor_header = ctk.CTkFrame(editor_frame, fg_color="transparent", height=60)
        editor_header.pack(fill="x", padx=20, pady=15)
        editor_header.pack_propagate(False)
        
        self.note_title_entry = ctk.CTkEntry(
            editor_header,
            placeholder_text="Note Title",
            height=45,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.note_title_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.note_title_entry.bind("<KeyRelease>", self.save_note_auto)
        
        # Action buttons
        action_frame = ctk.CTkFrame(editor_header, fg_color="transparent")
        action_frame.pack(side="right")
        
        self.save_btn = ctk.CTkButton(
            action_frame,
            text="Save",
            command=self.save_note,
            width=100,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        self.save_btn.pack(side="left", padx=5)
        
        self.delete_btn = ctk.CTkButton(
            action_frame,
            text="Delete",
            command=self.delete_note,
            width=100,
            height=35,
            fg_color="#f44336",
            hover_color="#d32f2f"
        )
        self.delete_btn.pack(side="left", padx=5)
        
        # Date label
        self.date_label = ctk.CTkLabel(
            editor_header,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.date_label.pack(side="left", padx=10)
        
        # Text editor
        text_frame = ctk.CTkFrame(editor_frame, fg_color="transparent")
        text_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.note_text = ctk.CTkTextbox(
            text_frame,
            font=ctk.CTkFont(size=14),
            wrap="word",
            corner_radius=10
        )
        self.note_text.pack(fill="both", expand=True)
        self.note_text.bind("<KeyRelease>", self.save_note_auto)
        
        # Store references
        self.sidebar = sidebar
        self.editor_frame = editor_frame
        
        # Refresh notes list
        self.refresh_notes_list()
        
    def create_new_note(self):
        """Create a new note"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        note_id = f"note_{timestamp}"
        
        self.current_note = note_id
        self.notes_data[note_id] = {
            "title": "Untitled Note",
            "content": "",
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat()
        }
        
        self.load_note_to_editor(note_id)
        self.refresh_notes_list()
        
    def load_note_to_editor(self, note_id):
        """Load a note into the editor"""
        if note_id not in self.notes_data:
            return
            
        self.current_note = note_id
        note = self.notes_data[note_id]
        
        self.note_title_entry.delete(0, "end")
        self.note_title_entry.insert(0, note["title"])
        
        self.note_text.delete("1.0", "end")
        self.note_text.insert("1.0", note["content"])
        
        # Update date label
        modified_date = datetime.fromisoformat(note["modified"])
        self.date_label.configure(text=f"Modified: {modified_date.strftime('%Y-%m-%d %H:%M')}")
        
    def save_note(self):
        """Save the current note"""
        if not self.current_note:
            messagebox.showinfo("Info", "No note selected")
            return
            
        title = self.note_title_entry.get().strip() or "Untitled Note"
        content = self.note_text.get("1.0", "end-1c")
        
        if self.current_note not in self.notes_data:
            self.notes_data[self.current_note] = {
                "created": datetime.now().isoformat()
            }
        
        self.notes_data[self.current_note]["title"] = title
        self.notes_data[self.current_note]["content"] = content
        self.notes_data[self.current_note]["modified"] = datetime.now().isoformat()
        
        # Save to file
        self.save_notes_to_file()
        self.refresh_notes_list()
        messagebox.showinfo("Success", "Note saved successfully!")
        
    def save_note_auto(self, event=None):
        """Auto-save note (debounced)"""
        if self.current_note:
            # Update modified time
            if self.current_note in self.notes_data:
                self.notes_data[self.current_note]["modified"] = datetime.now().isoformat()
                self.save_notes_to_file()
    
    def delete_note(self):
        """Delete the current note"""
        if not self.current_note:
            messagebox.showinfo("Info", "No note selected")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this note?"):
            del self.notes_data[self.current_note]
            self.save_notes_to_file()
            
            # Clear editor
            self.current_note = None
            self.note_title_entry.delete(0, "end")
            self.note_text.delete("1.0", "end")
            self.date_label.configure(text="")
            
            self.refresh_notes_list()
            messagebox.showinfo("Success", "Note deleted successfully!")
    
    def refresh_notes_list(self):
        """Refresh the notes list in sidebar"""
        # Clear existing notes
        for widget in self.notes_scroll.winfo_children():
            widget.destroy()
        
        # Sort notes by modified date
        sorted_notes = sorted(
            self.notes_data.items(),
            key=lambda x: x[1].get("modified", ""),
            reverse=True
        )
        
        # Filter notes based on search
        search_term = self.search_entry.get().lower()
        filtered_notes = [
            (note_id, note) for note_id, note in sorted_notes
            if search_term in note["title"].lower() or search_term in note["content"].lower()
        ]
        
        # Display notes
        for note_id, note in filtered_notes:
            note_frame = ctk.CTkFrame(
                self.notes_scroll,
                corner_radius=10,
                fg_color=("#2b2b2b" if note_id != self.current_note else "#1f538d")
            )
            note_frame.pack(fill="x", pady=5, padx=5)
            
            # Note title
            title_label = ctk.CTkLabel(
                note_frame,
                text=note["title"][:30] + ("..." if len(note["title"]) > 30 else ""),
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            title_label.pack(fill="x", padx=15, pady=(10, 5))
            
            # Note preview
            preview = note["content"][:50] + ("..." if len(note["content"]) > 50 else "")
            preview_label = ctk.CTkLabel(
                note_frame,
                text=preview,
                font=ctk.CTkFont(size=11),
                anchor="w",
                text_color="gray"
            )
            preview_label.pack(fill="x", padx=15, pady=(0, 5))
            
            # Date
            try:
                modified_date = datetime.fromisoformat(note["modified"])
                date_str = modified_date.strftime("%b %d, %Y")
            except:
                date_str = "Unknown"
            
            date_label = ctk.CTkLabel(
                note_frame,
                text=date_str,
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            date_label.pack(side="left", padx=15, pady=(0, 10))
            
            # Click to load note
            def make_loader(nid):
                return lambda e: self.load_note_to_editor(nid)
            
            note_frame.bind("<Button-1>", make_loader(note_id))
            title_label.bind("<Button-1>", make_loader(note_id))
            preview_label.bind("<Button-1>", make_loader(note_id))
            date_label.bind("<Button-1>", make_loader(note_id))
    
    def filter_notes(self, event=None):
        """Filter notes based on search"""
        self.refresh_notes_list()
    
    def load_notes(self):
        """Load notes from file"""
        notes_file = os.path.join(self.notes_dir, "notes.json")
        if os.path.exists(notes_file):
            try:
                with open(notes_file, "r", encoding="utf-8") as f:
                    self.notes_data = json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load notes: {str(e)}")
                self.notes_data = {}
        else:
            self.notes_data = {}
    
    def save_notes_to_file(self):
        """Save notes to file"""
        notes_file = os.path.join(self.notes_dir, "notes.json")
        try:
            with open(notes_file, "w", encoding="utf-8") as f:
                json.dump(self.notes_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save notes: {str(e)}")
    
    def initialize_ocr(self):
        """Initialize OCR reader (lazy loading)"""
        if self.reader is None and not self.ocr_loading:
            self.ocr_loading = True
            try:
                self.reader = easyocr.Reader(['en'], gpu=False)
                self.ocr_loading = False
            except Exception as e:
                self.ocr_loading = False
                messagebox.showerror("Error", f"Failed to initialize OCR: {str(e)}")
                return False
        return self.reader is not None
    
    def open_ocr_dialog(self):
        """Open dialog to select image and extract text"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        # Show loading dialog
        loading_window = ctk.CTkToplevel(self.root)
        loading_window.title("Processing OCR...")
        loading_window.geometry("300x150")
        loading_window.transient(self.root)
        loading_window.grab_set()
        
        loading_label = ctk.CTkLabel(
            loading_window,
            text="Extracting text from image...\nThis may take a moment.",
            font=ctk.CTkFont(size=14)
        )
        loading_label.pack(expand=True)
        
        progress = ctk.CTkProgressBar(loading_window)
        progress.pack(pady=10, padx=20, fill="x")
        progress.set(0.5)
        
        self.root.update()
        
        # Process OCR in thread
        def process_ocr():
            try:
                # Initialize OCR if needed
                if not self.initialize_ocr():
                    loading_window.destroy()
                    return
                
                # Read image
                image = cv2.imread(file_path)
                if image is None:
                    loading_window.destroy()
                    messagebox.showerror("Error", "Failed to load image")
                    return
                
                # Perform OCR
                results = self.reader.readtext(image)
                
                # Extract text
                extracted_text = "\n".join([result[1] for result in results])
                
                loading_window.destroy()
                
                # Show results dialog
                self.show_ocr_results(extracted_text, file_path)
                
            except Exception as e:
                loading_window.destroy()
                messagebox.showerror("Error", f"OCR failed: {str(e)}")
        
        thread = threading.Thread(target=process_ocr, daemon=True)
        thread.start()
    
    def show_ocr_results(self, text, image_path):
        """Show OCR results in a dialog"""
        result_window = ctk.CTkToplevel(self.root)
        result_window.title("OCR Results")
        result_window.geometry("800x600")
        result_window.transient(self.root)
        
        # Header
        header = ctk.CTkFrame(result_window, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=15)
        
        title_label = ctk.CTkLabel(
            header,
            text="Extracted Text",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack()
        
        # Text display
        text_frame = ctk.CTkFrame(result_window, fg_color="transparent")
        text_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        text_display = ctk.CTkTextbox(text_frame, font=ctk.CTkFont(size=13))
        text_display.pack(fill="both", expand=True)
        text_display.insert("1.0", text)
        
        # Buttons
        button_frame = ctk.CTkFrame(result_window, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        def add_to_note():
            if not self.current_note:
                self.create_new_note()
            
            current_content = self.note_text.get("1.0", "end-1c")
            separator = "\n\n--- Extracted from Image ---\n\n" if current_content else ""
            self.note_text.insert("end", separator + text)
            result_window.destroy()
            messagebox.showinfo("Success", "Text added to current note!")
        
        add_btn = ctk.CTkButton(
            button_frame,
            text="Add to Current Note",
            command=add_to_note,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        add_btn.pack(side="left", padx=5)
        
        def create_new():
            self.create_new_note()
            self.note_text.insert("1.0", text)
            result_window.destroy()
            messagebox.showinfo("Success", "New note created with extracted text!")
        
        new_btn = ctk.CTkButton(
            button_frame,
            text="Create New Note",
            command=create_new,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        new_btn.pack(side="left", padx=5)
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            command=result_window.destroy,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="gray",
            hover_color="darkgray"
        )
        close_btn.pack(side="right", padx=5)

def main():
    root = ctk.CTk()
    app = NoteTakingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
