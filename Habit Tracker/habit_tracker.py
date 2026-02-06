import customtkinter as ctk
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List

# Configure appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class HabitTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Habit Tracker")
        self.root.geometry("900x700")
        
        # Data file
        self.data_file = "habits_data.json"
        self.habits = self.load_habits()
        
        # Main container
        self.main_frame = ctk.CTkFrame(root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="?? Habit Tracker",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Add habit section
        self.create_add_habit_section()
        
        # Habits display section
        self.create_habits_display_section()
        
        # Refresh display
        self.refresh_habits_display()
    
    def create_add_habit_section(self):
        """Create the section for adding new habits"""
        add_frame = ctk.CTkFrame(self.main_frame)
        add_frame.pack(fill="x", padx=20, pady=10)
        
        add_label = ctk.CTkLabel(
            add_frame,
            text="Add New Habit",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        add_label.pack(pady=10)
        
        input_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        input_frame.pack(pady=10, padx=20)
        
        self.habit_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Enter habit name (e.g., Exercise, Read, Meditate)",
            width=400,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.habit_entry.pack(side="left", padx=10)
        
        add_button = ctk.CTkButton(
            input_frame,
            text="Add Habit",
            command=self.add_habit,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        add_button.pack(side="left", padx=10)
    
    def create_habits_display_section(self):
        """Create the scrollable frame for displaying habits"""
        display_frame = ctk.CTkFrame(self.main_frame)
        display_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        habits_label = ctk.CTkLabel(
            display_frame,
            text="Your Habits",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        habits_label.pack(pady=15)
        
        # Scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(
            display_frame,
            width=800,
            height=400
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    def add_habit(self):
        """Add a new habit"""
        habit_name = self.habit_entry.get().strip()
        if not habit_name:
            return
        
        if habit_name in self.habits:
            # Show error message
            error_label = ctk.CTkLabel(
                self.scrollable_frame,
                text=f"? '{habit_name}' already exists!",
                font=ctk.CTkFont(size=12),
                text_color="#f44336"
            )
            error_label.pack(pady=5)
            self.root.after(2000, error_label.destroy)
            return
        
        # Add habit with current date as start
        self.habits[habit_name] = {
            "created": datetime.now().strftime("%Y-%m-%d"),
            "completions": [],
            "current_streak": 0,
            "longest_streak": 0
        }
        
        self.save_habits()
        self.habit_entry.delete(0, "end")
        self.refresh_habits_display()
    
    def mark_complete(self, habit_name: str):
        """Mark a habit as complete for today"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        if today in self.habits[habit_name]["completions"]:
            # Already completed today
            return
        
        self.habits[habit_name]["completions"].append(today)
        self.update_streaks(habit_name)
        self.save_habits()
        self.refresh_habits_display()
    
    def mark_incomplete(self, habit_name: str):
        """Remove today's completion"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        if today in self.habits[habit_name]["completions"]:
            self.habits[habit_name]["completions"].remove(today)
            self.update_streaks(habit_name)
            self.save_habits()
            self.refresh_habits_display()
    
    def update_streaks(self, habit_name: str):
        """Update current and longest streaks"""
        completions = sorted(self.habits[habit_name]["completions"])
        if not completions:
            self.habits[habit_name]["current_streak"] = 0
            return
        
        # Calculate current streak
        today = datetime.now()
        current_streak = 0
        check_date = today
        
        for i in range(len(completions)):
            date_str = completions[-(i+1)]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            expected_date = today - timedelta(days=i)
            
            if date_obj.date() == expected_date.date():
                current_streak += 1
            else:
                break
        
        # Calculate longest streak
        longest_streak = 0
        temp_streak = 1
        
        for i in range(1, len(completions)):
            prev_date = datetime.strptime(completions[i-1], "%Y-%m-%d")
            curr_date = datetime.strptime(completions[i], "%Y-%m-%d")
            
            if (curr_date - prev_date).days == 1:
                temp_streak += 1
            else:
                longest_streak = max(longest_streak, temp_streak)
                temp_streak = 1
        
        longest_streak = max(longest_streak, temp_streak)
        
        self.habits[habit_name]["current_streak"] = current_streak
        self.habits[habit_name]["longest_streak"] = longest_streak
    
    def delete_habit(self, habit_name: str):
        """Delete a habit"""
        if habit_name in self.habits:
            del self.habits[habit_name]
            self.save_habits()
            self.refresh_habits_display()
    
    def refresh_habits_display(self):
        """Refresh the habits display"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.habits:
            empty_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="No habits yet. Add one to get started! ??",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            )
            empty_label.pack(pady=50)
            return
        
        # Update streaks for all habits
        for habit_name in self.habits:
            self.update_streaks(habit_name)
        
        # Display each habit
        for habit_name, habit_data in self.habits.items():
            self.create_habit_card(habit_name, habit_data)
    
    def create_habit_card(self, habit_name: str, habit_data: Dict):
        """Create a beautiful card for each habit"""
        card = ctk.CTkFrame(
            self.scrollable_frame,
            corner_radius=15,
            border_width=2,
            border_color="#4CAF50"
        )
        card.pack(fill="x", padx=10, pady=10)
        
        # Main content frame
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=20, pady=15)
        
        # Habit name
        name_label = ctk.CTkLabel(
            content_frame,
            text=f"?? {habit_name}",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        name_label.pack(fill="x", pady=(0, 10))
        
        # Stats frame
        stats_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=5)
        
        # Current streak
        current_streak = habit_data["current_streak"]
        streak_label = ctk.CTkLabel(
            stats_frame,
            text=f" Current Streak: {current_streak} days",
            font=ctk.CTkFont(size=14),
            text_color="#FF9800"
        )
        streak_label.pack(side="left", padx=10)
        
        # Longest streak
        longest_streak = habit_data["longest_streak"]
        longest_label = ctk.CTkLabel(
            stats_frame,
            text=f"? Longest: {longest_streak} days",
            font=ctk.CTkFont(size=14),
            text_color="#9C27B0"
        )
        longest_label.pack(side="left", padx=10)
        
        # Total completions
        total = len(habit_data["completions"])
        total_label = ctk.CTkLabel(
            stats_frame,
            text=f"? Total: {total} days",
            font=ctk.CTkFont(size=14),
            text_color="#2196F3"
        )
        total_label.pack(side="left", padx=10)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=10)
        
        # Check if completed today
        today = datetime.now().strftime("%Y-%m-%d")
        is_completed_today = today in habit_data["completions"]
        
        if is_completed_today:
            complete_button = ctk.CTkButton(
                buttons_frame,
                text="? Completed Today",
                command=lambda: self.mark_incomplete(habit_name),
                width=150,
                height=35,
                font=ctk.CTkFont(size=13),
                fg_color="#4CAF50",
                hover_color="#45a049",
                state="normal"
            )
        else:
            complete_button = ctk.CTkButton(
                buttons_frame,
                text="Mark Complete",
                command=lambda: self.mark_complete(habit_name),
                width=150,
                height=35,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color="#2196F3",
                hover_color="#1976D2"
            )
        
        complete_button.pack(side="left", padx=5)
        
        # Delete button
        delete_button = ctk.CTkButton(
            buttons_frame,
            text="Delete",
            command=lambda: self.delete_habit(habit_name),
            width=120,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color="#f44336",
            hover_color="#da190b"
        )
        delete_button.pack(side="left", padx=5)
    
    def load_habits(self) -> Dict:
        """Load habits from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_habits(self):
        """Save habits to JSON file"""
        with open(self.data_file, "w") as f:
            json.dump(self.habits, f, indent=2)

def main():
    root = ctk.CTk()
    app = HabitTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
