import os
import sys

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
    from kivy.metrics import dp
    from kivy.properties import ObjectProperty
except ImportError:
    print("Kivy is not installed. Please install it with 'pip install kivy' to use this interface.")
    sys.exit(1)

from recommender.models import EducationStage, Question, OptionScore, Stream, UserProfile
from recommender import services


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(
            text='Edu & Skill Path Recommender',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(24),
            bold=True
        )
        self.layout.add_widget(title)
        
        subtitle = Label(
            text='Who is using this tool today?',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(16)
        )
        self.layout.add_widget(subtitle)
        
        # Mode selection
        self.mode_buttons = {}
        modes = [
            ("Student (Class 1-12)", "STUDENT"),
            ("UG / PG Student", "UGPG"),
            ("Working Professional", "PROFESSIONAL"),
            ("Parent / Teacher / Counselor", "COUNSELOR"),
        ]
        
        self.mode_selection = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.mode_selection.bind(minimum_height=self.mode_selection.setter('height'))
        
        self.selected_mode = "STUDENT"
        for text, val in modes:
            btn_layout = BoxLayout(size_hint_y=None, height=dp(40))
            checkbox = CheckBox(group='mode', size_hint_x=None, width=dp(40))
            if val == "STUDENT":
                checkbox.active = True
            checkbox.bind(active=lambda instance, value, mode=val: self.on_mode_select(mode, value))
            
            label = Label(text=text, halign='left', valign='middle')
            label.bind(size=label.setter('text_size'))
            
            btn_layout.add_widget(checkbox)
            btn_layout.add_widget(label)
            self.mode_selection.add_widget(btn_layout)
        
        scroll = ScrollView(size_hint_y=0.4)
        scroll.add_widget(self.mode_selection)
        self.layout.add_widget(scroll)
        
        # Name input
        name_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        name_label = Label(
            text='Your name (for saving progress):',
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        name_label.bind(size=name_label.setter('text_size'))
        name_layout.add_widget(name_label)
        
        self.name_input = TextInput(multiline=False, size_hint_y=None, height=dp(40))
        name_layout.add_widget(self.name_input)
        self.layout.add_widget(name_layout)
        
        # Next button
        next_btn = Button(
            text='Next',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16)
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
            font_size=dp(20),
            bold=True
        )
        self.layout.add_widget(title)
        
        desc = Label(
            text='Answer a few simple questions about what you enjoy. This helps us suggest paths.',
            size_hint_y=None,
            height=dp(40),
            halign='left'
        )
        desc.bind(size=desc.setter('text_size'))
        self.layout.add_widget(desc)
        
        # Questions area
        self.questions_scroll = ScrollView()
        self.questions_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.questions_layout.bind(minimum_height=self.questions_layout.setter('height'))
        self.questions_scroll.add_widget(self.questions_layout)
        self.layout.add_widget(self.questions_scroll)
        
        # Navigation
        nav_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=10)
        back_btn = Button(text='Back')
        back_btn.bind(on_press=self.back_clicked)
        nav_layout.add_widget(back_btn)
        
        next_btn = Button(text='Next')
        next_btn.bind(on_press=self.next_clicked)
        nav_layout.add_widget(next_btn)
        
        self.layout.add_widget(nav_layout)
        self.add_widget(self.layout)
        
        self.option_vars = {}
    
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
            text='Recommendations',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(20),
            bold=True
        )
        self.layout.add_widget(title)
        
        # Results area
        self.results_scroll = ScrollView()
        self.results_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        self.results_scroll.add_widget(self.results_layout)
        self.layout.add_widget(self.results_scroll)
        
        # Navigation
        nav_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=10)
        back_btn = Button(text='Back')
        back_btn.bind(on_press=self.back_clicked)
        nav_layout.add_widget(back_btn)
        
        skill_btn = Button(text='Skill Roadmap')
        skill_btn.bind(on_press=self.skill_roadmap_clicked)
        nav_layout.add_widget(skill_btn)
        
        self.layout.add_widget(nav_layout)
        self.add_widget(self.layout)
    
    def on_enter(self):
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
        
        paths = services.get_skill_paths_for_target(stage, stream, getattr(user, "target_role", ""))
        if not paths:
            no_paths = Label(
                text='No skill paths defined yet. Admin can add them in Django admin.',
                size_hint_y=None,
                height=dp(40),
                halign='left'
            )
            self.roadmaps_layout.add_widget(no_paths)
            return
        
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