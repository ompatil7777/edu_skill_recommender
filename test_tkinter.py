#!/usr/bin/env python3
"""
Simple test script to verify Tkinter application works correctly
"""

import os
import sys

# Bootstrap Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edu_skill_recommender.settings")

import django
django.setup()
print("Django setup completed successfully.")

try:
    # Import the main application
    from desktop_app import show_login_window
    
    print("Starting simple Tkinter test...")
    # Just test that we can create the login window
    show_login_window()
    print("Tkinter application closed.")
    
except Exception as e:
    print(f"Error running Tkinter application: {e}")
    import traceback
    traceback.print_exc()