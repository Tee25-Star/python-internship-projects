import tkinter as tk
from tkinter import messagebox
import firebase_admin
from firebase_admin import credentials, firestore
import os

# --- 1. Robust Firebase Initialization ---
JSON_FILE = "serviceAccountKey.json"


def initialize_firebase():
    if not os.path.exists(JSON_FILE):
        # Create a popup error instead of crashing the console
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Configuration Error",
                             f"Missing '{JSON_FILE}' in:\n{os.getcwd()}\n\n"
                             "Please place the Firebase key in the project folder.")
        root.destroy()
        exit()

    cred = credentials.Certificate(JSON_FILE)
    firebase_admin.initialize_app(cred)
    return firestore.client()


db = initialize_firebase()
tasks_ref = db.collection('todos')


# --- 2. Application Logic ---
class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CloudSync To-Do")
        self.root.geometry("400x450")

        # UI Setup
        self.label = tk.Label(root, text="My Cloud Tasks", font=("Arial", 14, "bold"))
        self.label.pack(pady=10)

        self.entry = tk.Entry(root, width=35, font=("Arial", 12))
        self.entry.pack(pady=5)

        self.add_btn = tk.Button(root, text="Add Task", command=self.add_task, bg="#4CAF50", fg="white")
        self.add_btn.pack(pady=5)

        # We store the Firebase document IDs in a list to match them with the Listbox
        self.task_ids = []
        self.listbox = tk.Listbox(root, width=45, height=10, font=("Arial", 10))
        self.listbox.pack(pady=10)

        self.delete_btn = tk.Button(root, text="Delete Selected Task", command=self.delete_task, bg="#f44336",
                                    fg="white")
        self.delete_btn.pack(pady=5)

        self.load_tasks()

    def add_task(self):
        task_text = self.entry.get()
        if task_text.strip():
            # Sync to Cloud
            tasks_ref.add({'task': task_text, 'status': 'pending'})
            self.entry.delete(0, tk.END)
            self.load_tasks()
        else:
            messagebox.showwarning("Warning", "You cannot add an empty task.")

    def load_tasks(self):
        """Clears the list and pulls fresh data from Firebase."""
        self.listbox.delete(0, tk.END)
        self.task_ids = []
        try:
            docs = tasks_ref.stream()
            for doc in docs:
                data = doc.to_dict()
                self.listbox.insert(tk.END, f"• {data['task']}")
                self.task_ids.append(doc.id)  # Save ID for deletion
        except Exception as e:
            messagebox.showerror("Sync Error", f"Could not fetch data: {e}")

    def delete_task(self):
        """Deletes selected task from both the UI and the Cloud."""
        try:
            selected_index = self.listbox.curselection()[0]
            doc_id = self.task_ids[selected_index]

            # Delete from Firebase
            tasks_ref.document(doc_id).delete()

            # Refresh view
            self.load_tasks()
        except IndexError:
            messagebox.showwarning("Selection Error", "Please select a task to delete.")


if __name__ == "__main__":
    app_root = tk.Tk()
    app = TodoApp(app_root)
    app_root.mainloop()