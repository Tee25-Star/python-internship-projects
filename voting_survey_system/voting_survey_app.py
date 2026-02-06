import customtkinter as ctk
import json
import os
from datetime import datetime
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class VotingSurveyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voting & Survey System")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Data storage
        self.votes = {}
        self.surveys = {}
        self.survey_responses = {}
        
        # Load existing data
        self.load_data()
        
        # Create main container
        self.main_frame = ctk.CTkFrame(root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="🗳️ Voting & Survey System",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#4A90E2"
        )
        self.title_label.pack(pady=(0, 30))
        
        # Create tabview for different sections
        self.tabview = ctk.CTkTabview(self.main_frame, width=1100, height=650)
        self.tabview.pack(fill="both", expand=True)
        
        # Create tabs
        self.voting_tab = self.tabview.add("🗳️ Voting")
        self.survey_tab = self.tabview.add("📊 Surveys")
        self.results_tab = self.tabview.add("📈 Results")
        
        # Setup each tab
        self.setup_voting_tab()
        self.setup_survey_tab()
        self.setup_results_tab()
        
    def load_data(self):
        """Load saved data from JSON files"""
        if os.path.exists("votes.json"):
            with open("votes.json", "r") as f:
                self.votes = json.load(f)
        
        if os.path.exists("surveys.json"):
            with open("surveys.json", "r") as f:
                self.surveys = json.load(f)
        
        if os.path.exists("survey_responses.json"):
            with open("survey_responses.json", "r") as f:
                self.survey_responses = json.load(f)
    
    def save_data(self):
        """Save data to JSON files"""
        with open("votes.json", "w") as f:
            json.dump(self.votes, f, indent=2)
        
        with open("surveys.json", "w") as f:
            json.dump(self.surveys, f, indent=2)
        
        with open("survey_responses.json", "w") as f:
            json.dump(self.survey_responses, f, indent=2)
    
    def setup_voting_tab(self):
        """Setup the voting tab"""
        # Left side - Create/View polls
        left_frame = ctk.CTkFrame(self.voting_tab)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        create_label = ctk.CTkLabel(
            left_frame,
            text="Create New Poll",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        create_label.pack(pady=10)
        
        # Poll question input
        self.poll_question_entry = ctk.CTkEntry(
            left_frame,
            placeholder_text="Enter poll question...",
            width=400,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.poll_question_entry.pack(pady=10, padx=20)
        
        # Options frame
        options_label = ctk.CTkLabel(
            left_frame,
            text="Options:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        options_label.pack(pady=(20, 10))
        
        self.option_entries = []
        for i in range(4):
            entry = ctk.CTkEntry(
                left_frame,
                placeholder_text=f"Option {i+1}...",
                width=400,
                height=35,
                font=ctk.CTkFont(size=12)
            )
            entry.pack(pady=5, padx=20)
            self.option_entries.append(entry)
        
        # Create poll button
        create_poll_btn = ctk.CTkButton(
            left_frame,
            text="Create Poll",
            command=self.create_poll,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4A90E2",
            hover_color="#357ABD"
        )
        create_poll_btn.pack(pady=20)
        
        # Right side - Active polls
        right_frame = ctk.CTkFrame(self.voting_tab)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        polls_label = ctk.CTkLabel(
            right_frame,
            text="Active Polls",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        polls_label.pack(pady=10)
        
        # Scrollable frame for polls
        self.polls_scroll = ctk.CTkScrollableFrame(right_frame, width=500)
        self.polls_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.refresh_polls()
    
    def setup_survey_tab(self):
        """Setup the survey tab"""
        # Left side - Create survey
        left_frame = ctk.CTkFrame(self.survey_tab)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        create_label = ctk.CTkLabel(
            left_frame,
            text="Create New Survey",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        create_label.pack(pady=10)
        
        # Survey title
        self.survey_title_entry = ctk.CTkEntry(
            left_frame,
            placeholder_text="Survey Title...",
            width=400,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.survey_title_entry.pack(pady=10, padx=20)
        
        # Questions frame
        questions_label = ctk.CTkLabel(
            left_frame,
            text="Questions:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        questions_label.pack(pady=(20, 10))
        
        self.survey_questions = []
        self.question_frames = []
        
        # Add question button
        add_question_btn = ctk.CTkButton(
            left_frame,
            text="+ Add Question",
            command=self.add_survey_question,
            width=200,
            height=35,
            font=ctk.CTkFont(size=12),
            fg_color="#50C878",
            hover_color="#40A868"
        )
        add_question_btn.pack(pady=10)
        
        # Create survey button
        create_survey_btn = ctk.CTkButton(
            left_frame,
            text="Create Survey",
            command=self.create_survey,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4A90E2",
            hover_color="#357ABD"
        )
        create_survey_btn.pack(pady=20)
        
        # Right side - Active surveys
        right_frame = ctk.CTkFrame(self.survey_tab)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        surveys_label = ctk.CTkLabel(
            right_frame,
            text="Active Surveys",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        surveys_label.pack(pady=10)
        
        # Scrollable frame for surveys
        self.surveys_scroll = ctk.CTkScrollableFrame(right_frame, width=500)
        self.surveys_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.refresh_surveys()
    
    def setup_results_tab(self):
        """Setup the results tab"""
        results_label = ctk.CTkLabel(
            self.results_tab,
            text="Results & Analytics",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        results_label.pack(pady=20)
        
        # Scrollable frame for results
        self.results_scroll = ctk.CTkScrollableFrame(self.results_tab)
        self.results_scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.refresh_results()
    
    def create_poll(self):
        """Create a new poll"""
        question = self.poll_question_entry.get().strip()
        options = [entry.get().strip() for entry in self.option_entries if entry.get().strip()]
        
        if not question:
            messagebox.showerror("Error", "Please enter a poll question!")
            return
        
        if len(options) < 2:
            messagebox.showerror("Error", "Please enter at least 2 options!")
            return
        
        poll_id = f"poll_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.votes[poll_id] = {
            "question": question,
            "options": options,
            "votes": {opt: 0 for opt in options},
            "created": datetime.now().isoformat()
        }
        
        self.save_data()
        self.refresh_polls()
        
        # Clear inputs
        self.poll_question_entry.delete(0, "end")
        for entry in self.option_entries:
            entry.delete(0, "end")
        
        messagebox.showinfo("Success", "Poll created successfully!")
    
    def refresh_polls(self):
        """Refresh the polls display"""
        # Clear existing widgets
        for widget in self.polls_scroll.winfo_children():
            widget.destroy()
        
        if not self.votes:
            no_polls_label = ctk.CTkLabel(
                self.polls_scroll,
                text="No polls available. Create one!",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_polls_label.pack(pady=20)
            return
        
        for poll_id, poll_data in self.votes.items():
            poll_frame = ctk.CTkFrame(self.polls_scroll, fg_color="#2B2B2B")
            poll_frame.pack(fill="x", padx=10, pady=10)
            
            # Question
            question_label = ctk.CTkLabel(
                poll_frame,
                text=poll_data["question"],
                font=ctk.CTkFont(size=16, weight="bold"),
                anchor="w"
            )
            question_label.pack(pady=10, padx=15, anchor="w")
            
            # Options with vote buttons
            for option in poll_data["options"]:
                option_frame = ctk.CTkFrame(poll_frame, fg_color="#1E1E1E")
                option_frame.pack(fill="x", padx=15, pady=5)
                
                option_label = ctk.CTkLabel(
                    option_frame,
                    text=option,
                    font=ctk.CTkFont(size=12),
                    anchor="w"
                )
                option_label.pack(side="left", padx=10, pady=8)
                
                vote_count = poll_data["votes"].get(option, 0)
                count_label = ctk.CTkLabel(
                    option_frame,
                    text=f"Votes: {vote_count}",
                    font=ctk.CTkFont(size=11),
                    text_color="#4A90E2"
                )
                count_label.pack(side="right", padx=10)
                
                vote_btn = ctk.CTkButton(
                    option_frame,
                    text="Vote",
                    command=lambda pid=poll_id, opt=option: self.cast_vote(pid, opt),
                    width=80,
                    height=30,
                    font=ctk.CTkFont(size=11),
                    fg_color="#4A90E2",
                    hover_color="#357ABD"
                )
                vote_btn.pack(side="right", padx=5)
    
    def cast_vote(self, poll_id, option):
        """Cast a vote for an option"""
        if poll_id in self.votes:
            self.votes[poll_id]["votes"][option] = self.votes[poll_id]["votes"].get(option, 0) + 1
            self.save_data()
            self.refresh_polls()
            self.refresh_results()
            messagebox.showinfo("Success", f"Vote cast for '{option}'!")
    
    def add_survey_question(self):
        """Add a new question to the survey form"""
        question_frame = ctk.CTkFrame(self.survey_tab.winfo_children()[0])
        question_frame.pack(fill="x", padx=20, pady=5)
        
        question_entry = ctk.CTkEntry(
            question_frame,
            placeholder_text="Enter question...",
            width=350,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        question_entry.pack(side="left", padx=5)
        
        question_type = ctk.CTkComboBox(
            question_frame,
            values=["Multiple Choice", "Text", "Rating (1-5)"],
            width=150,
            height=35,
            font=ctk.CTkFont(size=11)
        )
        question_type.set("Multiple Choice")
        question_type.pack(side="left", padx=5)
        
        remove_btn = ctk.CTkButton(
            question_frame,
            text="Remove",
            command=lambda: self.remove_survey_question(question_frame),
            width=80,
            height=35,
            font=ctk.CTkFont(size=11),
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        remove_btn.pack(side="left", padx=5)
        
        self.question_frames.append({
            "frame": question_frame,
            "entry": question_entry,
            "type": question_type
        })
    
    def remove_survey_question(self, frame):
        """Remove a question from the survey form"""
        frame.destroy()
        self.question_frames = [q for q in self.question_frames if q["frame"] != frame]
    
    def create_survey(self):
        """Create a new survey"""
        title = self.survey_title_entry.get().strip()
        
        if not title:
            messagebox.showerror("Error", "Please enter a survey title!")
            return
        
        if not self.question_frames:
            messagebox.showerror("Error", "Please add at least one question!")
            return
        
        questions = []
        for qf in self.question_frames:
            question_text = qf["entry"].get().strip()
            question_type = qf["type"].get()
            
            if question_text:
                questions.append({
                    "question": question_text,
                    "type": question_type
                })
        
        if not questions:
            messagebox.showerror("Error", "Please enter at least one valid question!")
            return
        
        survey_id = f"survey_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.surveys[survey_id] = {
            "title": title,
            "questions": questions,
            "created": datetime.now().isoformat()
        }
        self.survey_responses[survey_id] = []
        
        self.save_data()
        self.refresh_surveys()
        
        # Clear inputs
        self.survey_title_entry.delete(0, "end")
        for qf in self.question_frames:
            qf["frame"].destroy()
        self.question_frames = []
        
        messagebox.showinfo("Success", "Survey created successfully!")
    
    def refresh_surveys(self):
        """Refresh the surveys display"""
        # Clear existing widgets
        for widget in self.surveys_scroll.winfo_children():
            widget.destroy()
        
        if not self.surveys:
            no_surveys_label = ctk.CTkLabel(
                self.surveys_scroll,
                text="No surveys available. Create one!",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_surveys_label.pack(pady=20)
            return
        
        for survey_id, survey_data in self.surveys.items():
            survey_frame = ctk.CTkFrame(self.surveys_scroll, fg_color="#2B2B2B")
            survey_frame.pack(fill="x", padx=10, pady=10)
            
            # Title
            title_label = ctk.CTkLabel(
                survey_frame,
                text=survey_data["title"],
                font=ctk.CTkFont(size=18, weight="bold"),
                anchor="w"
            )
            title_label.pack(pady=10, padx=15, anchor="w")
            
            # Questions preview
            for i, q in enumerate(survey_data["questions"][:3], 1):
                q_label = ctk.CTkLabel(
                    survey_frame,
                    text=f"{i}. {q['question']} ({q['type']})",
                    font=ctk.CTkFont(size=11),
                    anchor="w",
                    text_color="gray"
                )
                q_label.pack(pady=2, padx=15, anchor="w")
            
            if len(survey_data["questions"]) > 3:
                more_label = ctk.CTkLabel(
                    survey_frame,
                    text=f"... and {len(survey_data['questions']) - 3} more questions",
                    font=ctk.CTkFont(size=10),
                    text_color="gray"
                )
                more_label.pack(pady=2, padx=15, anchor="w")
            
            # Take survey button
            take_btn = ctk.CTkButton(
                survey_frame,
                text="Take Survey",
                command=lambda sid=survey_id: self.take_survey(sid),
                width=150,
                height=35,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#50C878",
                hover_color="#40A868"
            )
            take_btn.pack(pady=10)
    
    def take_survey(self, survey_id):
        """Open a window to take a survey"""
        if survey_id not in self.surveys:
            return
        
        survey_window = ctk.CTkToplevel(self.root)
        survey_window.title("Take Survey")
        survey_window.geometry("700x600")
        survey_window.transient(self.root)
        
        survey_data = self.surveys[survey_id]
        
        title_label = ctk.CTkLabel(
            survey_window,
            text=survey_data["title"],
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        scroll_frame = ctk.CTkScrollableFrame(survey_window)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        responses = {}
        
        for i, question in enumerate(survey_data["questions"]):
            q_frame = ctk.CTkFrame(scroll_frame, fg_color="#2B2B2B")
            q_frame.pack(fill="x", padx=10, pady=10)
            
            q_label = ctk.CTkLabel(
                q_frame,
                text=f"{i+1}. {question['question']}",
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            q_label.pack(pady=10, padx=15, anchor="w")
            
            if question["type"] == "Text":
                entry = ctk.CTkEntry(
                    q_frame,
                    placeholder_text="Your answer...",
                    width=600,
                    height=40,
                    font=ctk.CTkFont(size=12)
                )
                entry.pack(pady=10, padx=15)
                responses[i] = entry
            
            elif question["type"] == "Rating (1-5)":
                rating_var = ctk.StringVar(value="3")
                rating_frame = ctk.CTkFrame(q_frame, fg_color="transparent")
                rating_frame.pack(pady=10, padx=15)
                
                for j in range(1, 6):
                    rb = ctk.CTkRadioButton(
                        rating_frame,
                        text=str(j),
                        variable=rating_var,
                        value=str(j),
                        font=ctk.CTkFont(size=12)
                    )
                    rb.pack(side="left", padx=10)
                
                responses[i] = rating_var
            
            else:  # Multiple Choice
                mc_var = ctk.StringVar()
                options = ["Option A", "Option B", "Option C", "Option D"]
                for opt in options:
                    rb = ctk.CTkRadioButton(
                        q_frame,
                        text=opt,
                        variable=mc_var,
                        value=opt,
                        font=ctk.CTkFont(size=12)
                    )
                    rb.pack(pady=5, padx=15, anchor="w")
                mc_var.set(options[0])
                responses[i] = mc_var
        
        def submit_survey():
            response_data = {}
            for i, question in enumerate(survey_data["questions"]):
                if question["type"] == "Text":
                    response_data[i] = responses[i].get()
                else:
                    response_data[i] = responses[i].get()
            
            if survey_id not in self.survey_responses:
                self.survey_responses[survey_id] = []
            
            self.survey_responses[survey_id].append({
                "responses": response_data,
                "timestamp": datetime.now().isoformat()
            })
            
            self.save_data()
            self.refresh_results()
            survey_window.destroy()
            messagebox.showinfo("Success", "Survey submitted successfully!")
        
        submit_btn = ctk.CTkButton(
            survey_window,
            text="Submit Survey",
            command=submit_survey,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4A90E2",
            hover_color="#357ABD"
        )
        submit_btn.pack(pady=20)
    
    def refresh_results(self):
        """Refresh the results display"""
        # Clear existing widgets
        for widget in self.results_scroll.winfo_children():
            widget.destroy()
        
        # Poll results
        if self.votes:
            polls_label = ctk.CTkLabel(
                self.results_scroll,
                text="Poll Results",
                font=ctk.CTkFont(size=20, weight="bold")
            )
            polls_label.pack(pady=(10, 20))
            
            for poll_id, poll_data in self.votes.items():
                poll_result_frame = ctk.CTkFrame(self.results_scroll, fg_color="#2B2B2B")
                poll_result_frame.pack(fill="x", padx=20, pady=10)
                
                question_label = ctk.CTkLabel(
                    poll_result_frame,
                    text=poll_data["question"],
                    font=ctk.CTkFont(size=16, weight="bold")
                )
                question_label.pack(pady=10)
                
                # Create bar chart
                options = list(poll_data["options"])
                votes = [poll_data["votes"].get(opt, 0) for opt in options]
                total_votes = sum(votes)
                
                if total_votes > 0:
                    fig, ax = plt.subplots(figsize=(8, 4), facecolor='#2B2B2B')
                    ax.set_facecolor('#2B2B2B')
                    
                    colors = ['#4A90E2', '#50C878', '#FF6B6B', '#FFD93D', '#9B59B6']
                    bars = ax.barh(options, votes, color=colors[:len(options)])
                    
                    ax.set_xlabel('Votes', color='white', fontsize=10)
                    ax.set_ylabel('Options', color='white', fontsize=10)
                    ax.tick_params(colors='white', labelsize=9)
                    ax.spines['bottom'].set_color('white')
                    ax.spines['top'].set_color('white')
                    ax.spines['right'].set_color('white')
                    ax.spines['left'].set_color('white')
                    
                    # Add vote counts on bars
                    for i, (bar, vote) in enumerate(zip(bars, votes)):
                        width = bar.get_width()
                        percentage = (vote / total_votes * 100) if total_votes > 0 else 0
                        ax.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                               f'{vote} ({percentage:.1f}%)',
                               ha='left', va='center', color='white', fontsize=9)
                    
                    plt.tight_layout()
                    
                    canvas = FigureCanvasTkAgg(fig, poll_result_frame)
                    canvas.draw()
                    canvas.get_tk_widget().pack(pady=10, padx=10)
                else:
                    no_votes_label = ctk.CTkLabel(
                        poll_result_frame,
                        text="No votes yet",
                        font=ctk.CTkFont(size=12),
                        text_color="gray"
                    )
                    no_votes_label.pack(pady=10)
        
        # Survey results
        if self.surveys:
            surveys_label = ctk.CTkLabel(
                self.results_scroll,
                text="Survey Results",
                font=ctk.CTkFont(size=20, weight="bold")
            )
            surveys_label.pack(pady=(30, 20))
            
            for survey_id, survey_data in self.surveys.items():
                if survey_id not in self.survey_responses or not self.survey_responses[survey_id]:
                    continue
                
                survey_result_frame = ctk.CTkFrame(self.results_scroll, fg_color="#2B2B2B")
                survey_result_frame.pack(fill="x", padx=20, pady=10)
                
                title_label = ctk.CTkLabel(
                    survey_result_frame,
                    text=survey_data["title"],
                    font=ctk.CTkFont(size=18, weight="bold")
                )
                title_label.pack(pady=10)
                
                response_count = len(self.survey_responses[survey_id])
                count_label = ctk.CTkLabel(
                    survey_result_frame,
                    text=f"Total Responses: {response_count}",
                    font=ctk.CTkFont(size=12),
                    text_color="#4A90E2"
                )
                count_label.pack(pady=5)
                
                # Show responses summary
                for i, question in enumerate(survey_data["questions"]):
                    q_frame = ctk.CTkFrame(survey_result_frame, fg_color="#1E1E1E")
                    q_frame.pack(fill="x", padx=15, pady=5)
                    
                    q_label = ctk.CTkLabel(
                        q_frame,
                        text=f"Q{i+1}: {question['question']}",
                        font=ctk.CTkFont(size=12, weight="bold"),
                        anchor="w"
                    )
                    q_label.pack(pady=5, padx=10, anchor="w")
                    
                    # Collect responses for this question
                    question_responses = []
                    for response in self.survey_responses[survey_id]:
                        if i in response["responses"]:
                            question_responses.append(response["responses"][i])
                    
                    if question_responses:
                        if question["type"] == "Rating (1-5)":
                            ratings = [int(r) for r in question_responses if r.isdigit()]
                            if ratings:
                                avg_rating = sum(ratings) / len(ratings)
                                rating_label = ctk.CTkLabel(
                                    q_frame,
                                    text=f"Average Rating: {avg_rating:.2f}/5",
                                    font=ctk.CTkFont(size=11),
                                    text_color="#50C878"
                                )
                                rating_label.pack(pady=5, padx=10, anchor="w")
                        else:
                            # Show sample responses
                            sample_responses = question_responses[:3]
                            for resp in sample_responses:
                                resp_label = ctk.CTkLabel(
                                    q_frame,
                                    text=f"• {resp}",
                                    font=ctk.CTkFont(size=10),
                                    text_color="gray",
                                    anchor="w"
                                )
                                resp_label.pack(pady=2, padx=20, anchor="w")
                            
                            if len(question_responses) > 3:
                                more_label = ctk.CTkLabel(
                                    q_frame,
                                    text=f"... and {len(question_responses) - 3} more responses",
                                    font=ctk.CTkFont(size=9),
                                    text_color="gray"
                                )
                                more_label.pack(pady=2, padx=20, anchor="w")
        
        if not self.votes and not any(self.survey_responses.values()):
            no_results_label = ctk.CTkLabel(
                self.results_scroll,
                text="No results available yet. Create polls and surveys to see results!",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_results_label.pack(pady=50)

def main():
    root = ctk.CTk()
    app = VotingSurveyApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
