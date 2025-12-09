import os
import sys
import webbrowser

# Bootstrap Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edu_skill_recommender.settings")

import django
django.setup()

try:
    from kivy.app import App
    from kivy.uix.screenmanager import ScreenManager, Screen
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.textinput import TextInput
    from kivy.uix.spinner import Spinner
    from kivy.uix.checkbox import CheckBox
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.popup import Popup
    from kivy.uix.slider import Slider
    from kivy.metrics import dp
    from kivy.properties import ObjectProperty
except ImportError:
    print("Kivy is not installed. Please install it with 'pip install kivy' to use this interface.")
    sys.exit(1)

from recommender.models import EducationStage, Question, OptionScore, Stream, UserProfile, Feedback
from recommender import services


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # App title with better styling
        title = Label(
            text='Edu & Skill Path Recommender',
            size_hint_y=None,
            height=dp(60),
            font_size=dp(26),
            bold=True,
            color=(0.2, 0.6, 0.8, 1)  # Blue color
        )
        self.layout.add_widget(title)
        
        subtitle = Label(
            text='Your personalized education and career guidance platform',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(16),
            color=(0.3, 0.3, 0.3, 1)
        )
        self.layout.add_widget(subtitle)
        
        # Mode selection with improved layout
        mode_label = Label(
            text='Who is using this tool today?',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(18),
            bold=True
        )
        self.layout.add_widget(mode_label)
        
        # Mode selection
        self.mode_buttons = {}
        modes = [
            ("School Student (Class 1-12)", "STUDENT"),
            ("College Student (UG/PG)", "UGPG"),
            ("Working Professional", "PROFESSIONAL"),
            ("Parent / Teacher / Counselor", "COUNSELOR"),
        ]
        
        self.mode_selection = GridLayout(cols=1, spacing=15, size_hint_y=None)
        self.mode_selection.bind(minimum_height=self.mode_selection.setter('height'))
        
        self.selected_mode = "STUDENT"
        for text, val in modes:
            btn_layout = BoxLayout(size_hint_y=None, height=dp(50))
            checkbox = CheckBox(group='mode', size_hint_x=None, width=dp(40))
            if val == "STUDENT":
                checkbox.active = True
            checkbox.bind(active=lambda instance, value, mode=val: self.on_mode_select(mode, value))
            
            label = Label(text=text, halign='left', valign='middle', font_size=dp(14))
            label.bind(size=label.setter('text_size'))
            
            btn_layout.add_widget(checkbox)
            btn_layout.add_widget(label)
            self.mode_selection.add_widget(btn_layout)
        
        scroll = ScrollView(size_hint_y=0.4)
        scroll.add_widget(self.mode_selection)
        self.layout.add_widget(scroll)
        
        # Name input with better styling
        name_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))
        name_label = Label(
            text='Your name (for saving progress):',
            size_hint_y=None,
            height=dp(30),
            halign='left',
            font_size=dp(14)
        )
        name_label.bind(size=name_label.setter('text_size'))
        name_layout.add_widget(name_label)
        
        self.name_input = TextInput(multiline=False, size_hint_y=None, height=dp(40), font_size=dp(14))
        name_layout.add_widget(self.name_input)
        self.layout.add_widget(name_layout)
        
        # Next button with better styling
        next_btn = Button(
            text='Get Started',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16),
            background_color=(0.2, 0.7, 0.3, 1)  # Green color
        )
        next_btn.bind(on_press=self.next_clicked)
        self.layout.add_widget(next_btn)
        
        self.add_widget(self.layout)
    
    def on_mode_select(self, mode, active):
        if active:
            self.selected_mode = mode
    
    def next_clicked(self, instance):
        name = self.name_input.text.strip() or "Guest"
        mode = self.selected_mode
        
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
        
        self.manager.current_user = user
        self.manager.current_stage = stage
        self.manager.current = 'stage_selection'


class StageSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(
            text='Select your current stage',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(20),
            bold=True
        )
        self.layout.add_widget(title)
        
        # Class selection for students
        self.class_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))
        class_label = Label(
            text='Current class (1-12):',
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        class_label.bind(size=class_label.setter('text_size'))
        self.class_layout.add_widget(class_label)
        
        self.class_spinner = Spinner(
            text='10',
            values=[str(i) for i in range(1, 13)],
            size_hint_y=None,
            height=dp(40)
        )
        self.class_layout.add_widget(self.class_spinner)
        
        # Role inputs for professionals
        self.role_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(150))
        current_role_label = Label(
            text='Current job role:',
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        current_role_label.bind(size=current_role_label.setter('text_size'))
        self.role_layout.add_widget(current_role_label)
        
        self.current_role_input = TextInput(multiline=False, size_hint_y=None, height=dp(40))
        self.role_layout.add_widget(self.current_role_input)
        
        target_role_label = Label(
            text='Target role (optional):',
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        target_role_label.bind(size=target_role_label.setter('text_size'))
        self.role_layout.add_widget(target_role_label)
        
        self.target_role_input = TextInput(multiline=False, size_hint_y=None, height=dp(40))
        self.role_layout.add_widget(self.target_role_input)
        
        # Info label
        self.info_label = Label(
            text='For school students, we will use your class to suggest suitable streams or activities.',
            size_hint_y=None,
            height=dp(60),
            halign='left',
            valign='top'
        )
        self.info_label.bind(size=self.info_label.setter('text_size'))
        
        # Navigation buttons
        nav_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=10)
        back_btn = Button(text='Back')
        back_btn.bind(on_press=self.back_clicked)
        nav_layout.add_widget(back_btn)
        
        next_btn = Button(text='Next')
        next_btn.bind(on_press=self.next_clicked)
        nav_layout.add_widget(next_btn)
        
        self.layout.add_widget(self.class_layout)
        self.layout.add_widget(self.role_layout)
        self.layout.add_widget(self.info_label)
        self.layout.add_widget(nav_layout)
        
        self.add_widget(self.layout)
    
    def on_enter(self):
        user = self.manager.current_user
        if not user:
            return
            
        if user.education_stage.code in (
            EducationStage.PRIMARY,
            EducationStage.MIDDLE,
            EducationStage.HIGH_SCHOOL,
            EducationStage.HIGHER_SECONDARY,
        ):
            self.class_layout.opacity = 1
            self.role_layout.opacity = 0
            self.info_label.text = "For school students, we will use your class to suggest suitable streams or activities."
        elif user.education_stage.code == EducationStage.PROFESSIONAL:
            self.class_layout.opacity = 0
            self.role_layout.opacity = 1
            self.info_label.text = "For professionals, we will build a skill roadmap based on your current and target roles."
        else:
            self.class_layout.opacity = 0
            self.role_layout.opacity = 0
            self.info_label.text = "For UG/PG students or counselors, we will ask about interests and suggest domains and skills."
    
    def back_clicked(self, instance):
        self.manager.current = 'home'
    
    def next_clicked(self, instance):
        user = self.manager.current_user
        if not user:
            return
        
        if user.education_stage.code in (
            EducationStage.PRIMARY,
            EducationStage.MIDDLE,
            EducationStage.HIGH_SCHOOL,
            EducationStage.HIGHER_SECONDARY,
        ):
            current_class = int(self.class_spinner.text)
            user.current_class = current_class
            user.save()
            
            # Refine stage
            stage = services.classify_stage(current_class=current_class, is_professional=False, is_counselor=user.is_parent_mode)
            user.education_stage = stage
            user.save()
            self.manager.current_stage = stage
        elif user.education_stage.code == EducationStage.PROFESSIONAL:
            user.current_role = self.current_role_input.text.strip()
            user.target_role = self.target_role_input.text.strip()
            user.save()
        else:
            # UG/PG or counselor, no extra fields
            pass
        
        self.manager.current = 'questionnaire'


class QuestionnaireScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(
            text='Interest & Aptitude Questionnaire',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(22),
            bold=True,
            color=(0.2, 0.6, 0.8, 1)  # Blue color
        )
        self.layout.add_widget(title)
        
        desc = Label(
            text='Answer a few simple questions about what you enjoy. This helps us suggest paths.',
            size_hint_y=None,
            height=dp(40),
            halign='left',
            font_size=dp(14)
        )
        desc.bind(size=desc.setter('text_size'))
        self.layout.add_widget(desc)
        
        # Progress indicator
        self.progress_label = Label(
            text='Question 1 of 5',
            size_hint_y=None,
            height=dp(30),
            halign='right',
            font_size=dp(12),
            color=(0.5, 0.5, 0.5, 1)
        )
        self.layout.add_widget(self.progress_label)
        
        # Questions area
        self.questions_scroll = ScrollView()
        self.questions_layout = GridLayout(cols=1, spacing=15, size_hint_y=None)
        self.questions_layout.bind(minimum_height=self.questions_layout.setter('height'))
        self.questions_scroll.add_widget(self.questions_layout)
        self.layout.add_widget(self.questions_scroll)
        
        # Navigation
        nav_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=10)
        back_btn = Button(text='Back', background_color=(0.7, 0.7, 0.7, 1))
        back_btn.bind(on_press=self.back_clicked)
        nav_layout.add_widget(back_btn)
        
        next_btn = Button(text='Next', background_color=(0.2, 0.7, 0.3, 1))
        next_btn.bind(on_press=self.next_clicked)
        nav_layout.add_widget(next_btn)
        
        self.layout.add_widget(nav_layout)
        self.add_widget(self.layout)
        
        self.option_vars = {}
        self.current_question_index = 0

    def on_enter(self):
        # Clear previous questions
        self.questions_layout.clear_widgets()
        self.option_vars.clear()
        
        stage = self.manager.current_stage
        if not stage:
            return
        
        qs = Question.objects.filter(stage=stage, is_active=True)[:5]
        if not qs:
            no_questions = Label(
                text='No questions defined for this stage (admin can add some).',
                size_hint_y=None,
                height=dp(40),
                color=(1, 0, 0, 1)
            )
            self.questions_layout.add_widget(no_questions)
            return
        
        for q in qs:
            q_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(150))
            q_label = Label(
                text=q.text,
                size_hint_y=None,
                height=dp(60),
                halign='left',
                valign='top'
            )
            q_label.bind(size=q_label.setter('text_size'))
            q_layout.add_widget(q_label)
            
            # Options
            options_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
            options_layout.bind(minimum_height=options_layout.setter('height'))
            
            var = f"question_{q.id}"
            self.option_vars[q.id] = {"var": var, "selected": None}
            
            for opt in q.options.all():
                opt_layout = BoxLayout(size_hint_y=None, height=dp(30))
                checkbox = CheckBox(group=var, size_hint_x=None, width=dp(40))
                checkbox.bind(active=lambda cb, value, opt_id=opt.id, q_id=q.id: self.on_option_select(q_id, opt_id, value))
                
                opt_label = Label(text=opt.option_text, halign='left')
                opt_label.bind(size=opt_label.setter('text_size'))
                
                opt_layout.add_widget(checkbox)
                opt_layout.add_widget(opt_label)
                options_layout.add_widget(opt_layout)
            
            q_layout.add_widget(options_layout)
            self.questions_layout.add_widget(q_layout)
    
    def on_option_select(self, question_id, option_id, active):
        if active:
            self.option_vars[question_id]["selected"] = option_id
    
    def back_clicked(self, instance):
        self.manager.current = 'stage_selection'
    
    def next_clicked(self, instance):
        answers = []
        for qid, var_data in self.option_vars.items():
            opt_id = var_data["selected"]
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
        
        self.manager.interest_answers = answers
        
        stage_code = self.manager.current_stage.code if self.manager.current_stage else None
        if stage_code in (EducationStage.HIGH_SCHOOL, EducationStage.HIGHER_SECONDARY):
            self.manager.current = 'subject_strength'
        else:
            self.manager.current = 'results'


class SubjectStrengthScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(
            text='Subject Comfort Levels (1-10)',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(20),
            bold=True
        )
        self.layout.add_widget(title)
        
        desc = Label(
            text='Rate how comfortable you feel with each subject. 1 = very low, 10 = very high.',
            size_hint_y=None,
            height=dp(40),
            halign='left'
        )
        desc.bind(size=desc.setter('text_size'))
        self.layout.add_widget(desc)
        
        # Subject inputs
        self.inputs = {}
        subjects = [
            ("maths", "Mathematics"),
            ("science", "Science"),
            ("english", "English"),
            ("business", "Business / Commerce"),
            ("creativity", "Art / Creativity"),
            ("language", "Languages"),
            ("social", "Social Studies / People"),
        ]
        
        self.subjects_scroll = ScrollView()
        self.subjects_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.subjects_layout.bind(minimum_height=self.subjects_layout.setter('height'))
        
        for name, label in subjects:
            subj_layout = BoxLayout(size_hint_y=None, height=dp(40))
            subj_label = Label(
                text=f"{label}:",
                size_hint_x=None,
                width=dp(200),
                halign='left'
            )
            subj_label.bind(size=subj_label.setter('text_size'))
            
            spinner = Spinner(
                text='7',
                values=[str(i) for i in range(1, 11)],
                size_hint_x=None,
                width=dp(60)
            )
            self.inputs[name] = spinner
            
            subj_layout.add_widget(subj_label)
            subj_layout.add_widget(spinner)
            self.subjects_layout.add_widget(subj_layout)
        
        self.subjects_scroll.add_widget(self.subjects_layout)
        self.layout.add_widget(self.subjects_scroll)
        
        # Navigation
        nav_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=10)
        back_btn = Button(text='Back')
        back_btn.bind(on_press=self.back_clicked)
        nav_layout.add_widget(back_btn)
        
        next_btn = Button(text='See Recommendations')
        next_btn.bind(on_press=self.next_clicked)
        nav_layout.add_widget(next_btn)
        
        self.layout.add_widget(nav_layout)
        self.add_widget(self.layout)
    
    def back_clicked(self, instance):
        self.manager.current = 'questionnaire'
    
    def next_clicked(self, instance):
        levels = {k: int(v.text) for k, v in self.inputs.items()}
        self.manager.subject_levels = levels
        self.manager.current = 'results'


class ResultsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(
            text='Your Recommendations',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(22),
            bold=True,
            color=(0.2, 0.6, 0.8, 1)  # Blue color
        )
        self.layout.add_widget(title)
        
        desc = Label(
            text='Based on your profile and responses, here are our recommendations:',
            size_hint_y=None,
            height=dp(40),
            halign='left',
            font_size=dp(14)
        )
        desc.bind(size=desc.setter('text_size'))
        self.layout.add_widget(desc)
        
        # Results area
        self.results_scroll = ScrollView()
        self.results_layout = GridLayout(cols=1, spacing=15, size_hint_y=None)
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        self.results_scroll.add_widget(self.results_layout)
        self.layout.add_widget(self.results_scroll)
        
        # Navigation
        self.nav_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=10)
        back_btn = Button(text='Back', background_color=(0.7, 0.7, 0.7, 1))
        back_btn.bind(on_press=self.back_clicked)
        self.nav_layout.add_widget(back_btn)
        
        self.skill_btn = Button(text='Skill Roadmap', background_color=(0.3, 0.5, 0.8, 1))
        self.skill_btn.bind(on_press=self.skill_roadmap_clicked)
        self.nav_layout.add_widget(self.skill_btn)
        
        # Add Learning Resources button
        self.resources_btn = Button(text='Learning Resources', background_color=(0.2, 0.7, 0.3, 1))
        self.resources_btn.bind(on_press=self.learning_resources_clicked)
        self.nav_layout.add_widget(self.resources_btn)
        
        self.layout.add_widget(self.nav_layout)
        self.add_widget(self.layout)
        
        # Add Professional Development button (initially hidden)
        self.prof_dev_btn = Button(text='Professional Development Plan', background_color=(0.8, 0.5, 0.2, 1))
        self.prof_dev_btn.bind(on_press=self.professional_development_clicked)
    
    def on_enter(self):
        # Show/hide professional development button based on user type
        user = self.manager.current_user
        if user and user.education_stage.code == EducationStage.PROFESSIONAL:
            if self.prof_dev_btn not in self.nav_layout.children:
                self.nav_layout.add_widget(self.prof_dev_btn)
        else:
            if self.prof_dev_btn in self.nav_layout.children:
                self.nav_layout.remove_widget(self.prof_dev_btn)
        
        self.results_layout.clear_widgets()
        
        user = self.manager.current_user
        stage = self.manager.current_stage
        if not user or not stage:
            return
        
        profile = services.InterestProfile.from_option_scores(self.manager.interest_answers)
        
        if stage.code in (EducationStage.HIGH_SCHOOL, EducationStage.HIGHER_SECONDARY):
            streams = services.recommend_streams_with_explanations(profile, self.manager.subject_levels)
            self.manager.stream_recommendations = streams
            
            for plan_label in ["Plan A", "Plan B", "Plan C"]:
                if plan_label not in streams:
                    continue
                data = streams[plan_label]
                s = data["stream"]
                
                plan_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(300))
                plan_title = Label(
                    text=f'{s.name} Stream ({plan_label})',
                    size_hint_y=None,
                    height=dp(40),
                    font_size=dp(16),
                    bold=True,
                    halign='left'
                )
                plan_title.bind(size=plan_title.setter('text_size'))
                plan_layout.add_widget(plan_title)
                
                explanation = Label(
                    text=data["explanation"],
                    size_hint_y=None,
                    height=dp(60),
                    halign='left',
                    valign='top'
                )
                explanation.bind(size=explanation.setter('text_size'))
                plan_layout.add_widget(explanation)
                
                # Details
                details_scroll = ScrollView(size_hint_y=None, height=dp(150))
                details_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
                details_layout.bind(minimum_height=details_layout.setter('height'))
                
                details = [
                    f"Required strengths: {data['required_strengths']}",
                    f"Key subjects: {data['key_subjects']}",
                    f"Early preparation: {data['early_preparation_ideas']}"
                ]
                
                for detail in details:
                    detail_label = Label(
                        text=detail,
                        size_hint_y=None,
                        height=dp(40),
                        halign='left',
                        valign='top'
                    )
                    detail_label.bind(size=detail_label.setter('text_size'))
                    details_layout.add_widget(detail_label)
                
                details_scroll.add_widget(details_layout)
                plan_layout.add_widget(details_scroll)
                
                self.results_layout.add_widget(plan_layout)
        elif stage.code in (EducationStage.PRIMARY, EducationStage.MIDDLE):
            activities_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(200))
            activities_title = Label(
                text='Growth activities (not career-specific yet)',
                size_hint_y=None,
                height=dp(40),
                font_size=dp(16),
                bold=True,
                halign='left'
            )
            activities_title.bind(size=activities_title.setter('text_size'))
            activities_layout.add_widget(activities_title)
            
            activities_scroll = ScrollView(size_hint_y=None, height=dp(150))
            activities_text_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
            activities_text_layout.bind(minimum_height=activities_text_layout.setter('height'))
            
            for act in services.get_activity_suggestions(stage):
                act_label = Label(
                    text=f"• {act.title}: {act.description}",
                    size_hint_y=None,
                    height=dp(40),
                    halign='left',
                    valign='top'
                )
                act_label.bind(size=act_label.setter('text_size'))
                activities_text_layout.add_widget(act_label)
            
            activities_scroll.add_widget(activities_text_layout)
            activities_layout.add_widget(activities_scroll)
            self.results_layout.add_widget(activities_layout)
        else:
            summary_label = Label(
                text='Continue to the skill roadmap screen for more personalized recommendations.',
                size_hint_y=None,
                height=dp(40),
                halign='left'
            )
            summary_label.bind(size=summary_label.setter('text_size'))
            self.results_layout.add_widget(summary_label)
    
    def back_clicked(self, instance):
        stage_code = self.manager.current_stage.code if self.manager.current_stage else None
        if stage_code in (EducationStage.HIGH_SCHOOL, EducationStage.HIGHER_SECONDARY):
            self.manager.current = 'subject_strength'
        else:
            self.manager.current = 'questionnaire'
    
    def skill_roadmap_clicked(self, instance):
        self.manager.current = 'skill_roadmap'
    
    def learning_resources_clicked(self, instance):
        self.manager.current = 'learning_resources'
    
    def professional_development_clicked(self, instance):
        self.manager.current = 'professional_development'


class SkillRoadmapScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(
            text='Skill Path Roadmaps',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(20),
            bold=True
        )
        self.layout.add_widget(title)
        
        # Progress visualization area
        self.progress_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=10)
        
        # Progress bar
        from kivy.uix.progressbar import ProgressBar
        self.progress_bar = ProgressBar(max=100, size_hint_x=0.8)
        self.progress_layout.add_widget(self.progress_bar)
        
        self.progress_label = Label(
            text='0%',
            size_hint_x=0.2,
            halign='center',
            font_size=dp(16),
            bold=True
        )
        self.progress_layout.add_widget(self.progress_label)
        
        self.layout.add_widget(self.progress_layout)
        
        # Roadmaps area
        self.roadmaps_scroll = ScrollView()
        self.roadmaps_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.roadmaps_layout.bind(minimum_height=self.roadmaps_layout.setter('height'))
        self.roadmaps_scroll.add_widget(self.roadmaps_layout)
        self.layout.add_widget(self.roadmaps_scroll)
        
        # Navigation
        nav_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=10)
        back_btn = Button(text='Back')
        back_btn.bind(on_press=self.back_clicked)
        nav_layout.add_widget(back_btn)
        
        progress_btn = Button(text='Track Progress')
        progress_btn.bind(on_press=self.progress_clicked)
        nav_layout.add_widget(progress_btn)
        
        self.layout.add_widget(nav_layout)
        self.add_widget(self.layout)
    
    def on_enter(self):
        self.roadmaps_layout.clear_widgets()
        
        user = self.manager.current_user
        stage = self.manager.current_stage
        if not user or not stage:
            return
        
        stream = None
        if hasattr(self.manager, 'stream_recommendations') and self.manager.stream_recommendations:
            best = self.manager.stream_recommendations.get("Plan A")
            if best:
                stream = best["stream"]
        
        # Create interest profile from user answers
        profile = services.InterestProfile.from_option_scores(self.manager.interest_answers)
        paths = services.get_skill_paths_for_target(stage, stream, getattr(user, "target_role", ""), profile)
        if not paths:
            no_paths = Label(
                text='No skill paths defined yet. Admin can add them in Django admin.',
                size_hint_y=None,
                height=dp(40),
                halign='left'
            )
            self.roadmaps_layout.add_widget(no_paths)
            return
        
        # Update progress visualization if user has progress
        from recommender.models import UserSkillProgress
        user_progress = UserSkillProgress.objects.filter(user_profile=user)
        if user_progress.exists():
            path = user_progress.first().skill_path
            summary = services.compute_progress_summary(user, path)
            self.progress_bar.value = summary['percent']
            self.progress_label.text = f"{summary['percent']}%"
        else:
            self.progress_bar.value = 0
            self.progress_label.text = "0%"
        
        for label, path in paths.items():
            path_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(250))
            path_title = Label(
                text=f'{path.name} ({label})',
                size_hint_y=None,
                height=dp(40),
                font_size=dp(16),
                bold=True,
                halign='left'
            )
            path_title.bind(size=path_title.setter('text_size'))
            path_layout.add_widget(path_title)
            
            if path.description:
                path_desc = Label(
                    text=path.description,
                    size_hint_y=None,
                    height=dp(40),
                    halign='left',
                    valign='top'
                )
                path_desc.bind(size=path_desc.setter('text_size'))
                path_layout.add_widget(path_desc)
            
            # Steps
            steps_scroll = ScrollView(size_hint_y=None, height=dp(150))
            steps_layout = GridLayout(cols=4, spacing=5, size_hint_y=None)
            steps_layout.bind(minimum_height=steps_layout.setter('height'))
            
            # Headers
            headers = ["Skill step", "Level", "Difficulty", "Time"]
            for header in headers:
                header_label = Label(
                    text=header,
                    size_hint_y=None,
                    height=dp(30),
                    bold=True,
                    halign='left'
                )
                header_label.bind(size=header_label.setter('text_size'))
                steps_layout.add_widget(header_label)
            
            # Steps data
            for step in path.steps.all():
                level_text = dict(step.LEVEL_CHOICES).get(step.level, step.level)
                
                skill_label = Label(
                    text=step.skill.name,
                    size_hint_y=None,
                    height=dp(30),
                    halign='left'
                )
                skill_label.bind(size=skill_label.setter('text_size'))
                steps_layout.add_widget(skill_label)
                
                level_label = Label(
                    text=str(level_text),
                    size_hint_y=None,
                    height=dp(30),
                    halign='left'
                )
                steps_layout.add_widget(level_label)
                
                diff_label = Label(
                    text=step.difficulty.label,
                    size_hint_y=None,
                    height=dp(30),
                    halign='left'
                )
                steps_layout.add_widget(diff_label)
                
                time_label = Label(
                    text=f"{step.estimated_weeks} weeks",
                    size_hint_y=None,
                    height=dp(30),
                    halign='left'
                )
                steps_layout.add_widget(time_label)
            
            steps_scroll.add_widget(steps_layout)
            path_layout.add_widget(steps_scroll)
            self.roadmaps_layout.add_widget(path_layout)
    
    def back_clicked(self, instance):
        self.manager.current = 'results'
    
    def progress_clicked(self, instance):
        self.manager.current = 'progress_tracking'


class LearningResourcesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(
            text='Learning Resources',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(20),
            bold=True
        )
        self.layout.add_widget(title)
        
        desc = Label(
            text='Recommended YouTube videos and learning materials based on your profile',
            size_hint_y=None,
            height=dp(40),
            halign='left'
        )
        desc.bind(size=desc.setter('text_size'))
        self.layout.add_widget(desc)
        
        # Resources area
        self.resources_scroll = ScrollView()
        self.resources_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.resources_layout.bind(minimum_height=self.resources_layout.setter('height'))
        self.resources_scroll.add_widget(self.resources_layout)
        self.layout.add_widget(self.resources_scroll)
        
        # Navigation
        nav_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=10)
        back_btn = Button(text='Back')
        back_btn.bind(on_press=self.back_clicked)
        nav_layout.add_widget(back_btn)
        
        refresh_btn = Button(text='Refresh')
        refresh_btn.bind(on_press=self.refresh_clicked)
        nav_layout.add_widget(refresh_btn)
        
        self.layout.add_widget(nav_layout)
        self.add_widget(self.layout)
    
    def on_enter(self):
        self.load_resources()
    
    def load_resources(self):
        self.resources_layout.clear_widgets()
        
        user = self.manager.current_user
        stage = self.manager.current_stage
        if not user:
            return
        
        # Get personalized learning resources
        stream = None
        if hasattr(self.manager, 'stream_recommendations') and self.manager.stream_recommendations:
            best = self.manager.stream_recommendations.get("Plan A")
            if best:
                stream = best["stream"]
        
        resources = services.get_personalized_youtube_recommendations(user, stage, stream)
        
        if not resources:
            no_resources = Label(
                text='No learning resources found. Check back later for updates.',
                size_hint_y=None,
                height=dp(40),
                halign='left'
            )
            self.resources_layout.add_widget(no_resources)
            return
        
        for resource in resources:
            resource_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120))
            
            title_label = Label(
                text=resource.title,
                size_hint_y=None,
                height=dp(40),
                font_size=dp(14),
                bold=True,
                halign='left'
            )
            title_label.bind(size=title_label.setter('text_size'))
            resource_layout.add_widget(title_label)
            
            desc_label = Label(
                text=resource.description or "No description available",
                size_hint_y=None,
                height=dp(40),
                halign='left',
                valign='top'
            )
            desc_label.bind(size=desc_label.setter('text_size'))
            resource_layout.add_widget(desc_label)
            
            # Duration and action button
            bottom_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=10)
            
            duration_label = Label(
                text=f"Duration: {resource.duration_minutes or '?'} mins",
                size_hint_x=None,
                width=dp(120),
                halign='left'
            )
            bottom_layout.add_widget(duration_label)
            
            watch_btn = Button(
                text='Watch on YouTube',
                size_hint_x=None,
                width=dp(150)
            )
            watch_btn.bind(on_press=lambda x, url=resource.url: webbrowser.open(url))
            bottom_layout.add_widget(watch_btn)
            
            resource_layout.add_widget(bottom_layout)
            self.resources_layout.add_widget(resource_layout)
    
    def back_clicked(self, instance):
        self.manager.current = 'results'
    
    def refresh_clicked(self, instance):
        self.load_resources()


class ProfessionalDevelopmentScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(
            text='Professional Development Plan',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(22),
            bold=True,
            color=(0.2, 0.6, 0.8, 1)  # Blue color
        )
        self.layout.add_widget(title)
        
        desc = Label(
            text='Your personalized career transition roadmap and learning plan',
            size_hint_y=None,
            height=dp(40),
            halign='left',
            font_size=dp(14)
        )
        desc.bind(size=desc.setter('text_size'))
        self.layout.add_widget(desc)
        
        # Development plan area
        self.plan_scroll = ScrollView()
        self.plan_layout = GridLayout(cols=1, spacing=15, size_hint_y=None)
        self.plan_layout.bind(minimum_height=self.plan_layout.setter('height'))
        self.plan_scroll.add_widget(self.plan_layout)
        self.layout.add_widget(self.plan_scroll)
        
        # Navigation
        nav_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=10)
        back_btn = Button(text='Back', background_color=(0.7, 0.7, 0.7, 1))
        back_btn.bind(on_press=self.back_clicked)
        nav_layout.add_widget(back_btn)
        
        refresh_btn = Button(text='Refresh Plan', background_color=(0.3, 0.5, 0.8, 1))
        refresh_btn.bind(on_press=self.refresh_clicked)
        nav_layout.add_widget(refresh_btn)
        
        self.layout.add_widget(nav_layout)
        self.add_widget(self.layout)
    
    def on_enter(self):
        self.load_plan()
    
    def load_plan(self):
        self.plan_layout.clear_widgets()
        
        user = self.manager.current_user
        if not user:
            return
        
        # Get personalized development plan
        plan_items = services.generate_professional_development_plan(user)
        
        if not plan_items:
            no_plan = Label(
                text='No development plan available. Complete more assessments to generate personalized recommendations.',
                size_hint_y=None,
                height=dp(60),
                halign='left',
                valign='middle'
            )
            no_plan.bind(size=no_plan.setter('text_size'))
            self.plan_layout.add_widget(no_plan)
            return
        
        for item in plan_items:
            item_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100), padding=10)
            
            title_label = Label(
                text=item['title'],
                size_hint_y=None,
                height=dp(30),
                font_size=dp(16),
                bold=True,
                halign='left'
            )
            title_label.bind(size=title_label.setter('text_size'))
            item_layout.add_widget(title_label)
            
            desc_label = Label(
                text=item['description'],
                size_hint_y=None,
                height=dp(40),
                halign='left',
                valign='top'
            )
            desc_label.bind(size=desc_label.setter('text_size'))
            item_layout.add_widget(desc_label)
            
            timeline_label = Label(
                text=f"Timeline: {item['timeline']}",
                size_hint_y=None,
                height=dp(20),
                halign='left',
                font_size=dp(12),
                color=(0.4, 0.4, 0.4, 1)
            )
            item_layout.add_widget(timeline_label)
            
            self.plan_layout.add_widget(item_layout)
    
    def back_clicked(self, instance):
        self.manager.current = 'skill_roadmap'
    
    def refresh_clicked(self, instance):
        self.load_plan()


class ProgressTrackingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(
            text='Progress Tracking',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(22),
            bold=True,
            color=(0.2, 0.6, 0.8, 1)  # Blue color
        )
        self.layout.add_widget(title)
        
        desc = Label(
            text='Track your skill development progress',
            size_hint_y=None,
            height=dp(40),
            halign='left',
            font_size=dp(14)
        )
        desc.bind(size=desc.setter('text_size'))
        self.layout.add_widget(desc)
        
        # Progress visualization area
        self.progress_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120), spacing=10)
        
        # Progress bar
        from kivy.uix.progressbar import ProgressBar
        self.progress_bar = ProgressBar(max=100, size_hint_y=None, height=dp(30))
        self.progress_layout.add_widget(self.progress_bar)
        
        self.progress_text = Label(
            text='0% completed',
            size_hint_y=None,
            height=dp(30),
            halign='center',
            font_size=dp(16),
            bold=True
        )
        self.progress_layout.add_widget(self.progress_text)
        
        # Difficulty distribution
        self.difficulty_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=10)
        
        self.easy_label = Label(
            text='Easy: 0',
            size_hint_x=0.33,
            color=(0.29, 0.84, 0.35, 1)  # Green
        )
        self.difficulty_layout.add_widget(self.easy_label)
        
        self.medium_label = Label(
            text='Medium: 0',
            size_hint_x=0.33,
            color=(0.98, 0.75, 0.18, 1)  # Yellow
        )
        self.difficulty_layout.add_widget(self.medium_label)
        
        self.hard_label = Label(
            text='Hard: 0',
            size_hint_x=0.33,
            color=(0.97, 0.44, 0.44, 1)  # Red
        )
        self.difficulty_layout.add_widget(self.hard_label)
        
        self.progress_layout.add_widget(self.difficulty_layout)
        self.layout.add_widget(self.progress_layout)
        
        # Progress steps area
        self.steps_scroll = ScrollView()
        self.steps_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.steps_layout.bind(minimum_height=self.steps_layout.setter('height'))
        self.steps_scroll.add_widget(self.steps_layout)
        self.layout.add_widget(self.steps_scroll)
        
        # Navigation
        nav_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=10)
        back_btn = Button(text='Back', background_color=(0.7, 0.7, 0.7, 1))
        back_btn.bind(on_press=self.back_clicked)
        nav_layout.add_widget(back_btn)
        
        dashboard_btn = Button(text='Dashboard', background_color=(0.2, 0.7, 0.3, 1))
        dashboard_btn.bind(on_press=self.dashboard_clicked)
        nav_layout.add_widget(dashboard_btn)
        
        refresh_btn = Button(text='Refresh', background_color=(0.3, 0.5, 0.8, 1))
        refresh_btn.bind(on_press=self.refresh_clicked)
        nav_layout.add_widget(refresh_btn)
        
        self.layout.add_widget(nav_layout)
        self.add_widget(self.layout)
    
    def on_enter(self):
        self.load_progress()
    
    def load_progress(self):
        self.steps_layout.clear_widgets()
        
        user = self.manager.current_user
        if not user:
            return
        
        # Get user progress
        from recommender.models import UserSkillProgress
        user_progress = UserSkillProgress.objects.filter(user_profile=user).select_related("step__skill", "skill_path")
        
        if not user_progress.exists():
            no_progress = Label(
                text='No progress tracked yet. Start a skill path to begin tracking.',
                size_hint_y=None,
                height=dp(40),
                halign='left',
                color=(0.7, 0.7, 0.7, 1)
            )
            self.steps_layout.add_widget(no_progress)
            self.progress_bar.value = 0
            self.progress_text.text = '0% completed'
            self.easy_label.text = 'Easy: 0'
            self.medium_label.text = 'Medium: 0'
            self.hard_label.text = 'Hard: 0'
            return
        
        # Calculate summary
        path = user_progress.first().skill_path
        summary = services.compute_progress_summary(user, path)
        
        # Update progress visualization
        self.progress_bar.value = summary['percent']
        self.progress_text.text = f"{summary['percent']}% completed"
        
        # Parse difficulty text
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
        
        self.easy_label.text = f"Easy: {easy_count}"
        self.medium_label.text = f"Medium: {medium_count}"
        self.hard_label.text = f"Hard: {hard_count}"
        
        # Update milestone information
        milestones_text = f"Milestones: {summary.get('milestones_achieved', 0)}"
        streak_text = f"Streak: {summary.get('streak', 0)} days"
        
        # Add milestone info to the progress text
        self.progress_text.text = f"{summary['percent']}% completed | {milestones_text} | {streak_text}"
        
        # Get user's earned milestones
        user_milestones = services.get_user_milestones(user)
        
        # Display earned milestones if any
        if user_milestones:
            milestone_text = "\nEarned Badges: "
            for milestone in user_milestones[:3]:  # Show only first 3
                badge_symbols = {"BRONZE": "[color=#cd7f32]🥉[/color]", "SILVER": "[color=#c0c0c0]🥈[/color]", "GOLD": "[color=#ffd700]🥇[/color]"}
                symbol = badge_symbols.get(milestone['badge_type'], "🏆")
                milestone_text += f"{symbol} {milestone['name']}  "
            
            # Add to progress text
            self.progress_text.text += milestone_text
        
        # Display steps
        for progress in user_progress:
            step_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=10)
            
            # Skill name
            skill_label = Label(
                text=progress.step.skill.name,
                size_hint_x=0.6,
                halign='left'
            )
            step_layout.add_widget(skill_label)
            
            # Status
            status_colors = {
                'NOT_STARTED': (0.7, 0.7, 0.7, 1),
                'IN_PROGRESS': (0.98, 0.75, 0.18, 1),
                'COMPLETED': (0.29, 0.84, 0.35, 1)
            }
            status_color = status_colors.get(progress.status, (0.7, 0.7, 0.7, 1))
            
            # Add milestone indicator to status if achieved
            status_text = progress.get_status_display()
            if progress.milestone_achieved:
                status_text += " 🏆"
            
            status_label = Label(
                text=status_text,
                size_hint_x=0.3,
                color=status_color
            )
            step_layout.add_widget(status_label)
            
            # Action button
            action_btn = Button(
                text='Update',
                size_hint_x=0.1,
                font_size=dp(12)
            )
            action_btn.bind(on_press=lambda x, p=progress: self.update_progress(p))
            step_layout.add_widget(action_btn)
            
            self.steps_layout.add_widget(step_layout)
    
    def update_progress(self, progress):
        # Create popup for status selection
        popup = Popup(
            title='Update Progress',
            size_hint=(0.8, 0.6)
        )
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        title_label = Label(
            text=f'Update status for: {progress.step.skill.name}',
            size_hint_y=None,
            height=dp(40),
            halign='left'
        )
        content.add_widget(title_label)
        
        # Status selection
        status_layout = BoxLayout(orientation='vertical', spacing=5)
        
        from recommender.models import UserSkillProgress
        statuses = [
            (UserSkillProgress.NOT_STARTED, 'Not Started'),
            (UserSkillProgress.IN_PROGRESS, 'In Progress'),
            (UserSkillProgress.COMPLETED, 'Completed')
        ]
        
        self.selected_status = progress.status
        
        for status_value, status_label in statuses:
            btn = Button(
                text=status_label,
                size_hint_y=None,
                height=dp(40)
            )
            if status_value == progress.status:
                btn.background_color = (0.2, 0.7, 0.3, 1)  # Highlight current status
            
            btn.bind(on_press=lambda x, s=status_value: setattr(self, 'selected_status', s))
            status_layout.add_widget(btn)
        
        content.add_widget(status_layout)
        
        # Action buttons
        button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=10)
        
        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=popup.dismiss)
        button_layout.add_widget(cancel_btn)
        
        save_btn = Button(text='Save', background_color=(0.2, 0.7, 0.3, 1))
        save_btn.bind(on_press=lambda x: self.save_progress(progress, popup))
        button_layout.add_widget(save_btn)
        
        content.add_widget(button_layout)
        
        popup.content = content
        popup.open()
    
    def save_progress(self, progress, popup):
        # Use the new service function to update progress
        from recommender import services
        services.update_skill_step_progress(
            user=progress.user_profile,
            step=progress.step,
            status=self.selected_status
        )
        popup.dismiss()
        self.load_progress()  # Refresh the display
    
    def back_clicked(self, instance):
        self.manager.current = 'skill_roadmap'
    
    def dashboard_clicked(self, instance):
        self.manager.current = 'dashboard'
    
    def refresh_clicked(self, instance):
        self.load_progress()


class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(
            text='Learning Dashboard',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(22),
            bold=True,
            color=(0.2, 0.6, 0.8, 1)  # Blue color
        )
        self.layout.add_widget(title)
        
        # Stats grid
        self.stats_grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        self.stats_grid.bind(minimum_height=self.stats_grid.setter('height'))
        self.layout.add_widget(self.stats_grid)
        
        # Charts area
        self.charts_scroll = ScrollView(size_hint_y=0.4)
        self.charts_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.charts_layout.bind(minimum_height=self.charts_layout.setter('height'))
        self.charts_scroll.add_widget(self.charts_layout)
        self.layout.add_widget(self.charts_scroll)
        
        # Activity area
        self.activity_scroll = ScrollView(size_hint_y=0.3)
        self.activity_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.activity_layout.bind(minimum_height=self.activity_layout.setter('height'))
        self.activity_scroll.add_widget(self.activity_layout)
        self.layout.add_widget(self.activity_scroll)
        
        # Navigation
        nav_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=10)
        back_btn = Button(text='Back', background_color=(0.7, 0.7, 0.7, 1))
        back_btn.bind(on_press=self.back_clicked)
        nav_layout.add_widget(back_btn)
        
        feedback_btn = Button(text='Feedback', background_color=(0.8, 0.6, 0.2, 1))
        feedback_btn.bind(on_press=self.feedback_clicked)
        nav_layout.add_widget(feedback_btn)
        
        accessibility_btn = Button(text='Accessibility', background_color=(0.2, 0.8, 0.6, 1))
        accessibility_btn.bind(on_press=self.accessibility_clicked)
        nav_layout.add_widget(accessibility_btn)
        
        refresh_btn = Button(text='Refresh', background_color=(0.3, 0.5, 0.8, 1))
        refresh_btn.bind(on_press=self.refresh_clicked)
        nav_layout.add_widget(refresh_btn)
        
        self.layout.add_widget(nav_layout)
        self.add_widget(self.layout)
    
    def on_enter(self):
        self.load_dashboard()
    
    def load_dashboard(self):
        # Clear previous content
        self.stats_grid.clear_widgets()
        self.charts_layout.clear_widgets()
        self.activity_layout.clear_widgets()
        
        user = self.manager.current_user
        if not user:
            return
            
        # Get user's progress data
        from recommender.models import UserSkillProgress
        from recommender import services
        
        # Get all user progress records
        user_progress = UserSkillProgress.objects.filter(user_profile=user)
        
        if not user_progress.exists():
            no_data = Label(
                text='No progress data available yet.',
                size_hint_y=None,
                height=dp(40),
                halign='left'
            )
            self.stats_grid.add_widget(no_data)
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
        
        # Display stats in cards
        stat_cards = [
            {"title": "Total Steps", "value": str(total_steps), "color": (0.38, 0.65, 0.98, 1)},  # Blue
            {"title": "Completed", "value": str(completed_steps), "color": (0.29, 0.84, 0.35, 1)},  # Green
            {"title": "In Progress", "value": str(in_progress_steps), "color": (0.98, 0.75, 0.18, 1)},  # Yellow
            {"title": "Completion Rate", "value": f"{completion_rate}%", "color": (0.65, 0.55, 0.98, 1)},  # Purple
            {"title": "Milestones", "value": str(milestones_count), "color": (0.97, 0.44, 0.44, 1)},  # Red
        ]
        
        for stat in stat_cards:
            card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80), padding=10)
            card.canvas.before.clear()
            
            # Create colored background
            from kivy.graphics import Color, Rectangle
            with card.canvas.before:
                Color(*stat["color"])
                Rectangle(pos=card.pos, size=card.size)
            card.bind(pos=lambda instance, value: self.update_canvas(instance), 
                     size=lambda instance, value: self.update_canvas(instance))
            
            title_label = Label(
                text=stat["title"],
                size_hint_y=None,
                height=dp(25),
                font_size=dp(12),
                color=(1, 1, 1, 1),  # White text
                bold=True
            )
            card.add_widget(title_label)
            
            value_label = Label(
                text=stat["value"],
                size_hint_y=None,
                height=dp(35),
                font_size=dp(20),
                color=(1, 1, 1, 1),  # White text
                bold=True
            )
            card.add_widget(value_label)
            
            self.stats_grid.add_widget(card)
        
        # Charts section
        charts_title = Label(
            text='Progress Visualization',
            size_hint_y=None,
            height=dp(35),
            font_size=dp(16),
            bold=True,
            halign='left'
        )
        self.charts_layout.add_widget(charts_title)
        
        # Simple text-based chart for difficulty distribution
        difficulty_chart = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120))
        
        difficulty_title = Label(
            text='Difficulty Distribution:',
            size_hint_y=None,
            height=dp(25),
            font_size=dp(14),
            bold=True,
            halign='left'
        )
        difficulty_chart.add_widget(difficulty_title)
        
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
        
        chart_label = Label(
            text=chart_text,
            size_hint_y=None,
            height=dp(80),
            font_name='RobotoMono',
            font_size=dp(12),
            halign='left',
            valign='top'
        )
        chart_label.bind(size=chart_label.setter('text_size'))
        difficulty_chart.add_widget(chart_label)
        
        self.charts_layout.add_widget(difficulty_chart)
        
        # Activity section
        activity_title = Label(
            text='Recent Achievements',
            size_hint_y=None,
            height=dp(35),
            font_size=dp(16),
            bold=True,
            halign='left'
        )
        self.activity_layout.add_widget(activity_title)
        
        if user_milestones:
            for milestone in user_milestones[:5]:  # Show only first 5
                badge_symbols = {"BRONZE": "[color=#cd7f32]🥉[/color]", "SILVER": "[color=#c0c0c0]🥈[/color]", "GOLD": "[color=#ffd700]🥇[/color]"}
                symbol = badge_symbols.get(milestone['badge_type'], "🏆")
                
                activity_item = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), padding=5)
                
                badge_label = Label(
                    text=symbol,
                    size_hint_x=0.1,
                    markup=True
                )
                activity_item.add_widget(badge_label)
                
                text_label = Label(
                    text=f"{milestone['name']} - Achieved on {milestone['achieved_at']}",
                    size_hint_x=0.9,
                    halign='left'
                )
                text_label.bind(size=text_label.setter('text_size'))
                activity_item.add_widget(text_label)
                
                self.activity_layout.add_widget(activity_item)
        else:
            no_achievements = Label(
                text='No achievements yet. Keep learning!',
                size_hint_y=None,
                height=dp(40),
                halign='left'
            )
            self.activity_layout.add_widget(no_achievements)
    
    def update_canvas(self, instance):
        instance.canvas.before.clear()
        from kivy.graphics import Color, Rectangle
        with instance.canvas.before:
            Color(0.38, 0.65, 0.98, 1)  # Blue color as default
            Rectangle(pos=instance.pos, size=instance.size)
    
    def back_clicked(self, instance):
        self.manager.current = 'progress_tracking'
    
    def feedback_clicked(self, instance):
        self.manager.current = 'feedback'
    
    def accessibility_clicked(self, instance):
        self.manager.current = 'accessibility'
    
    def refresh_clicked(self, instance):
        self.load_dashboard()


class FeedbackScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(
            text='Share Your Feedback',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(22),
            bold=True,
            color=(0.2, 0.6, 0.8, 1)  # Blue color
        )
        self.layout.add_widget(title)
        
        desc = Label(
            text='Help us improve your experience by sharing your feedback. Your input is valuable to us!',
            size_hint_y=None,
            height=dp(40),
            halign='left',
            font_size=dp(14)
        )
        desc.bind(size=desc.setter('text_size'))
        self.layout.add_widget(desc)
        
        # Feedback type
        type_label = Label(
            text='Feedback Type:',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(16),
            bold=True,
            halign='left'
        )
        self.layout.add_widget(type_label)
        
        self.feedback_type_spinner = Spinner(
            text='General Feedback',
            values=['General Feedback', 'Recommendation Quality', 'User Interface', 'Feature Request', 'Bug Report'],
            size_hint_y=None,
            height=dp(40)
        )
        self.layout.add_widget(self.feedback_type_spinner)
        
        # Rating
        rating_label = Label(
            text='\nRating (1-5 stars):',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(16),
            bold=True,
            halign='left'
        )
        self.layout.add_widget(rating_label)
        
        self.rating_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=5)
        self.star_buttons = []
        self.rating = 0
        
        for i in range(1, 6):
            star_btn = Button(
                text='☆',
                font_size=dp(24),
                size_hint_x=None,
                width=dp(40),
                background_color=(1, 1, 1, 1)
            )
            star_btn.bind(on_press=lambda x, rating=i: self.set_rating(rating))
            self.star_buttons.append(star_btn)
            self.rating_layout.add_widget(star_btn)
        
        self.layout.add_widget(self.rating_layout)
        
        # Comment
        comment_label = Label(
            text='\nComments:',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(16),
            bold=True,
            halign='left'
        )
        self.layout.add_widget(comment_label)
        
        self.comment_input = TextInput(
            multiline=True,
            size_hint_y=None,
            height=dp(100)
        )
        self.layout.add_widget(self.comment_input)
        
        # Suggestions
        suggestion_label = Label(
            text='\nSuggestions for Improvement:',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(16),
            bold=True,
            halign='left'
        )
        self.layout.add_widget(suggestion_label)
        
        self.suggestion_input = TextInput(
            multiline=True,
            size_hint_y=None,
            height=dp(100)
        )
        self.layout.add_widget(self.suggestion_input)
        
        # Success message
        self.success_label = Label(
            text='',
            size_hint_y=None,
            height=dp(30),
            color=(0.2, 0.7, 0.3, 1),  # Green
            halign='center'
        )
        self.layout.add_widget(self.success_label)
        
        # Navigation
        nav_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=10)
        back_btn = Button(text='Back', background_color=(0.7, 0.7, 0.7, 1))
        back_btn.bind(on_press=self.back_clicked)
        nav_layout.add_widget(back_btn)
        
        submit_btn = Button(text='Submit Feedback', background_color=(0.2, 0.7, 0.3, 1))
        submit_btn.bind(on_press=self.submit_feedback)
        nav_layout.add_widget(submit_btn)
        
        self.layout.add_widget(nav_layout)
        self.add_widget(self.layout)
    
    def set_rating(self, rating):
        """Set the rating and update star display."""
        self.rating = rating
        for i, btn in enumerate(self.star_buttons):
            if i < rating:
                btn.text = '★'
                btn.color = (1, 0.8, 0, 1)  # Gold color
            else:
                btn.text = '☆'
                btn.color = (0, 0, 0, 1)  # Black color
    
    def submit_feedback(self, instance):
        """Submit the feedback to the database."""
        # Map spinner text to feedback type codes
        feedback_type_map = {
            'General Feedback': 'GENERAL',
            'Recommendation Quality': 'RECOMMENDATION',
            'User Interface': 'UI_EXPERIENCE',
            'Feature Request': 'FEATURE_REQUEST',
            'Bug Report': 'BUG_REPORT'
        }
        
        feedback_type = feedback_type_map.get(self.feedback_type_spinner.text, 'GENERAL')
        rating = self.rating if self.rating > 0 else None
        comment = self.comment_input.text.strip()
        suggestion = self.suggestion_input.text.strip()
        
        try:
            services.submit_user_feedback(
                user_profile=self.manager.current_user,
                feedback_type=feedback_type,
                rating=rating,
                comment=comment,
                suggestion=suggestion
            )
            
            # Show success message
            self.success_label.text = 'Thank you for your feedback! We appreciate your input.'
            
            # Clear form
            self.feedback_type_spinner.text = 'General Feedback'
            self.rating = 0
            for btn in self.star_buttons:
                btn.text = '☆'
                btn.color = (0, 0, 0, 1)  # Black color
            self.comment_input.text = ''
            self.suggestion_input.text = ''
            
            # Clear success message after 3 seconds
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: setattr(self.success_label, 'text', ''), 3)
            
        except Exception as e:
            from kivy.uix.popup import Popup
            popup = Popup(
                title='Error',
                content=Label(text=f'Failed to submit feedback: {str(e)}'),
                size_hint=(0.8, 0.4)
            )
            popup.open()
    
    def back_clicked(self, instance):
        self.manager.current = 'dashboard'


class AccessibilitySettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(
            text='Accessibility Settings',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(22),
            bold=True,
            color=(0.2, 0.6, 0.8, 1)  # Blue color
        )
        self.layout.add_widget(title)
        
        desc = Label(
            text='Customize your experience for better accessibility.',
            size_hint_y=None,
            height=dp(40),
            halign='left',
            font_size=dp(14)
        )
        desc.bind(size=desc.setter('text_size'))
        self.layout.add_widget(desc)
        
        # Text-to-Speech Settings
        tts_label = Label(
            text='Text-to-Speech Settings:',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(16),
            bold=True,
            halign='left'
        )
        self.layout.add_widget(tts_label)
        
        # Speech Rate
        rate_label = Label(
            text='Speech Rate:',
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        self.layout.add_widget(rate_label)
        
        self.rate_slider = Slider(min=50, max=300, value=150)
        self.layout.add_widget(self.rate_slider)
        
        self.rate_value = Label(
            text='150',
            size_hint_y=None,
            height=dp(30),
            halign='center'
        )
        self.layout.add_widget(self.rate_value)
        self.rate_slider.bind(value=self.on_rate_change)
        
        # Speech Volume
        volume_label = Label(
            text='Volume:',
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        self.layout.add_widget(volume_label)
        
        self.volume_slider = Slider(min=0.0, max=1.0, value=0.9)
        self.layout.add_widget(self.volume_slider)
        
        self.volume_value = Label(
            text='90%',
            size_hint_y=None,
            height=dp(30),
            halign='center'
        )
        self.layout.add_widget(self.volume_value)
        self.volume_slider.bind(value=self.on_volume_change)
        
        # Test Button
        test_btn = Button(
            text='Test Speech',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.7, 0.3, 1)
        )
        test_btn.bind(on_press=self.test_speech)
        self.layout.add_widget(test_btn)
        
        # Status message
        self.status_label = Label(
            text='',
            size_hint_y=None,
            height=dp(30),
            color=(0.2, 0.7, 0.3, 1),  # Green
            halign='center'
        )
        self.layout.add_widget(self.status_label)
        
        # Navigation
        nav_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=10)
        back_btn = Button(text='Back', background_color=(0.7, 0.7, 0.7, 1))
        back_btn.bind(on_press=self.back_clicked)
        nav_layout.add_widget(back_btn)
        
        apply_btn = Button(text='Apply Settings', background_color=(0.2, 0.5, 0.8, 1))
        apply_btn.bind(on_press=self.apply_settings)
        nav_layout.add_widget(apply_btn)
        
        reset_btn = Button(text='Reset to Defaults', background_color=(0.8, 0.5, 0.2, 1))
        reset_btn.bind(on_press=self.reset_defaults)
        nav_layout.add_widget(reset_btn)
        
        self.layout.add_widget(nav_layout)
        self.add_widget(self.layout)
    
    def on_rate_change(self, instance, value):
        """Update rate value display when slider changes."""
        self.rate_value.text = str(int(value))
    
    def on_volume_change(self, instance, value):
        """Update volume value display when slider changes."""
        self.volume_value.text = f'{int(value*100)}%'
    
    def test_speech(self, instance):
        """Test the current speech settings."""
        # In a real implementation, this would test TTS settings
        self.status_label.text = 'Testing speech settings...'
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'Test completed!'), 2)
    
    def apply_settings(self, instance):
        """Apply the selected accessibility settings."""
        # In a real implementation, this would apply TTS settings
        self.status_label.text = 'Settings applied successfully!'
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', ''), 3)
    
    def reset_defaults(self, instance):
        """Reset settings to defaults."""
        self.rate_slider.value = 150
        self.volume_slider.value = 0.9
        self.status_label.text = 'Defaults restored. Click Apply to save.'
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', ''), 3)
    
    def back_clicked(self, instance):
        self.manager.current = 'dashboard'


class EduSkillRecommenderApp(App):
    def build(self):
        sm = ScreenManager()
        
        # Add all screens
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(StageSelectionScreen(name='stage_selection'))
        sm.add_widget(QuestionnaireScreen(name='questionnaire'))
        sm.add_widget(SubjectStrengthScreen(name='subject_strength'))
        sm.add_widget(ResultsScreen(name='results'))
        sm.add_widget(SkillRoadmapScreen(name='skill_roadmap'))
        sm.add_widget(LearningResourcesScreen(name='learning_resources'))
        sm.add_widget(ProfessionalDevelopmentScreen(name='professional_development'))
        sm.add_widget(ProgressTrackingScreen(name='progress_tracking'))
        sm.add_widget(DashboardScreen(name='dashboard'))  # New dashboard screen
        sm.add_widget(FeedbackScreen(name='feedback'))  # New feedback screen
        sm.add_widget(AccessibilitySettingsScreen(name='accessibility'))  # New accessibility settings screen
        
        # Initialize manager attributes
        sm.current_user = None
        sm.current_stage = None
        sm.interest_answers = []
        sm.subject_levels = {}
        sm.stream_recommendations = {}
        
        sm.current = 'home'
        return sm


if __name__ == '__main__':
    EduSkillRecommenderApp().run()