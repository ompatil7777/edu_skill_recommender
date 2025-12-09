#!/usr/bin/env python3
"""
Edu & Skill Path Recommender Launcher
=====================================

This script provides an easy way to launch the Edu & Skill Path Recommender application.
It handles environment setup and launches the Kivy-based GUI.

Requirements:
- Python 3.8+
- Django
- Kivy
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        print(f"You are using Python {sys.version}")
        return False
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    missing_packages = []
    
    try:
        import django
        print(f"Django version: {django.VERSION}")
    except ImportError:
        missing_packages.append("Django")
    
    try:
        import kivy
        print(f"Kivy version: {kivy.__version__}")
    except ImportError:
        missing_packages.append("Kivy")
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        print("Please install them using:")
        print(f"  pip install {' '.join(missing_packages)}")
        return False
    
    return True

def setup_django():
    """Setup Django environment."""
    # Add project directory to Python path
    project_dir = Path(__file__).parent.absolute()
    if str(project_dir) not in sys.path:
        sys.path.insert(0, str(project_dir))
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_skill_recommender.settings')
    
    try:
        import django
        django.setup()
        print("Django setup completed successfully.")
        return True
    except Exception as e:
        print(f"Error setting up Django: {e}")
        return False

def run_database_migrations():
    """Run database migrations if needed."""
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'migrate'])
        print("Database migrations completed.")
        return True
    except Exception as e:
        print(f"Error running migrations: {e}")
        return False

def seed_database():
    """Seed database with initial data."""
    try:
        from django.core.management import execute_from_command_line
        print("Seeding database with initial data...")
        execute_from_command_line(['manage.py', 'seed_recommender'])
        execute_from_command_line(['manage.py', 'import_comprehensive_data'])
        print("Database seeding completed.")
        return True
    except Exception as e:
        print(f"Error seeding database: {e}")
        return False

def launch_gui():
    """Launch the Kivy GUI application."""
    try:
        print("Launching Edu & Skill Path Recommender...")
        from kivy_app import EduSkillRecommenderApp
        EduSkillRecommenderApp().run()
        return True
    except Exception as e:
        print(f"Error launching GUI: {e}")
        return False

def main():
    """Main launcher function."""
    print("=" * 50)
    print("Edu & Skill Path Recommender")
    print("=" * 50)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Launch Edu & Skill Path Recommender')
    parser.add_argument('--setup', action='store_true', help='Run initial setup')
    parser.add_argument('--seed', action='store_true', help='Seed database with data')
    parser.add_argument('--migrate', action='store_true', help='Run database migrations')
    args = parser.parse_args()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install the missing dependencies and try again.")
        sys.exit(1)
    
    # Setup Django
    if not setup_django():
        print("\nFailed to setup Django environment.")
        sys.exit(1)
    
    # Handle command line arguments
    if args.migrate or args.setup:
        if not run_database_migrations():
            print("\nFailed to run database migrations.")
            sys.exit(1)
    
    if args.seed or args.setup:
        if not seed_database():
            print("\nFailed to seed database.")
            sys.exit(1)
    
    # Launch GUI
    if not launch_gui():
        print("\nFailed to launch GUI application.")
        sys.exit(1)

if __name__ == "__main__":
    main()