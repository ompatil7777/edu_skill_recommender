# Edu & Skill Path Recommender (Enhanced Desktop, Offline)

Technologies used (as required):
- **Language:** Python
- **Backend / ORM / Admin:** Django
- **Database:** SQLite (via Django ORM)
- **Desktop GUI Options:** Tkinter (default) or Kivy (optional)
- **No** HTML/CSS/JS, React, Flutter, external APIs, ML/AI, or cloud services.

## Enhanced Features

- Education stage classification from Primary (1–5) up to Working Professional and Counselor.
- Interest & aptitude questionnaire (rule-based scoring, no ML) with questions for different education stages.
- Stream recommendation for classes 9–12 (Science / Commerce / Arts / Vocational) with:
  - Pros & cons
  - Required strengths
  - Subjects
  - Early preparation ideas
- Career direction suggestions per stream with example entrance exams (Engineering, Medicine, CA, CS, Law, Psychology, Mass Communication, Web Development, Digital Marketing).
- Skill-path roadmaps for UG/PG and Professionals, with:
  - Beginner → Intermediate → Advanced levels
  - Difficulty (Easy / Medium / Hard)
  - Time estimates (weeks) for each step
  - Example paths: Cloud Support Engineer, Full-Stack Python Developer, Data Science, Digital Marketing
- Plan A / Plan B / Plan C routes for streams and skill paths.
- Explanation text for recommendations (why it fits you).
- Parent/teacher friendly mode.
- Professional career switcher mode (e.g., Call Center → Cloud Support Engineer).
- Learning milestones (Level 1 Foundations → Level 4 Projects).
- Activity suggestions for Primary, Middle, and High school (clubs, debates, fairs, etc.).
- Motivation tips stored in DB for different audiences and stages.
- History tracking of sessions and progress.
- Progress tracker with NOT STARTED / IN PROGRESS / COMPLETED and % done.
- Difficulty visualization as text.
- Offline analytics via raw SQL (most recommended stream and most popular skill path).
- Text-to-speech functionality for accessibility.
- Two interface options: Tkinter (traditional desktop) and Kivy (modern touch interface, optional).
- Launcher application to easily choose between interfaces.
- **NEW: User Feedback System** - Collect and analyze user feedback to improve the application.
- **NEW: Accessibility Settings** - Customizable text-to-speech settings for better user experience.
- **NEW: Milestone Tracking** - Achievement badges and progress milestones.
- **NEW: Interactive Dashboards** - Visual progress tracking and analytics.
- **NEW: Learning Resources** - Curated YouTube videos and learning materials.

## Project structure

- `manage.py` – standard Django management entry point.
- `edu_skill_recommender/` – Django project settings and URLs.
- `recommender/` – core app with:
  - `models.py` – stages, profiles, interests, questions, streams, careers, skills, paths, rules, history, progress, tips, activities, feedback, milestones, learning resources.
  - `admin.py` – Django admin registrations (only admins use web admin).
  - `services.py` – rule-based recommendation logic, offline analytics, and feedback processing.
  - `tests.py` – Unit tests for models and services.
  - `management/commands/seed_recommender.py` – sample seed data including feedback and milestones.
- `desktop_app.py` – Tkinter desktop GUI that uses Django ORM and services.
- `kivy_app.py` – Kivy desktop GUI that uses Django ORM and services.
- `launcher.py` – Simple launcher to choose between Tkinter and Kivy interfaces.
- `test_gui.py` – Tests for GUI components.

## Setup instructions

1. **Create and activate a virtual environment (recommended)**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # on Windows
   ```

2. **Install Django** (if not already installed)

   ```bash
   pip install django
   ```
   
   Optionally, to use the Kivy interface:
   
   ```bash
   pip install kivy
   ```

3. **Apply migrations**

   ```bash
   python manage.py migrate
   ```

4. **Seed sample data** (stages, streams, careers, skills, paths, basic questions, tips, feedback, milestones)

   ```bash
   python manage.py seed_recommender
   ```

5. **Create a superuser for Django admin (optional but recommended)**

   ```bash
   python manage.py createsuperuser
   ```

6. **Run the desktop application**

   You can launch either interface directly:
   
   For Tkinter GUI:
   ```bash
   python desktop_app.py
   ```

   For Kivy GUI:
   ```bash
   python kivy_app.py
   ```
   
   Or use the launcher to choose your preferred interface:
   ```bash
   python launcher.py
   ```

7. **(Optional) Use Django admin to customize data**

   ```bash
   python manage.py runserver
   ```

   Then open the admin URL in a browser (only for admins) and manage:
   - Streams and careers
   - Question sets and option scores
   - Skills and skill paths
   - Motivation tips and activity suggestions
   - Feedback and milestone configurations

## Desktop UI walkthrough (Tkinter version)

1. **Home Screen**

## Desktop UI walkthrough (Kivy version)

The Kivy version provides the same functionality as the Tkinter version with a modern touch interface. All features are identical:

1. **Home Screen**
   - Choose who you are:
     - Student (Class 1–12)
     - UG/PG Student
     - Working Professional
     - Parent/Teacher/Counselor
   - Enter your name (used to save progress and history).

2. **Stage Selection**
   - For **students**: select your current class (1–12).
     - Classes 1–5 → Primary
     - 6–8 → Middle
     - 9–10 → High School
     - 11–12 → Higher Secondary
   - For **professionals**: enter current job role and optional target role.
   - For **UG/PG and counselors**: no extra fields; continue.

3. **Interest & Aptitude Questionnaire**
   - You see ~2–5 questions (can be extended in admin) for your stage.
   - Each question has simple options like:
     - “I enjoy them a lot”
     - “They are okay”
     - “I avoid them”
   - Each option contributes rule-based scores to categories:
     - Logical, Analytical, Creative, Practical, People, Scientific, Design.

4. **Subject Strengths (Class 9–12 only)**
   - Rate comfort (1–10) for:
     - Mathematics, Science, English, Business, Creativity, Languages, Social Studies.
   - The app computes:
     - `science_score = maths + science + logical_interest`
     - `commerce_score = maths + english + business_interest`
     - `arts_score = creativity + language + social_interest`
     - `vocational_score` based on practical interest and overall academics.

5. **Results Screen**
   - For **Class 9–12 students**:
     - Shows **Plan A / Plan B / Plan C streams** with:
       - Explanation (why it fits you)
       - Required strengths
       - Subjects
       - Early preparation ideas
     - Shows text-only career directions for the best stream (Plan A) with example entrance exams.
   - For **Primary and Middle school**:
     - Shows activity suggestions (e.g., robotics club, debates) and simple motivation tips.
   - For **Professionals**:
     - Shows a career switch roadmap (e.g. Call Center → Cloud Support Engineer) with steps and time estimates.
   - For **UG/PG**:
     - Brief text before moving to skill roadmaps.
   - **NEW: Text-to-Speech** - Listen to recommendations with the "🔊 Read Recommendations" button.

6. **Skill Roadmap Screen**
   - Shows **Plan A / Plan B / Plan C** skill paths:
     - Example: "Cloud Support Engineer Path"
       - Linux Basics (Easy, Level 1, 2 weeks)
       - Networking (Medium, Level 2, 3 weeks)
       - AWS Core Services (Medium, Level 2, 3 weeks)
       - IAM & Security (Hard, Level 3, 3 weeks)
       - Monitoring (Medium, Level 3, 2 weeks)
       - Scripting (Medium, Level 4, 3 weeks)
     - Example: "Full-Stack Python Developer Path"
       - Python Basics → Python OOP → Django → SQL → Deployment
   - Levels follow:
     - Level 1 – Foundations
     - Level 2 – Core
     - Level 3 – Tools / Frameworks
     - Level 4 – Projects / Deployment
   - When opened, the app initializes progress tracking for the primary path (Plan A).
   - **NEW: Text-to-Speech** - Listen to roadmaps with the "🔊 Read Roadmaps" button.

7. **Progress Screen**
   - Shows the skills for the tracked path in a simple table:
     - Skill step | Status
   - Status options:
     - NOT STARTED
     - IN PROGRESS
     - COMPLETED
   - You can select a step and mark it In Progress or Completed.
   - At the top you see a summary:
     - `Completed X of Y (Z%)`
     - Difficulty mix (Easy / Medium / Hard counts).
     - **NEW: Progress Bar** - Visual representation of completion percentage.
     - **NEW: Milestone Tracking** - Display of earned achievements and badges.
     - **NEW: Streak Counter** - Track consecutive days of learning.

8. **History Screen**
   - Lists past recommendation sessions for the current user.
   - Selecting a session shows stored input data and recommended streams/paths.

9. **Analytics Screen**
   - Uses raw SQL queries to show:
     - Most frequently recommended stream (from history JSON text).
     - Most popular skill path (from tracked progress records).
   - Output is text-only, no graphs.

## Notes

- All recommendations are **rule-based**, implemented in Python in `recommender/services.py`.
- The system runs 100% offline using SQLite.
- Django admin is only for admins to maintain data; students and other users interact only through the Tkinter desktop app.
