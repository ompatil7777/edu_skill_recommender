import tkinter as tk

class LoginWindow(tk.Tk):
    def __init__(self, on_login_success, on_register_click):
        super().__init__()
        self.on_login_success = on_login_success
        self.on_register_click = on_register_click
        self.title("Login - Edu & Skill Path Recommender")
        self.geometry("400x350")
        
        # Center the window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (350 // 2)
        self.geometry(f"400x350+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="Edu & Skill Path Recommender", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Subtitle
        subtitle_label = tk.Label(
            main_frame,
            text="Sign in to your account",
            font=("Arial", 10)
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Login form
        form_frame = tk.Frame(main_frame)
        form_frame.pack(expand=True, fill="both")
        
        # Username
        username_label = tk.Label(
            form_frame,
            text="Username:",
            font=("Arial", 10)
        )
        username_label.pack(anchor="w", pady=(0, 5))
        
        self.username_entry = tk.Entry(form_frame, font=("Arial", 10), width=30)
        self.username_entry.pack(pady=(0, 15))
        
        # Password
        password_label = tk.Label(
            form_frame,
            text="Password:",
            font=("Arial", 10)
        )
        password_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = tk.Entry(form_frame, font=("Arial", 10), width=30, show="*")
        self.password_entry.pack(pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(form_frame)
        button_frame.pack(fill="x")
        
        login_btn = tk.Button(
            button_frame,
            text="Sign In",
            font=("Arial", 10, "bold"),
            command=self.login
        )
        login_btn.pack(side="left", padx=(0, 10))
        
        exit_btn = tk.Button(
            button_frame,
            text="Exit",
            font=("Arial", 10, "bold"),
            command=self.destroy
        )
        exit_btn.pack(side="left")
        
        # Register link
        register_frame = tk.Frame(form_frame)
        register_frame.pack(fill="x", pady=(20, 0))
        
        register_label = tk.Label(
            register_frame,
            text="Don't have an account?",
            font=("Arial", 9)
        )
        register_label.pack(side="left")
        
        register_btn = tk.Button(
            register_frame,
            text="Register here",
            font=("Arial", 9, "underline"),
            fg="blue",
            cursor="hand2",
            relief="flat",
            command=self.on_register_click
        )
        register_btn.pack(side="left")
        
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
            
            # Center the error window
            error_window.update_idletasks()
            x = (self.winfo_screenwidth() // 2) - (300 // 2)
            y = (self.winfo_screenheight() // 2) - (100 // 2)
            error_window.geometry(f"300x100+{x}+{y}")
            
            tk.Label(
                error_window,
                text="Please enter both username and password",
                font=("Arial", 10)
            ).pack(expand=True)
            
            tk.Button(
                error_window,
                text="OK",
                font=("Arial", 10),
                command=error_window.destroy
            ).pack(pady=10)


class RegistrationWindow(tk.Tk):
    def __init__(self, on_register_success, on_login_click):
        super().__init__()
        self.on_register_success = on_register_success
        self.on_login_click = on_login_click
        self.title("Register - Edu & Skill Path Recommender")
        self.geometry("400x400")
        
        # Center the window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (400 // 2)
        self.geometry(f"400x400+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="Edu & Skill Path Recommender", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Subtitle
        subtitle_label = tk.Label(
            main_frame,
            text="Create a new account",
            font=("Arial", 10)
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Registration form
        form_frame = tk.Frame(main_frame)
        form_frame.pack(expand=True, fill="both")
        
        # Username
        username_label = tk.Label(
            form_frame,
            text="Username:",
            font=("Arial", 10)
        )
        username_label.pack(anchor="w", pady=(0, 5))
        
        self.username_entry = tk.Entry(form_frame, font=("Arial", 10), width=30)
        self.username_entry.pack(pady=(0, 15))
        
        # Email
        email_label = tk.Label(
            form_frame,
            text="Email (optional):",
            font=("Arial", 10)
        )
        email_label.pack(anchor="w", pady=(0, 5))
        
        self.email_entry = tk.Entry(form_frame, font=("Arial", 10), width=30)
        self.email_entry.pack(pady=(0, 15))
        
        # Password
        password_label = tk.Label(
            form_frame,
            text="Password:",
            font=("Arial", 10)
        )
        password_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = tk.Entry(form_frame, font=("Arial", 10), width=30, show="*")
        self.password_entry.pack(pady=(0, 15))
        
        # Confirm Password
        confirm_password_label = tk.Label(
            form_frame,
            text="Confirm Password:",
            font=("Arial", 10)
        )
        confirm_password_label.pack(anchor="w", pady=(0, 5))
        
        self.confirm_password_entry = tk.Entry(form_frame, font=("Arial", 10), width=30, show="*")
        self.confirm_password_entry.pack(pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(form_frame)
        button_frame.pack(fill="x")
        
        register_btn = tk.Button(
            button_frame,
            text="Register",
            font=("Arial", 10, "bold"),
            command=self.register
        )
        register_btn.pack(side="left", padx=(0, 10))
        
        exit_btn = tk.Button(
            button_frame,
            text="Exit",
            font=("Arial", 10, "bold"),
            command=self.destroy
        )
        exit_btn.pack(side="left")
        
        # Login link
        login_frame = tk.Frame(form_frame)
        login_frame.pack(fill="x", pady=(20, 0))
        
        login_label = tk.Label(
            login_frame,
            text="Already have an account?",
            font=("Arial", 9)
        )
        login_label.pack(side="left")
        
        login_btn = tk.Button(
            login_frame,
            text="Sign in here",
            font=("Arial", 9, "underline"),
            fg="blue",
            cursor="hand2",
            relief="flat",
            command=self.on_login_click
        )
        login_btn.pack(side="left")
        
        # Bind Enter key to registration
        self.username_entry.bind("<Return>", lambda e: self.email_entry.focus())
        self.email_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.confirm_password_entry.focus())
        self.confirm_password_entry.bind("<Return>", lambda e: self.register())
        
        # Focus on username entry
        self.username_entry.focus()
    
    def register(self):
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # Simple validation
        if not username:
            self.show_error("Please enter a username")
            return
        
        if not password:
            self.show_error("Please enter a password")
            return
        
        if password != confirm_password:
            self.show_error("Passwords do not match")
            return
        
        # In a real app, you would save the user to a database here
        # For now, we'll just close the registration window and open the main app
        self.destroy()
        self.on_register_success(username)
    
    def show_error(self, message):
        # Show error message
        error_window = tk.Toplevel(self)
        error_window.title("Registration Error")
        error_window.geometry("300x100")
        
        # Center the error window
        error_window.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.winfo_screenheight() // 2) - (100 // 2)
        error_window.geometry(f"300x100+{x}+{y}")
        
        tk.Label(
            error_window,
            text=message,
            font=("Arial", 10)
        ).pack(expand=True)
        
        tk.Button(
            error_window,
            text="OK",
            font=("Arial", 10),
            command=error_window.destroy
        ).pack(pady=10)


class MainWindow(tk.Tk):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.title(f"Main Application - Welcome {username}")
        self.geometry("800x600")
        
        # Create widgets
        self.create_widgets()
    
    def create_widgets(self):
        # Header with logout button
        header = tk.Frame(self, bg="lightgray", padx=20, pady=10)
        header.pack(fill="x")
        
        welcome_label = tk.Label(
            header,
            text=f"Welcome, {self.username}!",
            font=("Arial", 14, "bold")
        )
        welcome_label.pack(side="left")
        
        logout_btn = tk.Button(
            header,
            text="Logout",
            font=("Arial", 10, "bold"),
            command=self.logout
        )
        logout_btn.pack(side="right")
        
        # Main content
        content = tk.Frame(self, padx=20, pady=20)
        content.pack(expand=True, fill="both")
        
        title_label = tk.Label(
            content,
            text="Edu & Skill Path Recommender",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=(0, 30))
        
        info_label = tk.Label(
            content,
            text="This is the main application window.\nYou are now logged in.",
            font=("Arial", 12),
            justify="center"
        )
        info_label.pack()
    
    def logout(self):
        # Close the main application window
        self.destroy()
        
        # Show login window again
        show_login_window()


def show_login_window():
    """Show the login window."""
    def on_login_success(username):
        show_main_window(username)
    
    def on_register_click():
        login_window.destroy()
        show_registration_window()
    
    login_window = LoginWindow(on_login_success, on_register_click)
    login_window.mainloop()


def show_registration_window():
    """Show the registration window."""
    def on_register_success(username):
        show_main_window(username)
    
    def on_login_click():
        registration_window.destroy()
        show_login_window()
    
    registration_window = RegistrationWindow(on_register_success, on_login_click)
    registration_window.mainloop()


def show_main_window(username):
    """Show the main application window."""
    print(f"Starting main application for user: {username}")
    app = MainWindow(username)
    app.mainloop()


def main():
    """Main entry point."""
    print("Starting authentication demo...")
    # Show login window first
    show_login_window()


if __name__ == "__main__":
    main()