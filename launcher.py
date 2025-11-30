#!/usr/bin/env python
"""
Launcher script for Edu & Skill Path Recommender.
Allows users to choose between Tkinter and Kivy interfaces.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox


def launch_tkinter():
    """Launch the Tkinter version of the application."""
    try:
        # Import and run the Tkinter app
        import importlib.util
        spec = importlib.util.spec_from_file_location("desktop_app", "desktop_app.py")
        desktop_app = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(desktop_app)
        desktop_app.main()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch Tkinter app: {e}")


def launch_kivy():
    """Launch the Kivy version of the application."""
    try:
        # Import and run the Kivy app
        import importlib.util
        spec = importlib.util.spec_from_file_location("kivy_app", "kivy_app.py")
        kivy_app = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(kivy_app)
        kivy_app.EduSkillRecommenderApp().run()
    except ImportError:
        messagebox.showerror("Error", "Kivy is not installed. Please install it with 'pip install kivy' to use this interface.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch Kivy app: {e}")


class LauncherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Edu & Skill Path Recommender - Launcher")
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Center the window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (300 // 2)
        self.geometry(f"400x300+{x}+{y}")
        
        # Create UI
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        title = ttk.Label(
            self, 
            text="Edu & Skill Path Recommender", 
            font=("Arial", 16, "bold")
        )
        title.pack(pady=20)
        
        # Description
        desc = ttk.Label(
            self,
            text="Choose your preferred interface:",
            font=("Arial", 12)
        )
        desc.pack(pady=10)
        
        # Tkinter button
        tk_btn = ttk.Button(
            self,
            text="🖥️ Tkinter Interface",
            command=launch_tkinter,
            width=25
        )
        tk_btn.pack(pady=15)
        
        # Kivy button
        kivy_btn = ttk.Button(
            self,
            text="📱 Kivy Interface",
            command=launch_kivy,
            width=25
        )
        kivy_btn.pack(pady=15)
        
        # Info text
        info = ttk.Label(
            self,
            text="Both interfaces provide the same functionality.\nChoose based on your preference.",
            font=("Arial", 10),
            foreground="gray"
        )
        info.pack(pady=20)
        
        # Exit button
        exit_btn = ttk.Button(
            self,
            text="Exit",
            command=self.quit,
            width=15
        )
        exit_btn.pack(pady=10)


def main():
    """Main entry point for the launcher."""
    app = LauncherApp()
    app.mainloop()


if __name__ == "__main__":
    main()