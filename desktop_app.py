import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

# Bootstrap Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edu_skill_recommender.settings")

import django

django.setup()
print("Django setup completed successfully.")

import pyttsx3

from recommender.models import EducationStage, Question, OptionScore, Stream, UserProfile, Feedback  # noqa: E402
from recommender import services  # noqa: E402


class LoginWindow(tk.Tk):
    def __init__(self, on_login_success, on_register_click):
        super().__init__()
        self.on_login_success = on_login_success
        self.on_register_click = on_register_click
        self.title("Login - Edu & Skill Path Recommender")
        self.geometry("400x350")
        self.configure(bg="#0f172a")
        
        # Center the window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (350 // 2)
        self.geometry(f"400x350+{x}+{y}")
        
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
        
        # Subtitle
        subtitle_label = tk.Label(
            main_frame,
            text="Sign in to your account",
            font=("Segoe UI", 10),
            bg="#0f172a",
            fg="#9ca3af"
        )
        subtitle_label.pack(pady=(0, 20))
        
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
            text="Sign In",
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
        
        # Register link
        register_frame = tk.Frame(form_frame, bg="#0f172a")
        register_frame.pack(fill="x", pady=(20, 0))
        
        register_label = tk.Label(
            register_frame,
            text="Don't have an account?",
            font=("Segoe UI", 9),
            bg="#0f172a",
            fg="#9ca3af"
        )
        register_label.pack(side="left")
        
        register_btn = tk.Button(
            register_frame,
            text="Register here",
            font=("Segoe UI", 9, "underline"),
            bg="#0f172a",
            fg="#60a5fa",
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


class RegistrationWindow(tk.Tk):
    def __init__(self, on_register_success, on_login_click):
        super().__init__()
        self.on_register_success = on_register_success
        self.on_login_click = on_login_click
        self.title("Register - Edu & Skill Path Recommender")
        self.geometry("400x400")
        self.configure(bg="#0f172a")
        
        # Center the window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (400 // 2)
        self.geometry(f"400x400+{x}+{y}")
        
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
        
        # Subtitle
        subtitle_label = tk.Label(
            main_frame,
            text="Create a new account",
            font=("Segoe UI", 10),
            bg="#0f172a",
            fg="#9ca3af"
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Registration form
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
        
        # Email
        email_label = tk.Label(
            form_frame,
            text="Email (optional):",
            font=("Segoe UI", 10),
            bg="#0f172a",
            fg="#e5e7eb"
        )
        email_label.pack(anchor="w", pady=(0, 5))
        
        self.email_entry = tk.Entry(form_frame, font=("Segoe UI", 10), width=30)
        self.email_entry.pack(pady=(0, 15))
        
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
        self.password_entry.pack(pady=(0, 15))
        
        # Confirm Password
        confirm_password_label = tk.Label(
            form_frame,
            text="Confirm Password:",
            font=("Segoe UI", 10),
            bg="#0f172a",
            fg="#e5e7eb"
        )
        confirm_password_label.pack(anchor="w", pady=(0, 5))
        
        self.confirm_password_entry = tk.Entry(form_frame, font=("Segoe UI", 10), width=30, show="*")
        self.confirm_password_entry.pack(pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg="#0f172a")
        button_frame.pack(fill="x")
        
        register_btn = tk.Button(
            button_frame,
            text="Register",
            font=("Segoe UI", 10, "bold"),
            bg="#1d4ed8",
            fg="#e5e7eb",
            command=self.register
        )
        register_btn.pack(side="left", padx=(0, 10))
        
        exit_btn = tk.Button(
            button_frame,
            text="Exit",
            font=("Segoe UI", 10, "bold"),
            bg="#6b7280",
            fg="#e5e7eb",
            command=self.destroy
        )
        exit_btn.pack(side="left")
        
        # Login link
        login_frame = tk.Frame(form_frame, bg="#0f172a")
        login_frame.pack(fill="x", pady=(20, 0))
        
        login_label = tk.Label(
            login_frame,
            text="Already have an account?",
            font=("Segoe UI", 9),
            bg="#0f172a",
            fg="#9ca3af"
        )
        login_label.pack(side="left")
        
        login_btn = tk.Button(
            login_frame,
            text="Sign in here",
            font=("Segoe UI", 9, "underline"),
            bg="#0f172a",
            fg="#60a5fa",
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
        error_window.configure(bg="#0f172a")
        
        # Center the error window
        error_window.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.winfo_screenheight() // 2) - (100 // 2)
        error_window.geometry(f"300x100+{x}+{y}")
        
        tk.Label(
            error_window,
            text=message,
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


class ScreenManager(tk.Tk):
    def __init__(self, username):
        print("Initializing ScreenManager...")
        super().__init__()
        self.username = username
        print("Tk window created.")
        self.title(f"Edu & Skill Path Recommender - Welcome {username}")
        self.geometry("1000x650")
        self.minsize(900, 600)
        print("Window properties set.")

        # Dark theme configuration (eye-friendly)
        self.configure(bg="#0f172a")  # overall window background
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("App.TFrame", background="#0f172a")
        style.configure("Card.TFrame", background="#111827")
        style.configure("Header.TFrame", background="#020617")
        style.configure(
            "Header.TLabel",
            background="#020617",
            foreground="#e5e7eb",
            font=("Segoe UI", 14, "bold"),
        )
        style.configure(
            "SubHeader.TLabel",
            background="#020617",
            foreground="#9ca3af",
            font=("Segoe UI", 10),
        )
        style.configure(
            "TLabel",
            background="#111827",
            foreground="#e5e7eb",
            font=("Segoe UI", 10),
        )
        # High-contrast primary buttons for dark background
        style.configure(
            "TButton",
            padding=6,
            font=("Segoe UI", 10, "bold"),
            background="#1d4ed8",
            foreground="#e5e7eb",
        )
        style.map(
            "TButton",
            foreground=[("disabled", "#6b7280"), ("!disabled", "#e5e7eb")],
            background=[
                ("active", "#2563eb"),
                ("pressed", "#1d4ed8"),
            ],
        )
        style.configure(
            "Treeview",
            background="#020617",
            fieldbackground="#020617",
            foreground="#e5e7eb",
            rowheight=24,
        )
        style.configure(
            "Treeview.Heading",
            background="#111827",
            foreground="#e5e7eb",
            font=("Segoe UI", 10, "bold"),
        )

        self.current_user = None
        self.current_stage = None
        self.interest_answers = {}
        self.subject_levels = {}
        self.stream_recommendations = {}
        
        # Initialize text-to-speech engine
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
            
            # Get available voices and set a clear, pleasant voice
            voices = self.tts_engine.getProperty('voices')
            # Try to select a female voice if available (often clearer for instructions)
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            print(f"Text-to-speech initialization failed: {e}")
            self.tts_engine = None

        # Header bar with title and step indicator
        try:
            header = ttk.Frame(self, style="Header.TFrame", padding=(20, 10))
            header.pack(fill="x", side="top")

            self.title_label = ttk.Label(
                header,
                text=f"Edu & Skill Path Recommender - Welcome {username}",
                style="Header.TLabel",
            )
            self.title_label.pack(side="left")

            # Logout button
            logout_btn = tk.Button(
                header,
                text="Logout",
                font=("Segoe UI", 9, "bold"),
                bg="#6b7280",
                fg="#e5e7eb",
                command=self.logout
            )
            logout_btn.pack(side="right")

            right_header = ttk.Frame(header, style="Header.TFrame")
            right_header.pack(side="right", padx=(0, 10))

            self.step_label = ttk.Label(
                right_header,
                text="Step 1 of 7 – Welcome",
                style="SubHeader.TLabel",
            )
            self.step_label.pack(anchor="e")

            self.step_progress = ttk.Progressbar(
                right_header,
                orient="horizontal",
                length=220,
                mode="determinate",
                maximum=7,
            )
            self.step_progress.pack(anchor="e", pady=(4, 0))
            self.step_progress["value"] = 1
        except Exception as e:
            print(f"Error setting up header: {e}")
            import traceback
            traceback.print_exc()
            raise

        # Main container for screens
        try:
            container = ttk.Frame(self, style="App.TFrame")
            container.pack(fill="both", expand=True)

            self.frames = {}
            for F in (
                HomeScreen,
                StageSelectionScreen,
                QuestionnaireScreen,
                SubjectStrengthScreen,
                ResultsScreen,
                SkillRoadmapScreen,
                ProgressScreen,
                DashboardScreen,  # New dashboard screen
                HistoryScreen,
                AnalyticsScreen,
                FeedbackScreen,  # New feedback screen
                AccessibilitySettingsScreen,  # New accessibility settings screen
            ):
                frame = F(parent=container, controller=self)
                self.frames[F.__name__] = frame
                frame.grid(row=0, column=0, sticky="nsew")

            self._step_info = {
                "HomeScreen": (1, "Welcome"),
                "StageSelectionScreen": (2, "Stage selection"),
                "QuestionnaireScreen": (3, "Interests & aptitude"),
                "SubjectStrengthScreen": (4, "Subject strengths"),
                "ResultsScreen": (5, "Recommendations"),
                "SkillRoadmapScreen": (6, "Skill paths"),
                "ProgressScreen": (7, "Progress tracking"),
                "DashboardScreen": (8, "Dashboard"),
                "HistoryScreen": (8, "History"),
                "AnalyticsScreen": (8, "Analytics"),
            }

            self.show_frame("HomeScreen")
        except Exception as e:
            print(f"Error setting up screens: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def logout(self):
        # Show logout confirmation window
        LogoutWindow(self, self.perform_logout)
    
    def perform_logout(self):
        # Close the main application window
        self.destroy()
        
        # Show login window again
        login_window = LoginWindow(start_application)
        login_window.mainloop()

    def show_frame(self, name: str):
        frame = self.frames[name]
        frame.tkraise()

        # Update step indicator
        step_num, label = self._step_info.get(name, (1, "Welcome"))
        self.step_label.config(text=f"Step {step_num} of 7  {label}")
        self.step_progress["value"] = step_num

        if hasattr(frame, "on_show"):
            frame.on_show()
    
    def speak_text(self, text: str):
        """Speak the given text using text-to-speech."""
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"Text-to-speech failed: {e}")
    
    def speak_section(self, title: str, content: str):
        """Speak a section with title and content separately for better clarity."""
        if self.tts_engine:
            try:
                self.tts_engine.say(f"{title}. {content}")
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"Text-to-speech failed: {e}")
    
    def stop_speech(self):
        """Stop any ongoing speech."""
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except Exception as e:
                print(f"Failed to stop speech: {e}")


class BaseScreen(ttk.Frame):
    def __init__(self, parent, controller: ScreenManager):
        super().__init__(parent)
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.card = ttk.Frame(self, padding=20, style="Card.TFrame")
        self.card.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")


class HomeScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        title = ttk.Label(self.card, text="Edu & Skill Path Recommender", font=("Segoe UI", 18, "bold"))
        title.pack(pady=(0, 20))

        ttk.Label(self.card, text="Who is using this tool today?", font=("Segoe UI", 12)).pack(pady=10)

        self.mode_var = tk.StringVar(value="STUDENT")
        modes = [
            ("Student (Class 1-12)", "STUDENT"),
            ("UG / PG Student", "UGPG"),
            ("Working Professional", "PROFESSIONAL"),
            ("Parent / Teacher / Counselor", "COUNSELOR"),
        ]
        for text, val in modes:
            ttk.Radiobutton(self.card, text=text, variable=self.mode_var, value=val).pack(anchor="w")

        ttk.Label(self.card, text="Your name (for saving progress):").pack(pady=(20, 5))
        self.name_entry = ttk.Entry(self.card, width=40)
        self.name_entry.pack()

        # Create a frame for buttons
        button_frame = ttk.Frame(self.card)
        button_frame.pack(pady=(30, 0))
        
        # Next button
        btn = ttk.Button(button_frame, text="Next", command=self.next_clicked)
        btn.pack(side="left", padx=(0, 10))
        
        # Text-to-speech button
        tts_btn = ttk.Button(button_frame, text="🔊 Read Instructions", 
                           command=lambda: self.controller.speak_text(
                               "Please select who is using this tool today and enter your name"))
        tts_btn.pack(side="left")

    def next_clicked(self):
        name = self.name_entry.get().strip() or "Guest"
        mode = self.mode_var.get()

        is_counselor = mode == "COUNSELOR"
        is_professional = mode == "PROFESSIONAL"

        stage_code = EducationStage.UG
        if mode == "STUDENT":
            # Stage will be refined after class selection
            stage_code = EducationStage.PRIMARY
        elif mode == "UGPG":
            stage_code = EducationStage.UG
        elif mode == "PROFESSIONAL":
            stage_code = EducationStage.PROFESSIONAL
        elif mode == "COUNSELOR":
            stage_code = EducationStage.COUNSELOR

        stage = EducationStage.objects.get(code=stage_code)
        user = UserProfile.objects.create(
            name=name,
            education_stage=stage,
            is_parent_mode=is_counselor,
        )

        self.controller.current_user = user
        self.controller.current_stage = stage

        self.controller.show_frame("StageSelectionScreen")


class StageSelectionScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.title_lbl = ttk.Label(self.card, text="Select your current stage", font=("Segoe UI", 16, "bold"))
        self.title_lbl.pack(pady=(0, 20))

        self.class_var = tk.IntVar(value=10)
        self.role_var = tk.StringVar()
        self.target_role_var = tk.StringVar()

        self.class_frame = ttk.Frame(self.card)
        ttk.Label(self.class_frame, text="Current class (1-12):").pack(side="left")
        spin = ttk.Spinbox(self.class_frame, from_=1, to=12, textvariable=self.class_var, width=5)
        spin.pack(side="left", padx=5)

        self.role_frame = ttk.Frame(self.card)
        ttk.Label(self.role_frame, text="Current job role:").pack(anchor="w")
        ttk.Entry(self.role_frame, textvariable=self.role_var, width=40).pack(anchor="w")
        ttk.Label(self.role_frame, text="Target role (optional):").pack(anchor="w", pady=(10, 0))
        ttk.Entry(self.role_frame, textvariable=self.target_role_var, width=40).pack(anchor="w")

        self.info_lbl = ttk.Label(self.card, text="", wraplength=700, justify="left")
        self.info_lbl.pack(pady=10)

        nav = ttk.Frame(self.card)
        nav.pack(fill="x", pady=(20, 0))
        ttk.Button(nav, text="Back", command=lambda: controller.show_frame("HomeScreen")).pack(side="left")
        ttk.Button(nav, text="Next", command=self.next_clicked).pack(side="right")

    def on_show(self):
        user = self.controller.current_user
        if not user:
            return
        if user.education_stage.code in (
            EducationStage.PRIMARY,
            EducationStage.MIDDLE,
            EducationStage.HIGH_SCHOOL,
            EducationStage.HIGHER_SECONDARY,
        ):
            self.class_frame.pack(pady=10, fill="x")
            self.role_frame.pack_forget()
            self.info_lbl.config(
                text="For school students, we will use your class to suggest suitable streams or activities."
            )
        elif user.education_stage.code == EducationStage.PROFESSIONAL:
            self.role_frame.pack(pady=10, fill="x")
            self.class_frame.pack_forget()
            self.info_lbl.config(
                text="For professionals, we will build a skill roadmap based on your current and target roles."
            )
        else:
            self.class_frame.pack_forget()
            self.role_frame.pack_forget()
            self.info_lbl.config(
                text="For UG/PG students or counselors, we will ask about interests and suggest domains and skills."
            )

    def next_clicked(self):
        user = self.controller.current_user
        if not user:
            return

        if user.education_stage.code in (
            EducationStage.PRIMARY,
            EducationStage.MIDDLE,
            EducationStage.HIGH_SCHOOL,
            EducationStage.HIGHER_SECONDARY,
        ):
            current_class = self.class_var.get()
            user.current_class = current_class
            user.save()

            # Refine stage
            stage = services.classify_stage(current_class=current_class, is_professional=False, is_counselor=user.is_parent_mode)
            user.education_stage = stage
            user.save()
            self.controller.current_stage = stage
        elif user.education_stage.code == EducationStage.PROFESSIONAL:
            user.current_role = self.role_var.get().strip()
            user.target_role = self.target_role_var.get().strip()
            user.save()
        else:
            # UG/PG or counselor, no extra fields
            pass

        self.controller.show_frame("QuestionnaireScreen")


class QuestionnaireScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.title_lbl = ttk.Label(self.card, text="Interest & Aptitude Questionnaire", font=("Segoe UI", 16, "bold"))
        self.title_lbl.pack(pady=(0, 10))

        self.desc_lbl = ttk.Label(
            self.card,
            text="Answer a few simple questions about what you enjoy. This helps us suggest paths.",
            wraplength=700,
            justify="left",
        )
        self.desc_lbl.pack(pady=(0, 10))

        self.questions_frame = ttk.Frame(self.card)
        self.questions_frame.pack(fill="both", expand=True)

        nav = ttk.Frame(self.card)
        nav.pack(fill="x", pady=(10, 0))
        ttk.Button(nav, text="Back", command=lambda: controller.show_frame("StageSelectionScreen")).pack(side="left")
        ttk.Button(nav, text="Next", command=self.next_clicked).pack(side="right")

        self.option_vars = {}

    def on_show(self):
        for child in self.questions_frame.winfo_children():
            child.destroy()
        self.option_vars.clear()

        stage = self.controller.current_stage
        if not stage:
            return

        qs = Question.objects.filter(stage=stage, is_active=True)[:5]
        if not qs:
            ttk.Label(self.questions_frame, text="No questions defined for this stage (admin can add some).",
                      foreground="red").pack()
            return

        for q in qs:
            frame = ttk.Frame(self.questions_frame)
            frame.pack(fill="x", pady=5)
            ttk.Label(frame, text=q.text, wraplength=700, justify="left").pack(anchor="w")
            var = tk.IntVar(value=0)
            self.option_vars[q.id] = var
            for opt in q.options.all():
                ttk.Radiobutton(frame, text=opt.option_text, value=opt.id, variable=var).pack(anchor="w")

    def next_clicked(self):
        answers = []
        for qid, var in self.option_vars.items():
            opt_id = var.get()
            if opt_id:
                try:
                    opt = OptionScore.objects.get(id=opt_id)
                except OptionScore.DoesNotExist:
                    continue
                answers.append(
                    {
                        "logical": opt.logical_score,
                        "analytical": opt.analytical_score,
                        "creative": opt.creative_score,
                        "practical": opt.practical_score,
                        "people": opt.people_score,
                        "scientific": opt.scientific_score,
                        "design": opt.design_score,
                    }
                )

        self.controller.interest_answers = answers

        stage_code = self.controller.current_stage.code if self.controller.current_stage else None
        if stage_code in (EducationStage.HIGH_SCHOOL, EducationStage.HIGHER_SECONDARY):
            self.controller.show_frame("SubjectStrengthScreen")
        else:
            self.controller.show_frame("ResultsScreen")


class SubjectStrengthScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        ttk.Label(self.card, text="Subject Comfort Levels (1-10)", font=("Segoe UI", 16, "bold")).pack(pady=(0, 10))
        ttk.Label(
            self.card,
            text="Rate how comfortable you feel with each subject. 1 = very low, 10 = very high.",
        ).pack()

        self.inputs = {}
        form = ttk.Frame(self.card)
        form.pack(pady=10)

        for name, label in [
            ("maths", "Mathematics"),
            ("science", "Science"),
            ("english", "English"),
            ("business", "Business / Commerce"),
            ("creativity", "Art / Creativity"),
            ("language", "Languages"),
            ("social", "Social Studies / People"),
        ]:
            row = ttk.Frame(form)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=label + ":", width=25, anchor="w").pack(side="left")
            var = tk.IntVar(value=7)
            spin = ttk.Spinbox(row, from_=1, to=10, width=5, textvariable=var)
            spin.pack(side="left")
            self.inputs[name] = var

        nav = ttk.Frame(self.card)
        nav.pack(fill="x", pady=(10, 0))
        ttk.Button(nav, text="Back", command=lambda: controller.show_frame("QuestionnaireScreen")).pack(side="left")
        ttk.Button(nav, text="See Recommendations", command=self.next_clicked).pack(side="right")

    def next_clicked(self):
        levels = {k: v.get() for k, v in self.inputs.items()}
        self.controller.subject_levels = levels
        self.controller.show_frame("ResultsScreen")


class ResultsScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        ttk.Label(self.card, text="Recommendations", font=("Segoe UI", 16, "bold")).pack(pady=(0, 10))

        # Notebook for Plan A / Plan B / Plan C or other views
        self.notebook = ttk.Notebook(self.card)
        self.notebook.pack(fill="both", expand=True)

        nav = ttk.Frame(self.card)
        nav.pack(fill="x", pady=(10, 0))
        ttk.Button(nav, text="Back", command=lambda: controller.show_frame("QuestionnaireScreen")).pack(side="left")
        
        # Text-to-speech button for reading recommendations
        tts_btn = ttk.Button(nav, text="🔊 Read Recommendations", 
                          command=self.read_recommendations)
        tts_btn.pack(side="left", padx=(10, 0))
        
        ttk.Button(nav, text="Skill Roadmap", command=lambda: controller.show_frame("SkillRoadmapScreen")).pack(side="right")

    def _clear_tabs(self):
        for tab_id in self.notebook.tabs():
            self.notebook.forget(tab_id)

    def on_show(self):
        self._clear_tabs()

        user = self.controller.current_user
        stage = self.controller.current_stage
        if not user or not stage:
            return

        profile = services.InterestProfile.from_option_scores(self.controller.interest_answers)

        if stage.code in (EducationStage.HIGH_SCHOOL, EducationStage.HIGHER_SECONDARY):
            streams = services.recommend_streams_with_explanations(profile, self.controller.subject_levels)
            self.controller.stream_recommendations = streams

            for plan_label in ["Plan A", "Plan B", "Plan C"]:
                if plan_label not in streams:
                    continue
                data = streams[plan_label]
                s: Stream = data["stream"]

                frame = ttk.Frame(self.notebook, padding=12, style="Card.TFrame")
                self.notebook.add(frame, text=plan_label)

                ttk.Label(frame, text=f"{s.name} Stream", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 6))
                ttk.Label(frame, text=data["explanation"], wraplength=760, justify="left").pack(anchor="w", pady=(0, 10))

                info = ttk.Frame(frame, style="Card.TFrame")
                info.pack(fill="x", pady=(0, 8))
                ttk.Label(info, text=f"Required strengths: {data['required_strengths']}", wraplength=760, justify="left").pack(anchor="w", pady=2)
                ttk.Label(info, text=f"Key subjects: {data['key_subjects']}", wraplength=760, justify="left").pack(anchor="w", pady=2)
                ttk.Label(info, text=f"Early preparation: {data['early_preparation_ideas']}", wraplength=760, justify="left").pack(anchor="w", pady=2)

                # Show careers only for Plan A by default (most relevant)
                if plan_label == "Plan A":
                    careers_box = ttk.Frame(frame, style="Card.TFrame")
                    careers_box.pack(fill="both", expand=True, pady=(10, 0))
                    ttk.Label(careers_box, text="Career directions and entrance exams:", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 4))

                    careers = services.get_career_recommendations_for_stream(s, profile)
                    if not careers:
                        ttk.Label(careers_box, text="No careers configured yet for this stream.").pack(anchor="w")
                    else:
                        for c in careers:
                            block = ttk.Frame(careers_box, style="Card.TFrame")
                            block.pack(fill="x", pady=2)
                            ttk.Label(block, text=c["name"], font=("Segoe UI", 10, "bold")).pack(anchor="w")
                            if c["description"]:
                                ttk.Label(block, text=c["description"], wraplength=760, justify="left").pack(anchor="w")
                            ttk.Label(block, text=f"Why it fits: {c['why_fit']}", wraplength=760, justify="left").pack(anchor="w")
                            if c["exams"]:
                                ttk.Label(block, text=f"Entrance exams: {c['exams']}", wraplength=760, justify="left").pack(anchor="w")
        elif stage.code in (EducationStage.PRIMARY, EducationStage.MIDDLE):
            frame = ttk.Frame(self.notebook, padding=12, style="Card.TFrame")
            self.notebook.add(frame, text="Activities")

            ttk.Label(frame, text="Growth activities (not career-specific yet)", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 8))
            for act in services.get_activity_suggestions(stage):
                ttk.Label(frame, text=f"• {act.title}: {act.description}", wraplength=760, justify="left").pack(anchor="w", pady=1)

            tips = services.get_motivation_tips(stage, audience="SCHOOL")
            if tips:
                ttk.Label(frame, text="\nMotivation tips:", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(8, 2))
                for t in tips:
                    ttk.Label(frame, text=f"• {t.text}", wraplength=760, justify="left").pack(anchor="w")
        elif stage.code in (EducationStage.UG, EducationStage.PG):
            frame = ttk.Frame(self.notebook, padding=12, style="Card.TFrame")
            self.notebook.add(frame, text="Summary")
            ttk.Label(
                frame,
                text=(
                    "We will suggest skill paths on the next screen based on your interests and education level.\n"
                    "You can then track progress step-by-step."
                ),
                wraplength=760,
                justify="left",
            ).pack(anchor="w")
        elif stage.code == EducationStage.PROFESSIONAL:
            frame = ttk.Frame(self.notebook, padding=12, style="Card.TFrame")
            self.notebook.add(frame, text="Career switch roadmap")

            roadmap = services.career_switch_roadmap(user.current_role, user.target_role)
            ttk.Label(
                frame,
                text=roadmap,
                wraplength=760,
                justify="left",
            ).pack(anchor="w")
        else:
            frame = ttk.Frame(self.notebook, padding=12, style="Card.TFrame")
            self.notebook.add(frame, text="Counselor notes")
            ttk.Label(
                frame,
                text=(
                    "Counselor mode: focus on the student's curiosities, comfort with subjects, and wellbeing.\n"
                    "Use this tool as a guide, and combine it with your own observations."
                ),
                wraplength=760,
                justify="left",
            ).pack(anchor="w")

    def read_recommendations(self):
        """Read the current recommendations using text-to-speech."""
        user = self.controller.current_user
        stage = self.controller.current_stage
        if not user or not stage:
            return

        # Stop any ongoing speech
        self.controller.stop_speech()

        # Collect text to read
        texts_to_read = []
        
        if stage.code in (EducationStage.HIGH_SCHOOL, EducationStage.HIGHER_SECONDARY):
            texts_to_read.append("Here are your stream recommendations:")
            streams = self.controller.stream_recommendations
            for plan_label in ["Plan A", "Plan B", "Plan C"]:
                if plan_label in streams:
                    data = streams[plan_label]
                    s = data["stream"]
                    texts_to_read.append(f"{plan_label}: {s.name} stream.")
                    texts_to_read.append(data["explanation"])
                    
                    # For Plan A, also read career directions
                    if plan_label == "Plan A":
                        careers = services.get_career_recommendations_for_stream(s, 
                            services.InterestProfile.from_option_scores(self.controller.interest_answers))
                        if careers:
                            texts_to_read.append("Career directions for this stream:")
                            for c in careers:
                                texts_to_read.append(f"{c['name']}. {c['why_fit']}")
        elif stage.code in (EducationStage.PRIMARY, EducationStage.MIDDLE):
            texts_to_read.append("Here are growth activities for your stage:")
            for act in services.get_activity_suggestions(stage):
                texts_to_read.append(f"{act.title}. {act.description}")
            
            tips = services.get_motivation_tips(stage, audience="SCHOOL")
            if tips:
                texts_to_read.append("Here are some motivation tips:")
                for t in tips:
                    texts_to_read.append(t.text)
        elif stage.code in (EducationStage.UG, EducationStage.PG):
            texts_to_read.append("We will suggest skill paths based on your interests and education level. You can then track progress step by step.")
        elif stage.code == EducationStage.PROFESSIONAL:
            texts_to_read.append("Here is your career switch roadmap:")
            roadmap = services.career_switch_roadmap(user.current_role, user.target_role)
            texts_to_read.append(roadmap)
        else:
            texts_to_read.append("Counselor mode: focus on the student's curiosities, comfort with subjects, and wellbeing. Use this tool as a guide, and combine it with your own observations.")

        # Speak all collected text
        full_text = " ".join(texts_to_read)
        self.controller.speak_text(full_text)


class SkillRoadmapScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        ttk.Label(self.card, text="Skill Path Roadmaps", font=("Segoe UI", 16, "bold")).pack(pady=(0, 10))

        self.notebook = ttk.Notebook(self.card)
        self.notebook.pack(fill="both", expand=True)

        nav = ttk.Frame(self.card)
        nav.pack(fill="x", pady=(10, 0))
        ttk.Button(nav, text="Back", command=lambda: controller.show_frame("ResultsScreen")).pack(side="left")
        
        # Text-to-speech button for reading skill roadmaps
        tts_btn = ttk.Button(nav, text="🔊 Read Roadmaps", 
                          command=self.read_roadmaps)
        tts_btn.pack(side="left", padx=(10, 0))
        
        ttk.Button(nav, text="Track Selected Plan", command=self.track_selected_plan).pack(side="right")

        self.selected_path = None
        self.plan_paths = {}

    def _clear_tabs(self):
        for tab_id in self.notebook.tabs():
            self.notebook.forget(tab_id)
        self.plan_paths.clear()

    def on_show(self):
        self._clear_tabs()
        user = self.controller.current_user
        stage = self.controller.current_stage
        if not user or not stage:
            return

        stream = None
        if self.controller.stream_recommendations:
            best = self.controller.stream_recommendations.get("Plan A")
            if best:
                stream = best["stream"]

        profile = services.InterestProfile.from_option_scores(self.controller.interest_answers)
        paths = services.get_skill_paths_for_target(stage, stream, getattr(user, "target_role", ""), profile)
        if not paths:
            frame = ttk.Frame(self.notebook, padding=12, style="Card.TFrame")
            self.notebook.add(frame, text="No paths")
            ttk.Label(frame, text="No skill paths defined yet. Admin can add them in Django admin.").pack(anchor="w")
            return

        for label, path in paths.items():
            frame = ttk.Frame(self.notebook, padding=12, style="Card.TFrame")
            self.notebook.add(frame, text=label)
            self.plan_paths[label] = path

            ttk.Label(frame, text=path.name, font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 4))
            if path.description:
                ttk.Label(frame, text=path.description, wraplength=760, justify="left").pack(anchor="w", pady=(0, 6))

            columns = ("skill", "level", "difficulty", "time")
            tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
            tree.heading("skill", text="Skill step")
            tree.heading("level", text="Level")
            tree.heading("difficulty", text="Difficulty")
            tree.heading("time", text="Time")
            tree.column("skill", width=260)
            tree.column("level", width=160)
            tree.column("difficulty", width=120)
            tree.column("time", width=80)
            tree.pack(fill="both", expand=True, pady=(4, 0))

            for step in path.steps.all():
                level_text = dict(step.LEVEL_CHOICES).get(step.level, step.level)
                tree.insert(
                    "",
                    tk.END,
                    values=(
                        step.skill.name,
                        level_text,
                        step.difficulty.label,
                        f"{step.estimated_weeks} weeks",
                    ),
                )

        # Pre-select Plan A tab if available
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == "Plan A":
                self.notebook.select(tab_id)
                break

    def track_selected_plan(self):
        user = self.controller.current_user
        if not user:
            return

        current_tab = self.notebook.select()
        if not current_tab:
            return

        label = self.notebook.tab(current_tab, "text")
        path = self.plan_paths.get(label)
        if not path:
            return

        services.initialize_progress_for_path(user, path)
        self.selected_path = path
        messagebox.showinfo("Tracking started", f"Now tracking progress for: {path.name}")

        # Navigate to progress view
        self.controller.show_frame("ProgressScreen")

    def read_roadmaps(self):
        """Read the current skill roadmaps using text-to-speech."""
        user = self.controller.current_user
        stage = self.controller.current_stage
        if not user or not stage:
            return

        # Stop any ongoing speech
        self.controller.stop_speech()

        # Collect text to read
        texts_to_read = ["Here are your skill path roadmaps:"]
        
        stream = None
        if self.controller.stream_recommendations:
            best = self.controller.stream_recommendations.get("Plan A")
            if best:
                stream = best["stream"]

        profile = services.InterestProfile.from_option_scores(self.controller.interest_answers)
        paths = services.get_skill_paths_for_target(stage, stream, getattr(user, "target_role", ""), profile)
        if not paths:
            texts_to_read.append("No skill paths are currently defined.")
        else:
            for label, path in paths.items():
                texts_to_read.append(f"{label}: {path.name}.")
                if path.description:
                    texts_to_read.append(path.description)
                
                # Read steps
                steps = list(path.steps.all())
                if steps:
                    texts_to_read.append("Steps for this path:")
                    for i, step in enumerate(steps, 1):
                        level_text = dict(step.LEVEL_CHOICES).get(step.level, step.level)
                        texts_to_read.append(f"Step {i}: {step.skill.name}, {level_text}, {step.difficulty.label} difficulty, estimated time: {step.estimated_weeks} weeks.")

        # Speak all collected text
        full_text = " ".join(texts_to_read)
        self.controller.speak_text(full_text)


class ProgressScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        ttk.Label(self.card, text="Skill Path Progress", font=("Segoe UI", 16, "bold")).pack(pady=(0, 10))

        # Progress visualization frame
        self.progress_frame = ttk.Frame(self.card)
        self.progress_frame.pack(fill="x", pady=10)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(side="left", padx=(0, 20))
        
        self.progress_label = ttk.Label(self.progress_frame, text="0%", font=("Segoe UI", 12, "bold"))
        self.progress_label.pack(side="left")

        self.summary_lbl = ttk.Label(self.card, text="", wraplength=700, justify="left")
        self.summary_lbl.pack(pady=5)

        # Difficulty distribution frame
        self.difficulty_frame = ttk.Frame(self.card)
        self.difficulty_frame.pack(fill="x", pady=10)
        
        self.easy_label = ttk.Label(self.difficulty_frame, text="Easy: 0", foreground="#4ade80")
        self.easy_label.pack(side="left", padx=(0, 10))
        
        self.medium_label = ttk.Label(self.difficulty_frame, text="Medium: 0", foreground="#fbbf24")
        self.medium_label.pack(side="left", padx=(0, 10))
        
        self.hard_label = ttk.Label(self.difficulty_frame, text="Hard: 0", foreground="#f87171")
        self.hard_label.pack(side="left")

        self.tree = ttk.Treeview(self.card, columns=("skill", "status"), show="headings", height=10)
        self.tree.heading("skill", text="Skill step")
        self.tree.heading("status", text="Status")
        self.tree.pack(fill="both", expand=True, pady=5)

        # Double-click to quickly advance status (Not started -> In progress -> Completed)
        self.tree.bind("<Double-1>", self._on_double_click)

        btn_frame = ttk.Frame(self.card)
        btn_frame.pack(fill="x", pady=(5, 0))
        ttk.Button(btn_frame, text="Mark as In Progress", command=lambda: self.update_status("IN_PROGRESS")).pack(side="left")
        ttk.Button(btn_frame, text="Mark as Completed", command=lambda: self.update_status("COMPLETED")).pack(side="left", padx=5)

        nav = ttk.Frame(self.card)
        nav.pack(fill="x", pady=(10, 0))
        ttk.Button(nav, text="Back", command=lambda: controller.show_frame("SkillRoadmapScreen")).pack(side="left")
        ttk.Button(nav, text="Dashboard", command=lambda: controller.show_frame("DashboardScreen")).pack(side="left", padx=5)
        ttk.Button(nav, text="History / Analytics", command=lambda: controller.show_frame("HistoryScreen")).pack(side="right")

    def on_show(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        user = self.controller.current_user
        stage = self.controller.current_stage
        if not user or not stage:
            return

        # Pick first path for this user (from progress records)
        from recommender.models import UserSkillProgress

        qs = UserSkillProgress.objects.filter(user_profile=user).select_related("step__skill", "skill_path")
        if not qs.exists():
            self.summary_lbl.config(text="No skill path is being tracked yet.")
            self.progress_bar["value"] = 0
            self.progress_label.config(text="0%")
            self.easy_label.config(text="Easy: 0")
            self.medium_label.config(text="Medium: 0")
            self.hard_label.config(text="Hard: 0")
            return

        path = qs.first().skill_path
        summary = services.compute_progress_summary(user, path)
        
        # Update progress bar
        self.progress_bar["maximum"] = 100
        self.progress_bar["value"] = summary['percent']
        self.progress_label.config(text=f"{summary['percent']}%")
        
        # Update difficulty labels
        difficulty_parts = summary['difficulty_text'].split(", ")
        easy_count = 0
        medium_count = 0
        hard_count = 0
        
        for part in difficulty_parts:
            if "Easy:" in part:
                easy_count = int(part.split(":")[1].strip())
            elif "Medium:" in part:
                medium_count = int(part.split(":")[1].strip())
            elif "Hard:" in part:
                hard_count = int(part.split(":")[1].strip())
        
        self.easy_label.config(text=f"Easy: {easy_count}")
        self.medium_label.config(text=f"Medium: {medium_count}")
        self.hard_label.config(text=f"Hard: {hard_count}")
        
        # Update milestone information
        milestones_text = f"Milestones achieved: {summary.get('milestones_achieved', 0)}"
        streak_text = f"Current streak: {summary.get('streak', 0)} days"
        
        # Get user's earned milestones
        user_milestones = services.get_user_milestones(user)
        
        self.summary_lbl.config(
            text=(
                f"Tracking path: {path.name}\n"
                f"Completed {summary['completed']} of {summary['total']} steps "
                f"({summary['percent']}% done).\n"
                f"{milestones_text} | {streak_text}\n"
            )
        )
        
        # Display earned milestones if any
        if user_milestones:
            milestone_text = "\nEarned Badges: "
            for milestone in user_milestones[:3]:  # Show only first 3
                badge_symbols = {"BRONZE": "🥉", "SILVER": "🥈", "GOLD": "🥇"}
                symbol = badge_symbols.get(milestone['badge_type'], "🏆")
                milestone_text += f"{symbol} {milestone['name']}  "
            
            # Add to summary label
            current_text = self.summary_lbl.cget("text")
            self.summary_lbl.config(text=current_text + milestone_text)

        for p in qs:
            # Add milestone indicator to status if achieved
            status_display = p.get_status_display()
            if p.milestone_achieved:
                status_display += " 🏆"
            
            self.tree.insert("", tk.END, iid=str(p.id), values=(p.step.skill.name, status_display))

    def update_status(self, status_code: str):
        from recommender.models import UserSkillProgress
        from recommender import services

        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select a step", "Please select a skill step to update.")
            return

        prog_id = int(sel[0])
        try:
            prog = UserSkillProgress.objects.get(id=prog_id)
        except UserSkillProgress.DoesNotExist:
            return
        
        # Use the new service function to update progress
        services.update_skill_step_progress(
            user=prog.user_profile,
            step=prog.step,
            status=status_code
        )
        self.on_show()

    def _on_double_click(self, event):
        """Advance status in a simple cycle when the user double-clicks a row."""
        from recommender.models import UserSkillProgress
        from recommender import services

        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        try:
            prog = UserSkillProgress.objects.get(id=int(item_id))
        except UserSkillProgress.DoesNotExist:
            return

        if prog.status == UserSkillProgress.NOT_STARTED:
            new_status = UserSkillProgress.IN_PROGRESS
        elif prog.status == UserSkillProgress.IN_PROGRESS:
            new_status = UserSkillProgress.COMPLETED
        else:
            # Already completed; keep as-is
            return

        # Use the new service function to update progress
        services.update_skill_step_progress(
            user=prog.user_profile,
            step=prog.step,
            status=new_status
        )
        self.on_show()


class DashboardScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        ttk.Label(self.card, text="Learning Dashboard", font=("Segoe UI", 16, "bold")).pack(pady=(0, 10))
        
        # Summary stats frame
        self.stats_frame = ttk.Frame(self.card, style="Card.TFrame")
        self.stats_frame.pack(fill="x", pady=10)
        
        # Charts frame
        self.charts_frame = ttk.Frame(self.card, style="Card.TFrame")
        self.charts_frame.pack(fill="both", expand=True, pady=10)
        
        # Recent activity frame
        self.activity_frame = ttk.Frame(self.card, style="Card.TFrame")
        self.activity_frame.pack(fill="x", pady=10)
        
        # Navigation
        nav = ttk.Frame(self.card)
        nav.pack(fill="x", pady=(10, 0))
        ttk.Button(nav, text="Back", command=lambda: controller.show_frame("ProgressScreen")).pack(side="left")

    def on_show(self):
        # Clear previous content
        for child in self.stats_frame.winfo_children():
            child.destroy()
            
        for child in self.charts_frame.winfo_children():
            child.destroy()
            
        for child in self.activity_frame.winfo_children():
            child.destroy()
        
        user = self.controller.current_user
        if not user:
            return
            
        # Get user's progress data
        from recommender.models import UserSkillProgress
        from recommender import services
        
        # Stats section
        stats_title = ttk.Label(self.stats_frame, text="Overview", font=("Segoe UI", 12, "bold"))
        stats_title.pack(anchor="w", pady=(0, 10))
        
        # Get all user progress records
        user_progress = UserSkillProgress.objects.filter(user_profile=user)
        
        if not user_progress.exists():
            ttk.Label(self.stats_frame, text="No progress data available yet.").pack(anchor="w")
            return
            
        # Calculate statistics
        total_steps = user_progress.count()
        completed_steps = user_progress.filter(status=UserSkillProgress.COMPLETED).count()
        in_progress_steps = user_progress.filter(status=UserSkillProgress.IN_PROGRESS).count()
        not_started_steps = user_progress.filter(status=UserSkillProgress.NOT_STARTED).count()
        
        completion_rate = int(round((completed_steps / total_steps) * 100)) if total_steps > 0 else 0
        
        # Get milestones
        user_milestones = services.get_user_milestones(user)
        milestones_count = len(user_milestones)
        
        # Display stats in a grid
        stats_grid = ttk.Frame(self.stats_frame)
        stats_grid.pack(fill="x")
        
        # Stat cards
        stat_cards = [
            {"title": "Total Steps", "value": total_steps, "color": "#60a5fa"},
            {"title": "Completed", "value": completed_steps, "color": "#4ade80"},
            {"title": "In Progress", "value": in_progress_steps, "color": "#fbbf24"},
            {"title": "Completion Rate", "value": f"{completion_rate}%", "color": "#a78bfa"},
            {"title": "Milestones", "value": milestones_count, "color": "#f87171"},
        ]
        
        for i, stat in enumerate(stat_cards):
            col = i % 3
            row = i // 3
            
            card = ttk.Frame(stats_grid, style="Card.TFrame", padding=10)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            stats_grid.columnconfigure(col, weight=1)
            
            title_label = ttk.Label(card, text=stat["title"], font=("Segoe UI", 10))
            title_label.pack(anchor="w")
            
            value_label = ttk.Label(card, text=str(stat["value"]), font=("Segoe UI", 16, "bold"), foreground=stat["color"])
            value_label.pack(anchor="w")
        
        # Charts section
        charts_title = ttk.Label(self.charts_frame, text="Progress Visualization", font=("Segoe UI", 12, "bold"))
        charts_title.pack(anchor="w", pady=(0, 10))
        
        # Simple text-based chart for difficulty distribution
        difficulty_chart = ttk.Frame(self.charts_frame)
        difficulty_chart.pack(fill="x", pady=5)
        
        ttk.Label(difficulty_chart, text="Difficulty Distribution:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        
        # Calculate difficulty distribution
        difficulty_counts = {"Easy": 0, "Medium": 0, "Hard": 0}
        for prog in user_progress.select_related("step__difficulty"):
            label = prog.step.difficulty.label
            difficulty_counts[label] = difficulty_counts.get(label, 0) + 1
        
        # Display as simple bar chart using text
        chart_text = ""
        max_count = max(difficulty_counts.values()) if difficulty_counts.values() else 1
        
        for difficulty, count in difficulty_counts.items():
            bar_length = int((count / max_count) * 20) if max_count > 0 else 0
            bar = "█" * bar_length
            chart_text += f"{difficulty:8}: {bar} ({count})\n"
        
        chart_label = ttk.Label(difficulty_chart, text=chart_text, font=("Courier", 10), justify="left")
        chart_label.pack(anchor="w", padx=10)
        
        # Activity section
        activity_title = ttk.Label(self.activity_frame, text="Recent Achievements", font=("Segoe UI", 12, "bold"))
        activity_title.pack(anchor="w", pady=(0, 10))
        
        if user_milestones:
            for milestone in user_milestones[:5]:  # Show only first 5
                badge_symbols = {"BRONZE": "🥉", "SILVER": "🥈", "GOLD": "🥇"}
                symbol = badge_symbols.get(milestone['badge_type'], "🏆")
                
                activity_item = ttk.Frame(self.activity_frame, style="Card.TFrame", padding=5)
                activity_item.pack(fill="x", pady=2)
                
                ttk.Label(
                    activity_item, 
                    text=f"{symbol} {milestone['name']} - Achieved on {milestone['achieved_at']}",
                    font=("Segoe UI", 10)
                ).pack(anchor="w")
        else:
            ttk.Label(self.activity_frame, text="No achievements yet. Keep learning!").pack(anchor="w")

class HistoryScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        ttk.Label(self.card, text="Recommendation History", font=("Segoe UI", 16, "bold")).pack(pady=(0, 10))

        self.listbox = tk.Listbox(self.card, height=10)
        self.listbox.pack(fill="x", pady=5)

        self.text = tk.Text(self.card, wrap="word", height=10)
        self.text.pack(fill="both", expand=True)

        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        nav = ttk.Frame(self.card)
        nav.pack(fill="x", pady=(10, 0))
        ttk.Button(nav, text="Back", command=lambda: controller.show_frame("ProgressScreen")).pack(side="left")
        ttk.Button(nav, text="Analytics", command=lambda: controller.show_frame("AnalyticsScreen")).pack(side="right")

    def on_show(self):
        self.listbox.delete(0, tk.END)
        self.text.delete("1.0", tk.END)

        from recommender.models import RecommendationHistory

        user = self.controller.current_user
        if not user:
            return

        self.histories = list(RecommendationHistory.objects.filter(user_profile=user).order_by("-created_at")[:20])
        for h in self.histories:
            self.listbox.insert(tk.END, f"{h.created_at:%Y-%m-%d %H:%M} - {h.stage_snapshot}")

    def on_select(self, event=None):
        if not hasattr(self, "histories"):
            return
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        h = self.histories[idx]
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, f"Input: {h.input_data}\n\nStreams: {h.output_streams}\n\nSkills: {h.output_skill_paths}")


class AnalyticsScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        ttk.Label(self.card, text="Offline Analytics", font=("Segoe UI", 16, "bold")).pack(pady=(0, 10))

        self.text = tk.Text(self.card, wrap="word", height=18)
        self.text.pack(fill="both", expand=True)

        nav = ttk.Frame(self.card)
        nav.pack(fill="x", pady=(10, 0))
        ttk.Button(nav, text="Back", command=lambda: controller.show_frame("HistoryScreen")).pack(side="left")
        ttk.Button(nav, text="Home", command=lambda: controller.show_frame("HomeScreen")).pack(side="right")
        ttk.Button(nav, text="Feedback", command=lambda: controller.show_frame("FeedbackScreen")).pack(side="right", padx=(5, 0))
        ttk.Button(nav, text="Accessibility", command=lambda: controller.show_frame("AccessibilitySettingsScreen")).pack(side="right", padx=(5, 0))

    def on_show(self):
        self.text.delete("1.0", tk.END)
        most_stream = services.offline_analytics_most_chosen_stream()
        most_path = services.offline_analytics_most_popular_skill_path()

        self.text.insert(tk.END, "Offline usage summary (based on saved sessions):\n\n")
        if most_stream:
            self.text.insert(tk.END, f"Most frequently recommended stream: {most_stream}\n")
        else:
            self.text.insert(tk.END, "No stream data yet.\n")

        if most_path:
            self.text.insert(tk.END, f"Most popular skill path (by progress tracking): {most_path}\n")
        else:
            self.text.insert(tk.END, "No skill path progress data yet.\n")


class FeedbackScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        ttk.Label(self.card, text="Share Your Feedback", font=("Segoe UI", 16, "bold")).pack(pady=(0, 10))

        ttk.Label(self.card, text="Help us improve your experience by sharing your feedback.\nYour input is valuable to us!", 
                  font=("Segoe UI", 10)).pack(pady=(0, 20))

        # Feedback type
        ttk.Label(self.card, text="Feedback Type:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.feedback_type_var = tk.StringVar(value="GENERAL")
        feedback_types = [
            ("General Feedback", "GENERAL"),
            ("Recommendation Quality", "RECOMMENDATION"),
            ("User Interface", "UI_EXPERIENCE"),
            ("Feature Request", "FEATURE_REQUEST"),
            ("Bug Report", "BUG_REPORT"),
        ]
        
        for text, value in feedback_types:
            ttk.Radiobutton(self.card, text=text, variable=self.feedback_type_var, value=value).pack(anchor="w")

        # Rating
        ttk.Label(self.card, text="\nRating (1-5 stars):", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.rating_var = tk.IntVar(value=0)
        rating_frame = ttk.Frame(self.card)
        rating_frame.pack(anchor="w", pady=(5, 10))
        
        self.star_labels = []
        for i in range(1, 6):
            star_label = ttk.Label(rating_frame, text="☆", font=("Segoe UI", 16))
            star_label.pack(side="left", padx=2)
            star_label.bind("<Button-1>", lambda e, rating=i: self.set_rating(rating))
            self.star_labels.append(star_label)

        # Comment
        ttk.Label(self.card, text="Comments:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.comment_text = tk.Text(self.card, height=5, width=60)
        self.comment_text.pack(pady=(5, 10))

        # Suggestions
        ttk.Label(self.card, text="Suggestions for Improvement:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.suggestion_text = tk.Text(self.card, height=5, width=60)
        self.suggestion_text.pack(pady=(5, 10))

        # Buttons
        button_frame = ttk.Frame(self.card)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text="Back", command=lambda: controller.show_frame("AnalyticsScreen")).pack(side="left")
        ttk.Button(button_frame, text="Submit Feedback", command=self.submit_feedback).pack(side="right")
        
        # Success message label
        self.success_label = ttk.Label(self.card, text="", foreground="green")
        self.success_label.pack(pady=(10, 0))

    def set_rating(self, rating):
        """Set the rating and update star display."""
        self.rating_var.set(rating)
        for i, label in enumerate(self.star_labels):
            if i < rating:
                label.config(text="★")
            else:
                label.config(text="☆")

    def submit_feedback(self):
        """Submit the feedback to the database."""
        feedback_type = self.feedback_type_var.get()
        rating = self.rating_var.get() if self.rating_var.get() > 0 else None
        comment = self.comment_text.get("1.0", tk.END).strip()
        suggestion = self.suggestion_text.get("1.0", tk.END).strip()
        
        try:
            services.submit_user_feedback(
                user_profile=self.controller.current_user,
                feedback_type=feedback_type,
                rating=rating,
                comment=comment,
                suggestion=suggestion
            )
            
            # Show success message
            self.success_label.config(text="Thank you for your feedback! We appreciate your input.")
            
            # Clear form
            self.feedback_type_var.set("GENERAL")
            self.rating_var.set(0)
            self.comment_text.delete("1.0", tk.END)
            self.suggestion_text.delete("1.0", tk.END)
            
            # Reset stars
            for label in self.star_labels:
                label.config(text="☆")
                
            # Clear success message after 3 seconds
            self.after(3000, lambda: self.success_label.config(text=""))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit feedback: {str(e)}")

class AccessibilitySettingsScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        ttk.Label(self.card, text="Accessibility Settings", font=("Segoe UI", 16, "bold")).pack(pady=(0, 10))

        ttk.Label(self.card, text="Customize your experience for better accessibility.", 
                  font=("Segoe UI", 10)).pack(pady=(0, 20))

        # Text-to-Speech Settings
        ttk.Label(self.card, text="Text-to-Speech Settings:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10, 5))
        
        # Speech Rate
        rate_frame = ttk.Frame(self.card)
        rate_frame.pack(fill="x", pady=5)
        ttk.Label(rate_frame, text="Speech Rate:").pack(side="left")
        self.rate_var = tk.IntVar(value=150)
        rate_scale = ttk.Scale(rate_frame, from_=50, to=300, variable=self.rate_var, orient="horizontal", command=self.update_rate_display)
        rate_scale.pack(side="left", padx=10, fill="x", expand=True)
        self.rate_display = ttk.Label(rate_frame, text="150")
        self.rate_display.pack(side="left", padx=(10, 0))

        # Speech Volume
        volume_frame = ttk.Frame(self.card)
        volume_frame.pack(fill="x", pady=5)
        ttk.Label(volume_frame, text="Volume:").pack(side="left")
        self.volume_var = tk.DoubleVar(value=0.9)
        volume_scale = ttk.Scale(volume_frame, from_=0.0, to=1.0, variable=self.volume_var, orient="horizontal", command=self.update_volume_display)
        volume_scale.pack(side="left", padx=10, fill="x", expand=True)
        self.volume_display = ttk.Label(volume_frame, text="90%")
        self.volume_display.pack(side="left", padx=(10, 0))

        # Voice Selection
        voice_frame = ttk.Frame(self.card)
        voice_frame.pack(fill="x", pady=5)
        ttk.Label(voice_frame, text="Voice:").pack(side="left")
        self.voice_var = tk.StringVar()
        self.voice_combo = ttk.Combobox(voice_frame, textvariable=self.voice_var, state="readonly", width=30)
        self.voice_combo.pack(side="left", padx=10)
        
        # Test Button
        test_frame = ttk.Frame(self.card)
        test_frame.pack(fill="x", pady=(10, 20))
        ttk.Button(test_frame, text="Test Speech", command=self.test_speech).pack(side="left")
        
        # Apply Button
        apply_frame = ttk.Frame(self.card)
        apply_frame.pack(fill="x", pady=(10, 0))
        ttk.Button(apply_frame, text="Apply Settings", command=self.apply_settings).pack(side="left")
        ttk.Button(apply_frame, text="Reset to Defaults", command=self.reset_defaults).pack(side="left", padx=10)
        ttk.Button(apply_frame, text="Back", command=lambda: controller.show_frame("AnalyticsScreen")).pack(side="right")
        
        # Status message
        self.status_label = ttk.Label(self.card, text="", foreground="green")
        self.status_label.pack(pady=(10, 0))
        
        # Initialize voice options
        self.populate_voice_options()

    def populate_voice_options(self):
        """Populate voice selection combobox with available voices."""
        if self.controller.tts_engine:
            try:
                voices = self.controller.tts_engine.getProperty('voices')
                voice_names = [f"{voice.name} ({voice.id})" for voice in voices]
                self.voice_combo['values'] = voice_names
                
                # Select current voice
                current_voice = self.controller.tts_engine.getProperty('voice')
                for i, voice in enumerate(voices):
                    if voice.id == current_voice:
                        self.voice_combo.current(i)
                        break
            except Exception as e:
                print(f"Error populating voices: {e}")

    def update_rate_display(self, value):
        """Update the rate display label."""
        self.rate_display.config(text=str(int(float(value))))

    def update_volume_display(self, value):
        """Update the volume display label."""
        self.volume_display.config(text=f"{int(float(value)*100)}%")

    def test_speech(self):
        """Test the current speech settings."""
        if self.controller.tts_engine:
            try:
                # Save current settings temporarily
                current_rate = self.controller.tts_engine.getProperty('rate')
                current_volume = self.controller.tts_engine.getProperty('volume')
                
                # Apply test settings
                self.controller.tts_engine.setProperty('rate', self.rate_var.get())
                self.controller.tts_engine.setProperty('volume', self.volume_var.get())
                
                # Speak test phrase
                self.controller.tts_engine.say("This is a test of the text-to-speech settings.")
                self.controller.tts_engine.runAndWait()
                
                # Restore previous settings
                self.controller.tts_engine.setProperty('rate', current_rate)
                self.controller.tts_engine.setProperty('volume', current_volume)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to test speech: {str(e)}")

    def apply_settings(self):
        """Apply the selected accessibility settings."""
        if self.controller.tts_engine:
            try:
                # Apply settings
                self.controller.tts_engine.setProperty('rate', self.rate_var.get())
                self.controller.tts_engine.setProperty('volume', self.volume_var.get())
                
                # Apply voice if selected
                if self.voice_var.get():
                    # Extract voice ID from combo box text
                    voice_text = self.voice_var.get()
                    voice_id = voice_text.split("(")[-1].rstrip(")")
                    self.controller.tts_engine.setProperty('voice', voice_id)
                
                # Show success message
                self.status_label.config(text="Settings applied successfully!")
                
                # Clear success message after 3 seconds
                self.after(3000, lambda: self.status_label.config(text=""))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to apply settings: {str(e)}")

    def reset_defaults(self):
        """Reset settings to defaults."""
        self.rate_var.set(150)
        self.volume_var.set(0.9)
        
        # Update displays
        self.update_rate_display(150)
        self.update_volume_display(0.9)
        
        # Try to select a female voice if available
        if self.controller.tts_engine:
            try:
                voices = self.controller.tts_engine.getProperty('voices')
                for i, voice in enumerate(voices):
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.voice_combo.current(i)
                        break
            except Exception as e:
                print(f"Error resetting voice: {e}")
        
        self.status_label.config(text="Defaults restored. Click Apply to save.")
        
        # Clear success message after 3 seconds
        self.after(3000, lambda: self.status_label.config(text=""))


def show_login_window():
    """Show the login window."""
    def on_login_success(username):
        start_application(username)
    
    def on_register_click():
        login_window.destroy()
        show_registration_window()
    
    login_window = LoginWindow(on_login_success, on_register_click)
    login_window.mainloop()

def show_registration_window():
    """Show the registration window."""
    def on_register_success(username):
        start_application(username)
    
    def on_login_click():
        registration_window.destroy()
        show_login_window()
    
    registration_window = RegistrationWindow(on_register_success, on_login_click)
    registration_window.mainloop()

def start_application(username):
    """Start the main application after successful login or registration."""
    print(f"Starting application for user: {username}")
    try:
        app = ScreenManager(username)
        print("ScreenManager initialized, starting mainloop...")
        app.mainloop()
        print("Application closed.")
    except Exception as e:
        print(f"Error in Tkinter application: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main entry point for the Tkinter application."""
    print("Starting Tkinter application...")
    try:
        # Show login window first
        show_login_window()
    except Exception as e:
        print(f"Error in Tkinter application: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
