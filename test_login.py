import tkinter as tk
from tkinter import ttk

class LoginWindow(tk.Tk):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.title("Login - Edu & Skill Path Recommender")
        self.geometry("400x300")
        self.configure(bg="#0f172a")
        
        # Center the window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (300 // 2)
        self.geometry(f"400x300+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self, bg="#0f172a", padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="Edu & Skill Path Recommender", 
            font=("Segoe UI", 16, "bold"),
            bg="#0f172a",
            fg="#e5e7eb"
        )
        title_label.pack(pady=(0, 20))
        
        # Login form
        form_frame = tk.Frame(main_frame, bg="#0f172a")
        form_frame.pack(expand=True, fill="both")
        
        # Username
        username_label = tk.Label(
            form_frame,
            text="Username:",
            font=("Segoe UI", 10),
            bg="#0f172a",
            fg="#e5e7eb"
        )
        username_label.pack(anchor="w", pady=(0, 5))
        
        self.username_entry = tk.Entry(form_frame, font=("Segoe UI", 10), width=30)
        self.username_entry.pack(pady=(0, 15))
        
        # Password
        password_label = tk.Label(
            form_frame,
            text="Password:",
            font=("Segoe UI", 10),
            bg="#0f172a",
            fg="#e5e7eb"
        )
        password_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = tk.Entry(form_frame, font=("Segoe UI", 10), width=30, show="*")
        self.password_entry.pack(pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg="#0f172a")
        button_frame.pack(fill="x")
        
        login_btn = tk.Button(
            button_frame,
            text="Login",
            font=("Segoe UI", 10, "bold"),
            bg="#1d4ed8",
            fg="#e5e7eb",
            command=self.login
        )
        login_btn.pack(side="left", padx=(0, 10))
        
        exit_btn = tk.Button(
            button_frame,
            text="Exit",
            font=("Segoe UI", 10, "bold"),
            bg="#6b7280",
            fg="#e5e7eb",
            command=self.destroy
        )
        exit_btn.pack(side="left")
        
        # Bind Enter key to login
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.login())
        
        # Focus on username entry
        self.username_entry.focus()
    
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        # Simple authentication (in a real app, you would check against a database)
        if username and password:  # Basic check that both fields are filled
            self.destroy()
            self.on_login_success(username)
        else:
            # Show error message
            error_window = tk.Toplevel(self)
            error_window.title("Login Error")
            error_window.geometry("300x100")
            error_window.configure(bg="#0f172a")
            
            # Center the error window
            error_window.update_idletasks()
            x = (self.winfo_screenwidth() // 2) - (300 // 2)
            y = (self.winfo_screenheight() // 2) - (100 // 2)
            error_window.geometry(f"300x100+{x}+{y}")
            
            tk.Label(
                error_window,
                text="Please enter both username and password",
                font=("Segoe UI", 10),
                bg="#0f172a",
                fg="#e5e7eb"
            ).pack(expand=True)
            
            tk.Button(
                error_window,
                text="OK",
                font=("Segoe UI", 10),
                bg="#1d4ed8",
                fg="#e5e7eb",
                command=error_window.destroy
            ).pack(pady=10)


class LogoutWindow(tk.Toplevel):
    def __init__(self, parent, on_logout):
        super().__init__(parent)
        self.on_logout = on_logout
        self.title("Logout")
        self.geometry("300x150")
        self.configure(bg="#0f172a")
        
        # Center the window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.winfo_screenheight() // 2) - (150 // 2)
        self.geometry(f"300x150+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self, bg="#0f172a", padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")
        
        # Message
        message_label = tk.Label(
            main_frame,
            text="Are you sure you want to logout?",
            font=("Segoe UI", 12),
            bg="#0f172a",
            fg="#e5e7eb"
        )
        message_label.pack(pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg="#0f172a")
        button_frame.pack(fill="x")
        
        yes_btn = tk.Button(
            button_frame,
            text="Yes, Logout",
            font=("Segoe UI", 10, "bold"),
            bg="#1d4ed8",
            fg="#e5e7eb",
            command=self.confirm_logout
        )
        yes_btn.pack(side="left", padx=(0, 10))
        
        no_btn = tk.Button(
            button_frame,
            text="Cancel",
            font=("Segoe UI", 10, "bold"),
            bg="#6b7280",
            fg="#e5e7eb",
            command=self.destroy
        )
        no_btn.pack(side="left")
    
    def confirm_logout(self):
        self.destroy()
        self.on_logout()


class MainWindow(tk.Tk):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.title(f"Main Application - Welcome {username}")
        self.geometry("800x600")
        self.configure(bg="#0f172a")
        
        # Create widgets
        self.create_widgets()
    
    def create_widgets(self):
        # Header with logout button
        header = tk.Frame(self, bg="#020617", padx=20, pady=10)
        header.pack(fill="x")
        
        welcome_label = tk.Label(
            header,
            text=f"Welcome, {self.username}!",
            font=("Segoe UI", 14, "bold"),
            bg="#020617",
            fg="#e5e7eb"
        )
        welcome_label.pack(side="left")
        
        logout_btn = tk.Button(
            header,
            text="Logout",
            font=("Segoe UI", 10, "bold"),
            bg="#6b7280",
            fg="#e5e7eb",
            command=self.logout
        )
        logout_btn.pack(side="right")
        
        # Main content
        content = tk.Frame(self, bg="#0f172a", padx=20, pady=20)
        content.pack(expand=True, fill="both")
        
        title_label = tk.Label(
            content,
            text="Edu & Skill Path Recommender",
            font=("Segoe UI", 20, "bold"),
            bg="#0f172a",
            fg="#e5e7eb"
        )
        title_label.pack(pady=(0, 30))
        
        info_label = tk.Label(
            content,
            text="This is the main application window.\nYou are now logged in.",
            font=("Segoe UI", 12),
            bg="#0f172a",
            fg="#e5e7eb",
            justify="center"
        )
        info_label.pack()
    
    def logout(self):
        # Show logout confirmation window
        LogoutWindow(self, self.perform_logout)
    
    def perform_logout(self):
        # Close the main application window
        self.destroy()
        
        # Show login window again
        login_window = LoginWindow(start_main_app)
        login_window.mainloop()


def start_main_app(username):
    """Start the main application after successful login."""
    print(f"Starting main application for user: {username}")
    app = MainWindow(username)
    app.mainloop()


def main():
    """Main entry point."""
    print("Starting login application...")
    # Show login window first
    login_window = LoginWindow(start_main_app)
    login_window.mainloop()


if __name__ == "__main__":
    main()