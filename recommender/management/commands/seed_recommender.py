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
    help = "Seed sample data for the Edu & Skill Path Recommender"

    def handle(self, *args, **options):
        self.stdout.write("Seeding data...")

        # Education stages
        stages = {}
        for code, name, min_c, max_c in [
            (EducationStage.PRIMARY, "Primary (1-5)", 1, 5),
            (EducationStage.MIDDLE, "Middle (6-8)", 6, 8),
            (EducationStage.HIGH_SCHOOL, "High School (9-10)", 9, 10),
            (EducationStage.HIGHER_SECONDARY, "Higher Secondary (11-12)", 11, 12),
            (EducationStage.UG, "Undergraduate", None, None),
            (EducationStage.PG, "Postgraduate", None, None),
            (EducationStage.PROFESSIONAL, "Working Professional", None, None),
            (EducationStage.COUNSELOR, "Parent / Teacher / Counselor", None, None),
        ]:
            stage, _ = EducationStage.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "min_class": min_c,
                    "max_class": max_c,
                    "description": name,
                },
            )
            stages[code] = stage

        # Streams
        science, _ = Stream.objects.get_or_create(
            code=Stream.SCIENCE,
            defaults={
                "name": "Science",
                "description": "Science stream with focus on Physics, Chemistry, Maths, Biology.",
                "pros": "Strong base for engineering, medicine, research.",
                "cons": "Can be concept-heavy and requires consistent effort.",
                "required_strengths": "Comfort with maths and science, logical thinking.",
                "key_subjects": "Physics, Chemistry, Maths, Biology, Computer Science",
                "early_preparation_ideas": "Participate in science fairs, solve maths puzzles, try basic coding.",
            },
        )
        commerce, _ = Stream.objects.get_or_create(
            code=Stream.COMMERCE,
            defaults={
                "name": "Commerce",
                "description": "Commerce with focus on business, accounts, and finance.",
                "pros": "Leads to CA, CS, MBA, finance, analytics.",
                "cons": "Requires comfort with numbers and regulations.",
                "required_strengths": "Numerical ability, logical thinking, communication.",
                "key_subjects": "Accounts, Business Studies, Economics, Maths, English",
                "early_preparation_ideas": "Track business news, manage mock budgets, learn basic Excel.",
            },
        )
        arts, _ = Stream.objects.get_or_create(
            code=Stream.ARTS,
            defaults={
                "name": "Arts / Humanities",
                "description": "Humanities stream with focus on language, social sciences, and arts.",
                "pros": "Good for law, journalism, psychology, civil services.",
                "cons": "Needs strong reading and writing habits.",
                "required_strengths": "Creativity, language, interest in society and people.",
                "key_subjects": "History, Political Science, Sociology, Psychology, Literature",
                "early_preparation_ideas": "Read widely, join debates, write blogs or short essays.",
            },
        )
        vocational, _ = Stream.objects.get_or_create(
            code=Stream.VOCATIONAL,
            defaults={
                "name": "Vocational / Skill-based",
                "description": "Hands-on skills like IT, electronics, design, hospitality.",
                "pros": "Early entry to job market with practical skills.",
                "cons": "May need later upskilling for higher roles.",
                "required_strengths": "Practical mindset, curiosity to build and fix things.",
                "key_subjects": "Domain-specific vocational subjects.",
                "early_preparation_ideas": "Join clubs (robotics, carpentry, coding), tinker with DIY kits.",
            },
        )

        # Careers
        Career.objects.get_or_create(
            stream=science,
            name="Engineering",
            defaults={
                "description": "Design and build solutions in software, civil, mechanical, etc.",
                "why_it_fits_template": "Because you like maths and problem solving, engineering can be a strong fit.",
                "suggested_exams_text": "JEE Main, JEE Advanced, state engineering exams (e.g., MHTCET).",
            },
        )
        Career.objects.get_or_create(
            stream=science,
            name="Medicine",
            defaults={
                "description": "Doctor, surgeon, or healthcare professional.",
                "why_it_fits_template": "If you like biology and helping people, medicine is a strong choice.",
                "suggested_exams_text": "NEET UG, state medical entrance exams.",
            },
        )
        Career.objects.get_or_create(
            stream=commerce,
            name="Chartered Accountant (CA)",
            defaults={
                "description": "Finance, taxation, and auditing expert.",
                "why_it_fits_template": "If you are comfortable with numbers and detail, CA can be ideal.",
                "suggested_exams_text": "CA Foundation, Intermediate, Final.",
            },
        )
        Career.objects.get_or_create(
            stream=commerce,
            name="Company Secretary (CS)",
            defaults={
                "description": "Corporate governance and compliance expert.",
                "why_it_fits_template": "If you have good communication skills and attention to detail, CS can be a good fit.",
                "suggested_exams_text": "CS Foundation, Executive, Professional.",
            },
        )
        Career.objects.get_or_create(
            stream=arts,
            name="Law",
            defaults={
                "description": "Legal practice and judiciary.",
                "why_it_fits_template": "Strong language skills, reading and logical reasoning suit law.",
                "suggested_exams_text": "CLAT and other law entrance exams.",
            },
        )
        Career.objects.get_or_create(
            stream=arts,
            name="Psychology",
            defaults={
                "description": "Understanding human behavior and mental processes.",
                "why_it_fits_template": "If you're interested in people and their behaviors, psychology can be fulfilling.",
                "suggested_exams_text": "Bachelor's in Psychology, followed by Master's and optionally PhD.",
            },
        )
        Career.objects.get_or_create(
            stream=arts,
            name="Mass Communication/Journalism",
            defaults={
                "description": "Media, journalism, and content creation.",
                "why_it_fits_template": "Strong communication skills and creativity make this field suitable.",
                "suggested_exams_text": "Entrance exams like JMI, IP University, etc.",
            },
        )
        Career.objects.get_or_create(
            stream=vocational,
            name="Web Developer",
            defaults={
                "description": "Create and maintain websites and web applications.",
                "why_it_fits_template": "If you enjoy technology and problem-solving, web development is a great choice.",
                "suggested_exams_text": "Bootcamps, online courses, or certifications.",
            },
        )
        Career.objects.get_or_create(
            stream=vocational,
            name="Digital Marketing Specialist",
            defaults={
                "description": "Promote brands and products through digital channels.",
                "why_it_fits_template": "If you understand social media and have creative skills, this field suits you.",
                "suggested_exams_text": "Certifications from Google, Facebook, or online platforms.",
            },
        )

        # Skill difficulties
        easy, _ = SkillDifficulty.objects.get_or_create(code=SkillDifficulty.EASY, defaults={"label": "Easy"})
        medium, _ = SkillDifficulty.objects.get_or_create(code=SkillDifficulty.MEDIUM, defaults={"label": "Medium"})
        hard, _ = SkillDifficulty.objects.get_or_create(code=SkillDifficulty.HARD, defaults={"label": "Hard"})

        # Create learning resources (YouTube videos, articles, etc.)
        self.create_learning_resources(stages, science, commerce, arts, vocational)

        # Skills and paths (example: Cloud Support Engineer)
        linux, _ = Skill.objects.get_or_create(name="Linux Basics")
        networking, _ = Skill.objects.get_or_create(name="Computer Networking")
        aws_core, _ = Skill.objects.get_or_create(name="AWS Core Services")
        iam, _ = Skill.objects.get_or_create(name="AWS IAM & Security")
        monitoring, _ = Skill.objects.get_or_create(name="Monitoring & Troubleshooting")
        scripting, _ = Skill.objects.get_or_create(name="Scripting (Python/Bash)")

        cloud_path, _ = SkillPath.objects.get_or_create(
            name="Cloud Support Engineer Path",
            defaults={
                "description": "Roadmap from basics of OS and networking to cloud support.",
                "stage": stages[EducationStage.PROFESSIONAL],
                "primary_stream": science,
            },
        )
        if not cloud_path.steps.exists():
            SkillPathStep.objects.create(
                skill_path=cloud_path,
                skill=linux,
                order_index=1,
                difficulty=easy,
                level=1,
                estimated_weeks=2,
            )
            SkillPathStep.objects.create(
                skill_path=cloud_path,
                skill=networking,
                order_index=2,
                difficulty=medium,
                level=2,
                estimated_weeks=3,
            )
            SkillPathStep.objects.create(
                skill_path=cloud_path,
                skill=aws_core,
                order_index=3,
                difficulty=medium,
                level=2,
                estimated_weeks=3,
            )
            SkillPathStep.objects.create(
                skill_path=cloud_path,
                skill=iam,
                order_index=4,
                difficulty=hard,
                level=3,
                estimated_weeks=3,
            )
            SkillPathStep.objects.create(
                skill_path=cloud_path,
                skill=monitoring,
                order_index=5,
                difficulty=medium,
                level=3,
                estimated_weeks=2,
            )
            SkillPathStep.objects.create(
                skill_path=cloud_path,
                skill=scripting,
                order_index=6,
                difficulty=medium,
                level=4,
                estimated_weeks=3,
            )

        # Simple full-stack Python dev path
        py_basics, _ = Skill.objects.get_or_create(name="Python Basics")
        py_oop, _ = Skill.objects.get_or_create(name="Python OOP")
        django, _ = Skill.objects.get_or_create(name="Django Fundamentals")
        sql_skill, _ = Skill.objects.get_or_create(name="SQL & Databases")
        deployment, _ = Skill.objects.get_or_create(name="Deployment & DevOps Basics")

        dev_path, _ = SkillPath.objects.get_or_create(
            name="Full-Stack Python Developer Path",
            defaults={
                "description": "From Python basics to deploying simple apps.",
                "stage": stages[EducationStage.UG],
                "primary_stream": science,
            },
        )
        if not dev_path.steps.exists():
            SkillPathStep.objects.create(
                skill_path=dev_path,
                skill=py_basics,
                order_index=1,
                difficulty=easy,
                level=1,
                estimated_weeks=3,
            )
            SkillPathStep.objects.create(
                skill_path=dev_path,
                skill=py_oop,
                order_index=2,
                difficulty=medium,
                level=2,
                estimated_weeks=3,
            )
            SkillPathStep.objects.create(
                skill_path=dev_path,
                skill=django,
                order_index=3,
                difficulty=medium,
                level=3,
                estimated_weeks=4,
            )
            SkillPathStep.objects.create(
                skill_path=dev_path,
                skill=sql_skill,
                order_index=4,
                difficulty=medium,
                level=3,
                estimated_weeks=3,
            )
            SkillPathStep.objects.create(
                skill_path=dev_path,
                skill=deployment,
                order_index=5,
                difficulty=hard,
                level=4,
                estimated_weeks=4,
            )
            
        # Data Science path
        ds_basics, _ = Skill.objects.get_or_create(name="Data Science Basics")
        statistics, _ = Skill.objects.get_or_create(name="Statistics & Probability")
        pandas, _ = Skill.objects.get_or_create(name="Data Analysis with Pandas")
        ml_basics, _ = Skill.objects.get_or_create(name="Machine Learning Basics")
        data_viz, _ = Skill.objects.get_or_create(name="Data Visualization")
        
        ds_path, _ = SkillPath.objects.get_or_create(
            name="Data Science Path",
            defaults={
                "description": "From basic statistics to machine learning models.",
                "stage": stages[EducationStage.UG],
                "primary_stream": science,
            },
        )
        if not ds_path.steps.exists():
            SkillPathStep.objects.create(
                skill_path=ds_path,
                skill=ds_basics,
                order_index=1,
                difficulty=easy,
                level=1,
                estimated_weeks=3,
            )
            SkillPathStep.objects.create(
                skill_path=ds_path,
                skill=statistics,
                order_index=2,
                difficulty=medium,
                level=2,
                estimated_weeks=4,
            )
            SkillPathStep.objects.create(
                skill_path=ds_path,
                skill=pandas,
                order_index=3,
                difficulty=medium,
                level=2,
                estimated_weeks=4,
            )
            SkillPathStep.objects.create(
                skill_path=ds_path,
                skill=data_viz,
                order_index=4,
                difficulty=medium,
                level=3,
                estimated_weeks=3,
            )
            SkillPathStep.objects.create(
                skill_path=ds_path,
                skill=ml_basics,
                order_index=5,
                difficulty=hard,
                level=3,
                estimated_weeks=5,
            )
            
        # Digital Marketing path
        dm_basics, _ = Skill.objects.get_or_create(name="Digital Marketing Basics")
        seo, _ = Skill.objects.get_or_create(name="Search Engine Optimization (SEO)")
        sem, _ = Skill.objects.get_or_create(name="Search Engine Marketing (SEM)")
        social_media, _ = Skill.objects.get_or_create(name="Social Media Marketing")
        analytics, _ = Skill.objects.get_or_create(name="Marketing Analytics")
        
        dm_path, _ = SkillPath.objects.get_or_create(
            name="Digital Marketing Specialist Path",
            defaults={
                "description": "From marketing basics to advanced digital strategies.",
                "stage": stages[EducationStage.UG],
                "primary_stream": commerce,
            },
        )
        if not dm_path.steps.exists():
            SkillPathStep.objects.create(
                skill_path=dm_path,
                skill=dm_basics,
                order_index=1,
                difficulty=easy,
                level=1,
                estimated_weeks=2,
            )
            SkillPathStep.objects.create(
                skill_path=dm_path,
                skill=seo,
                order_index=2,
                difficulty=medium,
                level=2,
                estimated_weeks=3,
            )
            SkillPathStep.objects.create(
                skill_path=dm_path,
                skill=sem,
                order_index=3,
                difficulty=medium,
                level=2,
                estimated_weeks=3,
            )
            SkillPathStep.objects.create(
                skill_path=dm_path,
                skill=social_media,
                order_index=4,
                difficulty=medium,
                level=3,
                estimated_weeks=3,
            )
            SkillPathStep.objects.create(
                skill_path=dm_path,
                skill=analytics,
                order_index=5,
                difficulty=hard,
                level=3,
                estimated_weeks=4,
            )

        # More comprehensive questions for different stages
        
        # High school questions
        if not Question.objects.filter(stage=stages[EducationStage.HIGH_SCHOOL]).exists():
            # Question 1
            q1 = Question.objects.create(
                text="How do you feel about solving maths and logic puzzles?",
                stage=stages[EducationStage.HIGH_SCHOOL],
            )
            OptionScore.objects.create(
                question=q1,
                option_text="I enjoy them a lot",
                logical_score=3,
                analytical_score=3,
            )
            OptionScore.objects.create(
                question=q1,
                option_text="They are okay",
                logical_score=1,
                analytical_score=1,
            )
            OptionScore.objects.create(
                question=q1,
                option_text="I avoid them",
            )

            # Question 2
            q2 = Question.objects.create(
                text="Do you like reading and writing long answers or essays?",
                stage=stages[EducationStage.HIGH_SCHOOL],
            )
            OptionScore.objects.create(
                question=q2,
                option_text="Yes, I like it",
                creative_score=2,
                people_score=1,
            )
            OptionScore.objects.create(
                question=q2,
                option_text="Sometimes",
                creative_score=1,
            )
            OptionScore.objects.create(
                question=q2,
                option_text="No, I prefer short answers",
            )
            
            # Question 3
            q3 = Question.objects.create(
                text="How do you feel about working with technology and computers?",
                stage=stages[EducationStage.HIGH_SCHOOL],
            )
            OptionScore.objects.create(
                question=q3,
                option_text="I love it and want to learn more",
                logical_score=2,
                practical_score=3,
                design_score=1,
            )
            OptionScore.objects.create(
                question=q3,
                option_text="It's okay, I can work with it",
                practical_score=1,
            )
            OptionScore.objects.create(
                question=q3,
                option_text="I find it difficult and prefer other subjects",
            )
            
            # Question 4
            q4 = Question.objects.create(
                text="Do you enjoy working in groups or leading projects?",
                stage=stages[EducationStage.HIGH_SCHOOL],
            )
            OptionScore.objects.create(
                question=q4,
                option_text="Yes, I enjoy collaborating and leading",
                people_score=3,
                practical_score=1,
            )
            OptionScore.objects.create(
                question=q4,
                option_text="Sometimes, depends on the project",
                people_score=1,
            )
            OptionScore.objects.create(
                question=q4,
                option_text="I prefer working alone",
            )

        # Middle school questions
        if not Question.objects.filter(stage=stages[EducationStage.MIDDLE]).exists():
            q1 = Question.objects.create(
                text="What do you enjoy doing in your free time?",
                stage=stages[EducationStage.MIDDLE],
            )
            OptionScore.objects.create(
                question=q1,
                option_text="Building things, solving puzzles, or coding",
                logical_score=2,
                practical_score=2,
            )
            OptionScore.objects.create(
                question=q1,
                option_text="Reading books, writing stories, or drawing",
                creative_score=2,
                people_score=1,
            )
            OptionScore.objects.create(
                question=q1,
                option_text="Playing sports or outdoor activities",
                practical_score=2,
            )
            
            # Question 2
            q2 = Question.objects.create(
                text="Which subjects do you find most interesting?",
                stage=stages[EducationStage.MIDDLE],
            )
            OptionScore.objects.create(
                question=q2,
                option_text="Maths and Science",
                logical_score=2,
                scientific_score=2,
            )
            OptionScore.objects.create(
                question=q2,
                option_text="Languages and Social Studies",
                creative_score=1,
                people_score=2,
            )
            OptionScore.objects.create(
                question=q2,
                option_text="Arts, Music, or Drawing",
                creative_score=3,
                design_score=2,
            )

        # UG/PG questions
        if not Question.objects.filter(stage=stages[EducationStage.UG]).exists():
            q1 = Question.objects.create(
                text="What type of projects do you prefer working on?",
                stage=stages[EducationStage.UG],
            )
            OptionScore.objects.create(
                question=q1,
                option_text="Technical projects involving coding or engineering",
                logical_score=3,
                scientific_score=2,
                practical_score=2,
            )
            OptionScore.objects.create(
                question=q1,
                option_text="Research projects or academic writing",
                analytical_score=3,
                creative_score=1,
            )
            OptionScore.objects.create(
                question=q1,
                option_text="Creative projects like design or media",
                creative_score=3,
                design_score=3,
            )

        # Activity suggestions for different stages
        ActivitySuggestion.objects.get_or_create(
            stage=stages[EducationStage.PRIMARY],
            title="Join a robotics or science fun club",
            defaults={
                "description": "Encourage simple experiments, building with blocks, and coding games.",
                "focus_area": "logical",
            },
        )
        ActivitySuggestion.objects.get_or_create(
            stage=stages[EducationStage.PRIMARY],
            title="Participate in art and craft activities",
            defaults={
                "description": "Develop creativity and fine motor skills through drawing, painting, and making things.",
                "focus_area": "creative",
            },
        )
        ActivitySuggestion.objects.get_or_create(
            stage=stages[EducationStage.MIDDLE],
            title="Participate in debates or speech competitions",
            defaults={
                "description": "Helps with confidence, communication, and critical thinking.",
                "focus_area": "communication",
            },
        )
        ActivitySuggestion.objects.get_or_create(
            stage=stages[EducationStage.MIDDLE],
            title="Join a math or science olympiad club",
            defaults={
                "description": "Enhance problem-solving skills and logical thinking through competitive activities.",
                "focus_area": "logical",
            },
        )
        ActivitySuggestion.objects.get_or_create(
            stage=stages[EducationStage.HIGH_SCHOOL],
            title="Participate in science fairs and exhibitions",
            defaults={
                "description": "Apply classroom knowledge to real-world projects and develop presentation skills.",
                "focus_area": "scientific",
            },
        )
        ActivitySuggestion.objects.get_or_create(
            stage=stages[EducationStage.HIGH_SCHOOL],
            title="Join a coding or programming club",
            defaults={
                "description": "Develop technical skills and logical thinking through hands-on programming projects.",
                "focus_area": "logical",
            },
        )

        # Motivation tips for different audiences and stages
        MotivationTip.objects.get_or_create(
            audience=MotivationTip.AUDIENCE_SCHOOL,
            text="Small daily practice in your weak subject is more powerful than last-minute study.",
        )
        MotivationTip.objects.get_or_create(
            audience=MotivationTip.AUDIENCE_SCHOOL,
            stage=stages[EducationStage.HIGH_SCHOOL],
            text="Choosing the right stream now will make your future career path smoother. Focus on your interests, not just peer pressure.",
        )
        MotivationTip.objects.get_or_create(
            audience=MotivationTip.AUDIENCE_SCHOOL,
            stage=stages[EducationStage.MIDDLE],
            text="Exploring different subjects and activities now will help you discover your true interests for the future.",
        )
        MotivationTip.objects.get_or_create(
            audience=MotivationTip.AUDIENCE_UG_PG,
            text="University is not just about grades; it's about building skills and networks that will support your career.",
        )
        MotivationTip.objects.get_or_create(
            audience=MotivationTip.AUDIENCE_PROFESSIONAL,
            text="Learning one new skill at a time makes career switches realistic and less stressful.",
        )
        MotivationTip.objects.get_or_create(
            audience=MotivationTip.AUDIENCE_PROFESSIONAL,
            text="Set small, achievable learning goals each week to maintain momentum in your career development.",
        )
        MotivationTip.objects.get_or_create(
            audience=MotivationTip.AUDIENCE_PARENT,
            text="Focus on your child's genuine interests and efforts, not just marks.",
        )
        MotivationTip.objects.get_or_create(
            audience=MotivationTip.AUDIENCE_PARENT,
            text="Encourage your child to explore different fields through activities and discussions about their interests.",
        )

        self.stdout.write(self.style.SUCCESS("Seeding completed."))

    def create_learning_resources(self, stages, science, commerce, arts, vocational):
        """Create sample learning resources including YouTube videos for different streams."""
        
        # Science stream resources
        LearningResource.objects.get_or_create(
            title="Introduction to Physics - Basic Concepts",
            url="https://www.youtube.com/watch?v=ZM8ECpQHNUM",
            defaults={
                "description": "Basic physics concepts for high school students",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.HIGH_SCHOOL],
                "stream": science,
                "duration_minutes": 15,
            }
        )
        
        LearningResource.objects.get_or_create(
            title="Chemistry Experiments at Home",
            url="https://www.youtube.com/watch?v=lpvEd94rdeY",
            defaults={
                "description": "Safe chemistry experiments you can do at home",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.HIGH_SCHOOL],
                "stream": science,
                "duration_minutes": 20,
            }
        )
        
        LearningResource.objects.get_or_create(
            title="Mathematics: Calculus Basics",
            url="https://www.youtube.com/watch?v=HfACrKJ_Y2w",
            defaults={
                "description": "Introduction to calculus concepts for beginners",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.HIGH_SCHOOL],
                "stream": science,
                "duration_minutes": 25,
            }
        )
        
        LearningResource.objects.get_or_create(
            title="Biology: Cell Structure and Functions",
            url="https://www.youtube.com/watch?v=41_NPkvx19M",
            defaults={
                "description": "Detailed explanation of cell biology",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.HIGH_SCHOOL],
                "stream": science,
                "duration_minutes": 18,
            }
        )
        
        # Engineering preparation resources
        LearningResource.objects.get_or_create(
            title="JEE Main Preparation Strategy",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            defaults={
                "description": "Effective preparation strategy for JEE Main examination",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.HIGH_SCHOOL],
                "stream": science,
                "duration_minutes": 22,
            }
        )
        
        LearningResource.objects.get_or_create(
            title="NEET Biology Preparation Tips",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            defaults={
                "description": "How to prepare effectively for NEET Biology section",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.HIGH_SCHOOL],
                "stream": science,
                "duration_minutes": 19,
            }
        )
        
        # Commerce stream resources
        LearningResource.objects.get_or_create(
            title="Basics of Accounting Principles",
            url="https://www.youtube.com/watch?v=UFc08zFU3f8",
            defaults={
                "description": "Introduction to accounting fundamentals",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.HIGH_SCHOOL],
                "stream": commerce,
                "duration_minutes": 22,
            }
        )
        
        LearningResource.objects.get_or_create(
            title="Business Studies: Entrepreneurship",
            url="https://www.youtube.com/watch?v=68kG2t0G7NM",
            defaults={
                "description": "Understanding entrepreneurship and business creation",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.HIGH_SCHOOL],
                "stream": commerce,
                "duration_minutes": 19,
            }
        )
        
        # CA preparation resources
        LearningResource.objects.get_or_create(
            title="CA Foundation Preparation Guide",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            defaults={
                "description": "Complete guide to preparing for CA Foundation exams",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.HIGH_SCHOOL],
                "stream": commerce,
                "duration_minutes": 25,
            }
        )
        
        # Arts stream resources
        LearningResource.objects.get_or_create(
            title="History: Ancient Civilizations",
            url="https://www.youtube.com/watch?v=q4GdJVvdxss",
            defaults={
                "description": "Overview of ancient civilizations and their contributions",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.HIGH_SCHOOL],
                "stream": arts,
                "duration_minutes": 24,
            }
        )
        
        LearningResource.objects.get_or_create(
            title="Political Science: Government Systems",
            url="https://www.youtube.com/watch?v=rAhA3Z5R4CU",
            defaults={
                "description": "Different types of government systems around the world",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.HIGH_SCHOOL],
                "stream": arts,
                "duration_minutes": 21,
            }
        )
        
        # Law preparation resources
        LearningResource.objects.get_or_create(
            title="CLAT Preparation Strategy",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            defaults={
                "description": "Effective strategy for CLAT law entrance exam",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.HIGH_SCHOOL],
                "stream": arts,
                "duration_minutes": 23,
            }
        )
        
        # Programming and tech resources for all streams
        LearningResource.objects.get_or_create(
            title="Python Programming for Beginners",
            url="https://www.youtube.com/watch?v=_uQrJ0TkZlc",
            defaults={
                "description": "Complete Python tutorial for absolute beginners",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.UG],
                "duration_minutes": 300,
            }
        )
        
        LearningResource.objects.get_or_create(
            title="Web Development Full Course",
            url="https://www.youtube.com/watch?v=Q33KBiDriJY",
            defaults={
                "description": "Learn HTML, CSS, JavaScript in one course",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.UG],
                "duration_minutes": 240,
            }
        )
        
        LearningResource.objects.get_or_create(
            title="Data Science with Python",
            url="https://www.youtube.com/watch?v=LHBE6Q9XlzI",
            defaults={
                "description": "Complete data science tutorial using Python",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.UG],
                "duration_minutes": 360,
            }
        )
        
        # Career switching resources
        LearningResource.objects.get_or_create(
            title="Career Change: From Accountant to Data Analyst",
            url="https://www.youtube.com/watch?v=5k38wN6RgMs",
            defaults={
                "description": "How to transition from accounting to data analysis",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.PROFESSIONAL],
                "duration_minutes": 25,
            }
        )
        
        LearningResource.objects.get_or_create(
            title="Cloud Computing Basics for IT Professionals",
            url="https://www.youtube.com/watch?v=1pG4ATCx61A",
            defaults={
                "description": "Introduction to cloud computing for IT professionals",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.PROFESSIONAL],
                "duration_minutes": 35,
            }
        )
        
        # Additional career switching resources
        LearningResource.objects.get_or_create(
            title="Transitioning from Sales to Digital Marketing",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            defaults={
                "description": "Complete guide to moving from sales to digital marketing",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.PROFESSIONAL],
                "duration_minutes": 28,
            }
        )
        
        LearningResource.objects.get_or_create(
            title="From Teacher to Instructional Designer",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            defaults={
                "description": "How educators can transition to instructional design roles",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.PROFESSIONAL],
                "duration_minutes": 26,
            }
        )
        
        # General motivation and study resources
        LearningResource.objects.get_or_create(
            title="How to Study Effectively",
            url="https://www.youtube.com/watch?v=pQ348JVT6IU",
            defaults={
                "description": "Proven techniques to improve your studying",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.HIGH_SCHOOL],
                "duration_minutes": 15,
            }
        )
        
        LearningResource.objects.get_or_create(
            title="Time Management Tips for Students",
            url="https://www.youtube.com/watch?v=iU4/2i8Lw1o",
            defaults={
                "description": "Effective time management strategies for students",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.HIGH_SCHOOL],
                "duration_minutes": 12,
            }
        )
        
        # Professional development resources
        LearningResource.objects.get_or_create(
            title="Networking Tips for Career Changers",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            defaults={
                "description": "How to build professional networks when changing careers",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.PROFESSIONAL],
                "duration_minutes": 20,
            }
        )
        
        LearningResource.objects.get_or_create(
            title="Building a Portfolio for Career Transition",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            defaults={
                "description": "Creating impactful portfolios to showcase transferable skills",
                "resource_type": "VIDEO",
                "stage": stages[EducationStage.PROFESSIONAL],
                "duration_minutes": 22,
            }
        )
        
        # Create sample milestones
        from recommender.models import Milestone
        
        # Bronze milestones
        Milestone.objects.get_or_create(
            name="First Step",
            defaults={
                "description": "Complete your first skill step",
                "badge_type": Milestone.BADGE_BRONZE,
                "required_completed_steps": 1
            }
        )
        
        # Create sample feedback
        from recommender.models import Feedback
        
        # Sample feedback entries
        Feedback.objects.get_or_create(
            feedback_type="RECOMMENDATION",
            rating=5,
            comment="The career recommendations were very helpful and aligned with my interests.",
            suggestion="Add more career options for creative fields."
        )
        
        Feedback.objects.get_or_create(
            feedback_type="UI_EXPERIENCE",
            rating=4,
            comment="The interface is clean and easy to navigate.",
            suggestion="Consider adding dark mode for better eye comfort during long sessions."
        )
        
        Feedback.objects.get_or_create(
            feedback_type="FEATURE_REQUEST",
            comment="Would love to see a feature for setting reminders for skill practice.",
            suggestion="Add notification system for daily learning reminders."
        )
        
        Milestone.objects.get_or_create(
            name="Getting Started",
            defaults={
                "description": "Complete 3 skill steps",
                "badge_type": Milestone.BADGE_BRONZE,
                "required_completed_steps": 3
            }
        )
        
        # Silver milestones
        Milestone.objects.get_or_create(
            name="Making Progress",
            defaults={
                "description": "Complete 5 skill steps",
                "badge_type": Milestone.BADGE_SILVER,
                "required_completed_steps": 5
            }
        )
        
        Milestone.objects.get_or_create(
            name="Half Way There",
            defaults={
                "description": "Reach 50% completion on your skill path",
                "badge_type": Milestone.BADGE_SILVER,
                "required_progress_percent": 50
            }
        )
        
        # Gold milestones
        Milestone.objects.get_or_create(
            name="Consistency King",
            defaults={
                "description": "Maintain a 5-day learning streak",
                "badge_type": Milestone.BADGE_GOLD,
                "required_streak_days": 5
            }
        )
        
        Milestone.objects.get_or_create(
            name="Path Master",
            defaults={
                "description": "Complete 100% of your skill path",
                "badge_type": Milestone.BADGE_GOLD,
                "required_progress_percent": 100
            }
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded all data including milestones"))
