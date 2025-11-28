import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class AdminWindow:
    def __init__(self, parent, auth_system):
        self.parent = parent
        self.auth_system = auth_system
        
        self.parent.title("FaceAuth - Admin Panel")
        self.parent.geometry("800x600")
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup admin interface"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Users tab
        users_frame = ttk.Frame(notebook, padding="10")
        notebook.add(users_frame, text="User Management")
        
        # Users list
        users_tree_frame = ttk.Frame(users_frame)
        users_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for users
        columns = ('Username', 'Full Name', 'Email', 'Created At')
        self.users_tree = ttk.Treeview(users_tree_frame, columns=columns, show='headings')
        
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=150)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(users_tree_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # User actions frame
        user_actions_frame = ttk.Frame(users_frame)
        user_actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            user_actions_frame, 
            text="Refresh", 
            command=self.load_users
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            user_actions_frame, 
            text="Delete Selected", 
            command=self.delete_selected_user
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Login history tab
        history_frame = ttk.Frame(notebook, padding="10")
        notebook.add(history_frame, text="Login History")
        
        # History treeview
        history_tree_frame = ttk.Frame(history_frame)
        history_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        history_columns = ('Username', 'Success', 'Confidence', 'Timestamp')
        self.history_tree = ttk.Treeview(history_tree_frame, columns=history_columns, show='headings')
        
        for col in history_columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=150)
        
        history_scrollbar = ttk.Scrollbar(history_tree_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # History actions
        history_actions_frame = ttk.Frame(history_frame)
        history_actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            history_actions_frame, 
            text="Refresh History", 
            command=self.load_history
        ).pack(side=tk.LEFT)
    
    def load_data(self):
        """Load all data"""
        self.load_users()
        self.load_history()
    
    def load_users(self):
        """Load users into treeview"""
        # Clear existing data
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        users = self.auth_system.get_users()
        for user in users:
            self.users_tree.insert('', tk.END, values=user)
    
    def load_history(self):
        """Load login history"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        history = self.auth_system.get_login_history()
        for record in history:
            success_text = "✅ Success" if record[1] else "❌ Failed"
            confidence_text = f"{record[3]:.1f}%" if record[3] else "N/A"
            self.history_tree.insert('', tk.END, values=(
                record[0], success_text, confidence_text, record[2]
            ))
    
    def delete_selected_user(self):
        """Delete selected user"""
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a user to delete")
            return
        
        user_data = self.users_tree.item(selected[0], 'values')
        username = user_data[0]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user '{username}'?"):
            success, message = self.auth_system.delete_user(username)
            if success:
                messagebox.showinfo("Success", message)
                self.load_users()
            else:
                messagebox.showerror("Error", message)