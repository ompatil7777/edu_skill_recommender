import json
from django.core.management.base import BaseCommand
from recommender.models import (
    ActivitySuggestion,
    Career,
    EducationStage,
    LearningResource,
    MotivationTip,
    Question,
    OptionScore,
    Skill,
    SkillDifficulty,
    SkillPath,
    SkillPathStep,
    Stream,
)


class Command(BaseCommand):
    help = "Import comprehensive data for the Edu & Skill Path Recommender"

    def handle(self, *args, **options):
        self.stdout.write("Importing comprehensive data...")
        
        # Get existing stages
        stages = {}
        for code in [
            EducationStage.PRIMARY, EducationStage.MIDDLE, EducationStage.HIGH_SCHOOL,
            EducationStage.HIGHER_SECONDARY, EducationStage.UG, EducationStage.PG,
            EducationStage.PROFESSIONAL, EducationStage.COUNSELOR
        ]:
            try:
                stages[code] = EducationStage.objects.get(code=code)
            except EducationStage.DoesNotExist:
                self.stdout.write(f"Warning: Stage {code} not found")
        
        # Get existing streams
        streams = {}
        for code in [Stream.SCIENCE, Stream.COMMERCE, Stream.ARTS, Stream.VOCATIONAL]:
            try:
                streams[code] = Stream.objects.get(code=code)
            except Stream.DoesNotExist:
                self.stdout.write(f"Warning: Stream {code} not found")
        
        # Get or create skill difficulties
        easy, _ = SkillDifficulty.objects.get_or_create(code=SkillDifficulty.EASY, defaults={"label": "Easy"})
        medium, _ = SkillDifficulty.objects.get_or_create(code=SkillDifficulty.MEDIUM, defaults={"label": "Medium"})
        hard, _ = SkillDifficulty.objects.get_or_create(code=SkillDifficulty.HARD, defaults={"label": "Hard"})
        
        # Create comprehensive learning resources
        self.create_comprehensive_learning_resources(stages, streams, easy, medium, hard)
        
        # Create additional questions for better profiling
        self.create_additional_questions(stages)
        
        # Create more career paths
        self.create_additional_careers(streams)
        
        # Create more activity suggestions
        self.create_additional_activities(stages)
        
        # Create more motivation tips
        self.create_additional_motivation_tips(stages)
        
        # Create more skill paths
        self.create_additional_skill_paths(stages, streams, easy, medium, hard)
        
        self.stdout.write(self.style.SUCCESS("Comprehensive data import completed."))

    def create_comprehensive_learning_resources(self, stages, streams, easy, medium, hard):
        """Create a comprehensive set of learning resources."""
        
        # Extended list of YouTube resources for different streams and stages
        resources_data = [
            # Science stream resources
            {
                "title": "Advanced Physics Concepts Explained",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "description": "Deep dive into advanced physics concepts for higher secondary students",
                "resource_type": "VIDEO",
                "stage": stages.get(EducationStage.HIGHER_SECONDARY),
                "stream": streams.get(Stream.SCIENCE),
                "duration_minutes": 30,
                "difficulty": medium,
            },
            {
                "title": "Organic Chemistry Mastery",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "description": "Complete guide to organic chemistry for NEET/JEE aspirants",
                "resource_type": "VIDEO",
                "stage": stages.get(EducationStage.HIGHER_SECONDARY),
                "stream": streams.get(Stream.SCIENCE),
                "duration_minutes": 45,
                "difficulty": hard,
            },
            {
                "title": "Mathematical Olympiad Preparation",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "description": "Techniques and problems for mathematics olympiads",
                "resource_type": "VIDEO",
                "stage": stages.get(EducationStage.HIGH_SCHOOL),
                "stream": streams.get(Stream.SCIENCE),
                "duration_minutes": 35,
                "difficulty": hard,
            },
            
            # Commerce stream resources
            {
                "title": "Advanced Accountancy for CA Intermediate",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "description": "Detailed coverage of CA Intermediate accountancy topics",
                "resource_type": "VIDEO",
                "stage": stages.get(EducationStage.HIGHER_SECONDARY),
                "stream": streams.get(Stream.COMMERCE),
                "duration_minutes": 40,
                "difficulty": hard,
            },
            {
                "title": "Business Statistics Made Easy",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "description": "Understanding statistical concepts for business applications",
                "resource_type": "VIDEO",
                "stage": stages.get(EducationStage.HIGH_SCHOOL),
                "stream": streams.get(Stream.COMMERCE),
                "duration_minutes": 25,
                "difficulty": medium,
            },
            
            # Arts stream resources
            {
                "title": "World History: Ancient to Modern",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "description": "Comprehensive overview of world history from ancient civilizations to modern times",
                "resource_type": "VIDEO",
                "stage": stages.get(EducationStage.HIGHER_SECONDARY),
                "stream": streams.get(Stream.ARTS),
                "duration_minutes": 50,
                "difficulty": medium,
            },
            {
                "title": "Psychology: Understanding Human Behavior",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "description": "Introduction to psychological concepts and theories",
                "resource_type": "VIDEO",
                "stage": stages.get(EducationStage.HIGH_SCHOOL),
                "stream": streams.get(Stream.ARTS),
                "duration_minutes": 30,
                "difficulty": medium,
            },
            
            # Programming and technology resources
            {
                "title": "Java Programming Masterclass",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "description": "Complete Java programming course for beginners to advanced",
                "resource_type": "VIDEO",
                "stage": stages.get(EducationStage.UG),
                "duration_minutes": 420,
                "difficulty": hard,
            },
            {
                "title": "Machine Learning with Python",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "description": "Hands-on machine learning course using Python and scikit-learn",
                "resource_type": "VIDEO",
                "stage": stages.get(EducationStage.UG),
                "duration_minutes": 360,
                "difficulty": hard,
            },
            {
                "title": "Android App Development",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "description": "Build your first Android app with Kotlin",
                "resource_type": "VIDEO",
                "stage": stages.get(EducationStage.UG),
                "duration_minutes": 280,
                "difficulty": medium,
            },
            
            # Professional development resources
            {
                "title": "Project Management Fundamentals",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "description": "Learn essential project management skills for career advancement",
                "resource_type": "VIDEO",
                "stage": stages.get(EducationStage.PROFESSIONAL),
                "duration_minutes": 45,
                "difficulty": medium,
            },
            {
                "title": "Public Speaking and Presentation Skills",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "description": "Master the art of public speaking and effective presentations",
                "resource_type": "VIDEO",
                "stage": stages.get(EducationStage.PROFESSIONAL),
                "duration_minutes": 35,
                "difficulty": medium,
            },
            
            # General study skills and motivation
            {
                "title": "Memory Techniques for Better Learning",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "description": "Scientifically proven memory techniques to enhance learning",
                "resource_type": "VIDEO",
                "stage": stages.get(EducationStage.HIGH_SCHOOL),
                "duration_minutes": 20,
                "difficulty": easy,
            },
            {
                "title": "Mindfulness for Stress Management",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "description": "Practical mindfulness techniques for students and professionals",
                "resource_type": "VIDEO",
                "stage": stages.get(EducationStage.UG),
                "duration_minutes": 25,
                "difficulty": easy,
            },
        ]
        
        for resource_data in resources_data:
            LearningResource.objects.get_or_create(
                title=resource_data["title"],
                url=resource_data["url"],
                defaults=resource_data
            )

    def create_additional_questions(self, stages):
        """Create additional profiling questions for better recommendations."""
        
        # Additional questions for higher secondary students
        if stages.get(EducationStage.HIGHER_SECONDARY):
            # Question 1
            q1 = Question.objects.create(
                text="How do you approach complex problem-solving?",
                stage=stages[EducationStage.HIGHER_SECONDARY],
            )
            OptionScore.objects.create(
                question=q1,
                option_text="I enjoy breaking down complex problems into smaller parts",
                logical_score=3,
                analytical_score=3,
            )
            OptionScore.objects.create(
                question=q1,
                option_text="I prefer working with known formulas and methods",
                logical_score=2,
                analytical_score=1,
            )
            OptionScore.objects.create(
                question=q1,
                option_text="I find complex problems overwhelming",
                logical_score=0,
                analytical_score=0,
            )
            
            # Question 2
            q2 = Question.objects.create(
                text="What type of extracurricular activities interest you most?",
                stage=stages[EducationStage.HIGHER_SECONDARY],
            )
            OptionScore.objects.create(
                question=q2,
                option_text="Science clubs, math competitions, robotics",
                logical_score=3,
                scientific_score=3,
                practical_score=2,
            )
            OptionScore.objects.create(
                question=q2,
                option_text="Debate team, student government, Model UN",
                people_score=3,
                creative_score=2,
            )
            OptionScore.objects.create(
                question=q2,
                option_text="Art classes, music band, drama club",
                creative_score=3,
                design_score=2,
            )
            
            # Question 3
            q3 = Question.objects.create(
                text="How do you prefer to learn new concepts?",
                stage=stages[EducationStage.HIGHER_SECONDARY],
            )
            OptionScore.objects.create(
                question=q3,
                option_text="Through hands-on experiments and practical work",
                practical_score=3,
                scientific_score=2,
            )
            OptionScore.objects.create(
                question=q3,
                option_text="By reading textbooks and taking detailed notes",
                analytical_score=3,
                logical_score=2,
            )
            OptionScore.objects.create(
                question=q3,
                option_text="Through group discussions and collaborative learning",
                people_score=3,
                creative_score=2,
            )

    def create_additional_careers(self, streams):
        """Create additional career paths for different streams."""
        
        # Additional science careers
        if streams.get(Stream.SCIENCE):
            Career.objects.get_or_create(
                stream=streams[Stream.SCIENCE],
                name="Biotechnology Research Scientist",
                defaults={
                    "description": "Conduct research in biotechnology to develop new products and processes.",
                    "why_it_fits_template": "If you're fascinated by biology and want to contribute to scientific breakthroughs, biotechnology research is an excellent fit.",
                    "suggested_exams_text": "B.Sc in Biotechnology, followed by M.Sc and Ph.D.",
                },
            )
            Career.objects.get_or_create(
                stream=streams[Stream.SCIENCE],
                name="Aerospace Engineer",
                defaults={
                    "description": "Design and develop aircraft, spacecraft, satellites, and missiles.",
                    "why_it_fits_template": "If you're passionate about physics and mathematics with an interest in aviation and space, aerospace engineering is ideal.",
                    "suggested_exams_text": "B.Tech in Aerospace Engineering, Aeronautical Engineering, or Mechanical Engineering with specialization.",
                },
            )
        
        # Additional commerce careers
        if streams.get(Stream.COMMERCE):
            Career.objects.get_or_create(
                stream=streams[Stream.COMMERCE],
                name="Investment Banker",
                defaults={
                    "description": "Help clients raise capital and give advice on financial transactions.",
                    "why_it_fits_template": "If you have strong analytical skills and enjoy high-pressure environments with significant financial rewards, investment banking suits you.",
                    "suggested_exams_text": "Bachelor's in Commerce/Finance, MBA, and professional certifications like CFA.",
                },
            )
            Career.objects.get_or_create(
                stream=streams[Stream.COMMERCE],
                name="Financial Analyst",
                defaults={
                    "description": "Analyze financial data to help companies make business decisions.",
                    "why_it_fits_template": "If you enjoy working with numbers and have an analytical mind, financial analysis is a great career path.",
                    "suggested_exams_text": "Bachelor's in Commerce/Finance/Economics, followed by CFA or FRM certifications.",
                },
            )
        
        # Additional arts careers
        if streams.get(Stream.ARTS):
            Career.objects.get_or_create(
                stream=streams[Stream.ARTS],
                name="International Relations Specialist",
                defaults={
                    "description": "Work in diplomacy, international organizations, or policy research.",
                    "why_it_fits_template": "If you're interested in global affairs, politics, and cross-cultural communication, international relations is a perfect fit.",
                    "suggested_exams_text": "Bachelor's in Political Science/International Relations, followed by MA and possibly UPSC civil services.",
                },
            )
            Career.objects.get_or_create(
                stream=streams[Stream.ARTS],
                name="Content Strategist",
                defaults={
                    "description": "Plan and develop content for digital platforms and marketing campaigns.",
                    "why_it_fits_template": "If you have strong writing skills and understand digital media trends, content strategy combines creativity with business acumen.",
                    "suggested_exams_text": "Bachelor's in Mass Communication/Journalism/English, with digital marketing certifications.",
                },
            )

    def create_additional_activities(self, stages):
        """Create additional activity suggestions for different stages."""
        
        # Activities for primary students
        if stages.get(EducationStage.PRIMARY):
            ActivitySuggestion.objects.get_or_create(
                stage=stages[EducationStage.PRIMARY],
                title="Math Puzzle Club",
                defaults={
                    "description": "Weekly puzzle-solving sessions to develop logical thinking skills.",
                    "focus_area": "logical",
                },
            )
            ActivitySuggestion.objects.get_or_create(
                stage=stages[EducationStage.PRIMARY],
                title="Storytelling Circle",
                defaults={
                    "description": "Group storytelling sessions to enhance creativity and communication skills.",
                    "focus_area": "creative",
                },
            )
        
        # Activities for middle school students
        if stages.get(EducationStage.MIDDLE):
            ActivitySuggestion.objects.get_or_create(
                stage=stages[EducationStage.MIDDLE],
                title="Young Scientists Forum",
                defaults={
                    "description": "Monthly science discussion groups to explore scientific concepts beyond textbooks.",
                    "focus_area": "scientific",
                },
            )
            ActivitySuggestion.objects.get_or_create(
                stage=stages[EducationStage.MIDDLE],
                title="Creative Writing Workshop",
                defaults={
                    "description": "Regular creative writing sessions to develop writing and imagination skills.",
                    "focus_area": "creative",
                },
            )
        
        # Activities for high school students
        if stages.get(EducationStage.HIGH_SCHOOL):
            ActivitySuggestion.objects.get_or_create(
                stage=stages[EducationStage.HIGH_SCHOOL],
                title="Peer Tutoring Program",
                defaults={
                    "description": "Teach younger students to reinforce your own learning and develop leadership skills.",
                    "focus_area": "people",
                },
            )
            ActivitySuggestion.objects.get_or_create(
                stage=stages[EducationStage.HIGH_SCHOOL],
                title="Entrepreneurship Challenge",
                defaults={
                    "description": "Participate in business plan competitions to develop entrepreneurial thinking.",
                    "focus_area": "practical",
                },
            )

    def create_additional_motivation_tips(self, stages):
        """Create additional motivation tips for different audiences and stages."""
        
        # Tips for high school students
        if stages.get(EducationStage.HIGH_SCHOOL):
            MotivationTip.objects.get_or_create(
                audience=MotivationTip.AUDIENCE_SCHOOL,
                stage=stages[EducationStage.HIGH_SCHOOL],
                text="Focus on understanding concepts rather than memorizing. This approach will serve you well in board exams and competitive exams.",
            )
            MotivationTip.objects.get_or_create(
                audience=MotivationTip.AUDIENCE_SCHOOL,
                stage=stages[EducationStage.HIGH_SCHOOL],
                text="Balance your study schedule with physical exercise and hobbies. A healthy mind performs better academically.",
            )
        
        # Tips for college students
        if stages.get(EducationStage.UG):
            MotivationTip.objects.get_or_create(
                audience=MotivationTip.AUDIENCE_UG_PG,
                stage=stages[EducationStage.UG],
                text="Internships and practical experience matter more than perfect grades. Seek opportunities to apply your knowledge in real-world settings.",
            )
            MotivationTip.objects.get_or_create(
                audience=MotivationTip.AUDIENCE_UG_PG,
                stage=stages[EducationStage.UG],
                text="Build a network of peers, professors, and industry professionals. Relationships often open doors that qualifications alone cannot.",
            )
        
        # Tips for professionals
        if stages.get(EducationStage.PROFESSIONAL):
            MotivationTip.objects.get_or_create(
                audience=MotivationTip.AUDIENCE_PROFESSIONAL,
                text="Continuous learning is essential in today's rapidly changing job market. Dedicate time weekly to acquire new skills.",
            )
            MotivationTip.objects.get_or_create(
                audience=MotivationTip.AUDIENCE_PROFESSIONAL,
                text="Document your achievements and skills regularly. This practice makes performance reviews and job searches much easier.",
            )

    def create_additional_skill_paths(self, stages, streams, easy, medium, hard):
        """Create additional skill paths for various career directions."""
        
        # Cybersecurity path
        cybersecurity_skill, _ = Skill.objects.get_or_create(name="Cybersecurity Fundamentals")
        ethical_hacking, _ = Skill.objects.get_or_create(name="Ethical Hacking")
        network_security, _ = Skill.objects.get_or_create(name="Network Security")
        incident_response, _ = Skill.objects.get_or_create(name="Incident Response")
        
        cybersecurity_path, _ = SkillPath.objects.get_or_create(
            name="Cybersecurity Specialist Path",
            defaults={
                "description": "From security basics to advanced threat detection and response.",
                "stage": stages.get(EducationStage.UG),
                "primary_stream": streams.get(Stream.SCIENCE),
            },
        )
        if not cybersecurity_path.steps.exists():
            SkillPathStep.objects.create(
                skill_path=cybersecurity_path,
                skill=cybersecurity_skill,
                order_index=1,
                difficulty=easy,
                level=1,
                estimated_weeks=3,
            )
            SkillPathStep.objects.create(
                skill_path=cybersecurity_path,
                skill=ethical_hacking,
                order_index=2,
                difficulty=medium,
                level=2,
                estimated_weeks=4,
            )
            SkillPathStep.objects.create(
                skill_path=cybersecurity_path,
                skill=network_security,
                order_index=3,
                difficulty=medium,
                level=3,
                estimated_weeks=4,
            )
            SkillPathStep.objects.create(
                skill_path=cybersecurity_path,
                skill=incident_response,
                order_index=4,
                difficulty=hard,
                level=4,
                estimated_weeks=5,
            )
        
        # UX/UI Design path
        design_fundamentals, _ = Skill.objects.get_or_create(name="Design Fundamentals")
        ui_design, _ = Skill.objects.get_or_create(name="UI Design Principles")
        ux_research, _ = Skill.objects.get_or_create(name="UX Research Methods")
        prototyping, _ = Skill.objects.get_or_create(name="Prototyping Tools")
        
        design_path, _ = SkillPath.objects.get_or_create(
            name="UX/UI Designer Path",
            defaults={
                "description": "From design basics to creating user-centered digital experiences.",
                "stage": stages.get(EducationStage.UG),
                "primary_stream": streams.get(Stream.ARTS),
            },
        )
        if not design_path.steps.exists():
            SkillPathStep.objects.create(
                skill_path=design_path,
                skill=design_fundamentals,
                order_index=1,
                difficulty=easy,
                level=1,
                estimated_weeks=3,
            )
            SkillPathStep.objects.create(
                skill_path=design_path,
                skill=ui_design,
                order_index=2,
                difficulty=medium,
                level=2,
                estimated_weeks=4,
            )
            SkillPathStep.objects.create(
                skill_path=design_path,
                skill=ux_research,
                order_index=3,
                difficulty=medium,
                level=3,
                estimated_weeks=4,
            )
            SkillPathStep.objects.create(
                skill_path=design_path,
                skill=prototyping,
                order_index=4,
                difficulty=hard,
                level=4,
                estimated_weeks=5,
            )