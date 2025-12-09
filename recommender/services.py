import json
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from datetime import datetime

from django.db import connection, models
from django.utils import timezone

from .models import (
    ActivitySuggestion,
    Career,
    EducationStage,
    LearningResource,
    MotivationTip,
    RecommendationHistory,
    RecommendationRule,
    SkillPath,
    SkillPathStep,
    Stream,
    UserProfile,
    UserLearningProgress,
    UserSkillProgress,
)


@dataclass
class InterestProfile:
    logical: int = 0
    analytical: int = 0
    creative: int = 0
    practical: int = 0
    people: int = 0
    scientific: int = 0
    design: int = 0

    @classmethod
    def from_option_scores(cls, options: List[Dict[str, int]]) -> "InterestProfile":
        data: Dict[str, int] = {
            "logical": 0,
            "analytical": 0,
            "creative": 0,
            "practical": 0,
            "people": 0,
            "scientific": 0,
            "design": 0,
        }
        for opt in options:
            for key in data.keys():
                data[key] += int(opt.get(key, 0))
        return cls(**data)

    def to_dict(self) -> Dict[str, int]:
        return {
            "logical": self.logical,
            "analytical": self.analytical,
            "creative": self.creative,
            "practical": self.practical,
            "people": self.people,
            "scientific": self.scientific,
            "design": self.design,
        }


def classify_stage(current_class: Optional[int], is_professional: bool, is_counselor: bool) -> EducationStage:
    """Classify user into an EducationStage based on simple rules."""

    if is_counselor:
        return EducationStage.objects.get(code=EducationStage.COUNSELOR)

    if is_professional:
        return EducationStage.objects.get(code=EducationStage.PROFESSIONAL)

    if current_class is None:
        return EducationStage.objects.get(code=EducationStage.UG)

    if 1 <= current_class <= 5:
        code = EducationStage.PRIMARY
    elif 6 <= current_class <= 8:
        code = EducationStage.MIDDLE
    elif 9 <= current_class <= 10:
        code = EducationStage.HIGH_SCHOOL
    elif 11 <= current_class <= 12:
        code = EducationStage.HIGHER_SECONDARY
    else:
        code = EducationStage.UG

    return EducationStage.objects.get(code=code)


def compute_stream_scores(
    interest_profile: InterestProfile,
    subject_levels: Dict[str, int],
) -> Dict[str, int]:
    """Compute rule-based scores for different streams for 9-12."""

    maths = int(subject_levels.get("maths", 0))
    science = int(subject_levels.get("science", 0))
    english = int(subject_levels.get("english", 0))
    business = int(subject_levels.get("business", 0))
    creativity = int(subject_levels.get("creativity", 0))
    language = int(subject_levels.get("language", 0))
    social = int(subject_levels.get("social", 0))

    logical_interest = interest_profile.logical + interest_profile.analytical
    business_interest = interest_profile.practical + interest_profile.people
    social_interest = interest_profile.people

    science_score = maths + science + logical_interest
    commerce_score = maths + english + business_interest
    arts_score = creativity + language + social_interest

    academic_total = maths + science + english
    vocational_score = interest_profile.practical * 2 + max(0, 30 - academic_total)

    return {
        Stream.SCIENCE: science_score,
        Stream.COMMERCE: commerce_score,
        Stream.ARTS: arts_score,
        Stream.VOCATIONAL: vocational_score,
    }


def rank_streams(stream_scores: Dict[str, int]) -> List[Tuple[str, int]]:
    return sorted(stream_scores.items(), key=lambda item: item[1], reverse=True)


def recommend_streams_with_explanations(
    interest_profile: InterestProfile,
    subject_levels: Dict[str, int],
) -> Dict[str, Dict]:
    scores = compute_stream_scores(interest_profile, subject_levels)
    ranked = rank_streams(scores)

    result: Dict[str, Dict] = {}
    for idx, (stream_code, score) in enumerate(ranked[:3]):
        try:
            stream = Stream.objects.get(code=stream_code)
        except Stream.DoesNotExist:
            continue

        label = "Plan A" if idx == 0 else ("Plan B" if idx == 1 else "Plan C")

        explanation_parts = []
        if stream_code == Stream.SCIENCE:
            explanation_parts.append("You showed comfort with maths and science and logical thinking.")
        elif stream_code == Stream.COMMERCE:
            explanation_parts.append("You are comfortable with numbers and communication, which helps in Commerce.")
        elif stream_code == Stream.ARTS:
            explanation_parts.append("Your creativity and language/social interests point towards Arts.")
        else:
            explanation_parts.append("You like hands-on, practical work, which suits vocational paths.")

        explanation = " ".join(explanation_parts)

        result[label] = {
            "stream": stream,
            "score": score,
            "explanation": explanation,
            "pros": stream.pros,
            "cons": stream.cons,
            "required_strengths": stream.required_strengths,
            "key_subjects": stream.key_subjects,
            "early_preparation_ideas": stream.early_preparation_ideas,
        }

    return result


def get_career_recommendations_for_stream(
    stream: Stream, interest_profile: InterestProfile
) -> List[Dict[str, str]]:
    """Return simple rule-based career suggestions for a stream."""

    careers = list(stream.careers.all())
    results: List[Dict[str, str]] = []

    for career in careers:
        if stream.code == Stream.SCIENCE:
            reason = "Because you enjoy problem-solving and science, technical careers like this can fit you well."
        elif stream.code == Stream.COMMERCE:
            reason = "Your comfort with numbers and business thinking supports this career." \
                " It can lead to roles in finance, business, or analytics."
        elif stream.code == Stream.ARTS:
            reason = "Your creative and language interests make this a natural direction."
        else:
            reason = "Your practical, hands-on preferences make this vocational career suitable."

        if career.why_it_fits_template:
            reason = career.why_it_fits_template

        results.append(
            {
                "name": career.name,
                "description": career.description,
                "why_fit": reason,
                "exams": career.suggested_exams_text,
            }
        )

    return results


def get_skill_paths_for_target(
    stage: EducationStage, stream: Optional[Stream], target_role: str, interest_profile: Optional[InterestProfile] = None
) -> Dict[str, SkillPath]:
    """Return Plan A/B/C skill paths based on stage, stream, textual target role, and interest profile."""

    queryset = SkillPath.objects.all()
    if stage:
        queryset = queryset.filter(models.Q(stage=stage) | models.Q(stage__isnull=True))
    if stream:
        queryset = queryset.filter(models.Q(primary_stream=stream) | models.Q(primary_stream__isnull=True))

    target_lower = (target_role or "").lower()

    def path_score(path: SkillPath) -> int:
        score = 0
        name_l = path.name.lower()
        
        # Score based on target role keywords
        if any(k in target_lower for k in ["cloud", "aws"]):
            if "cloud" in name_l or "aws" in name_l:
                score += 3
        if any(k in target_lower for k in ["data", "analytics"]):
            if "data" in name_l or "analytics" in name_l:
                score += 3
        if any(k in target_lower for k in ["developer", "software", "python"]):
            if "developer" in name_l or "python" in name_l:
                score += 3
        
        # Score based on interest profile if provided
        if interest_profile:
            # Technical/Logical interests favor technical paths
            if interest_profile.logical > 5 or interest_profile.analytical > 5:
                if any(keyword in name_l for keyword in ["developer", "engineer", "technical", "python", "data"]):
                    score += 2
            
            # Creative interests favor design/creative paths
            if interest_profile.creative > 5 or interest_profile.design > 5:
                if any(keyword in name_l for keyword in ["design", "creative", "ui", "ux", "graphic"]):
                    score += 2
            
            # People-oriented interests favor business/communication paths
            if interest_profile.people > 5:
                if any(keyword in name_l for keyword in ["marketing", "business", "communication", "sales"]):
                    score += 2
            
            # Scientific interests favor research/analysis paths
            if interest_profile.scientific > 5:
                if any(keyword in name_l for keyword in ["research", "science", "analysis", "data"]):
                    score += 2
            
            # Practical interests favor hands-on paths
            if interest_profile.practical > 5:
                if any(keyword in name_l for keyword in ["support", "operations", "technical"]):
                    score += 2
        
        return score

    paths = list(queryset)
    paths.sort(key=path_score, reverse=True)

    result: Dict[str, SkillPath] = {}
    labels = ["Plan A", "Plan B", "Plan C"]
    for label, path in zip(labels, paths[:3]):
        result[label] = path
    return result


def initialize_progress_for_path(user: UserProfile, path: SkillPath) -> None:
    steps = list(path.steps.all())
    for step in steps:
        UserSkillProgress.objects.get_or_create(
            user_profile=user,
            skill_path=path,
            step=step,
            defaults={
                'status': UserSkillProgress.NOT_STARTED,
                'step_progress': 0,
                'milestone_achieved': False
            }
        )


def compute_progress_summary(user: UserProfile, path: SkillPath) -> Dict[str, object]:
    qs = UserSkillProgress.objects.filter(user_profile=user, skill_path=path)
    total = qs.count()
    completed = qs.filter(status=UserSkillProgress.COMPLETED).count()
    in_progress = qs.filter(status=UserSkillProgress.IN_PROGRESS).count()

    percent = int(round((completed / total) * 100)) if total else 0

    difficulty_counts: Dict[str, int] = {"Easy": 0, "Medium": 0, "Hard": 0}
    for prog in qs.select_related("step__difficulty"):
        label = prog.step.difficulty.label
        difficulty_counts[label] = difficulty_counts.get(label, 0) + 1

    difficulty_text = (
        f"Easy: {difficulty_counts.get('Easy', 0)}, "
        f"Medium: {difficulty_counts.get('Medium', 0)}, "
        f"Hard: {difficulty_counts.get('Hard', 0)}"
    )
    
    # Check for milestones
    milestones_achieved = qs.filter(milestone_achieved=True).count()
    
    # Calculate streak (consecutive days with progress)
    streak = calculate_streak(user, path)

    return {
        "total": total,
        "completed": completed,
        "in_progress": in_progress,
        "percent": percent,
        "difficulty_text": difficulty_text,
        "milestones_achieved": milestones_achieved,
        "streak": streak
    }


def calculate_streak(user: UserProfile, path: SkillPath) -> int:
    """Calculate the current streak of consecutive days with progress."""
    # This is a simplified implementation
    # In a real application, you would track daily progress in a separate model
    # For now, we'll simulate a streak based on completed steps
    from .models import UserSkillProgress
    completed_steps = UserSkillProgress.objects.filter(
        user_profile=user, 
        skill_path=path, 
        status=UserSkillProgress.COMPLETED
    ).count()
    
    # Simulate streak: 1 day for every 2 completed steps, up to 7 days
    streak = min(completed_steps // 2, 7)
    return streak


def check_and_award_milestones(user: UserProfile, path: SkillPath) -> List[Dict[str, str]]:
    """Check if user qualifies for any milestones and award them."""
    from .models import Milestone, UserMilestone
    
    # Get user's current progress
    summary = compute_progress_summary(user, path)
    
    # Get all milestones not yet achieved by the user
    achieved_milestone_ids = UserMilestone.objects.filter(user_profile=user).values_list('milestone_id', flat=True)
    unachieved_milestones = Milestone.objects.exclude(id__in=achieved_milestone_ids)
    
    newly_awarded = []
    
    for milestone in unachieved_milestones:
        # Check if user qualifies for this milestone
        qualifies = False
        
        # Check progress percent requirement
        if milestone.required_progress_percent > 0:
            if summary['percent'] >= milestone.required_progress_percent:
                qualifies = True
        
        # Check completed steps requirement
        if milestone.required_completed_steps > 0:
            if summary['completed'] >= milestone.required_completed_steps:
                qualifies = True
        
        # Check streak requirement
        if milestone.required_streak_days > 0:
            streak = summary.get('streak', 0)
            if streak >= milestone.required_streak_days:
                qualifies = True
        
        # Award milestone if qualified
        if qualifies:
            UserMilestone.objects.get_or_create(
                user_profile=user,
                milestone=milestone
            )
            newly_awarded.append({
                'name': milestone.name,
                'badge_type': milestone.badge_type,
                'description': milestone.description
            })
    
    return newly_awarded


def save_recommendation_history(
    user: Optional[UserProfile],
    stage_label: str,
    input_payload: Dict,
    streams_payload: Dict,
    careers_payload: Dict,
    skill_paths_payload: Dict,
    notes: str = "",
) -> RecommendationHistory:
    history = RecommendationHistory.objects.create(
        user_profile=user,
        stage_snapshot=stage_label,
        input_data=json.dumps(input_payload),
        output_streams=json.dumps(streams_payload, default=str),
        output_careers=json.dumps(careers_payload, default=str),
        output_skill_paths=json.dumps(skill_paths_payload, default=str),
        notes=notes,
    )
    return history


def get_motivation_tips(stage: EducationStage, audience: str) -> List[MotivationTip]:
    return list(
        MotivationTip.objects.filter(audience=audience).filter(
            models.Q(stage=stage) | models.Q(stage__isnull=True)
        )
    )


def get_activity_suggestions(stage: EducationStage) -> List[ActivitySuggestion]:
    return list(ActivitySuggestion.objects.filter(stage=stage))


def get_learning_resources_for_user(
    user: UserProfile, 
    stage: Optional[EducationStage] = None,
    stream: Optional[Stream] = None,
    skill: Optional[str] = None,
    career: Optional[str] = None,
    resource_type: Optional[str] = None,
    limit: int = 20
) -> List[LearningResource]:
    """Get learning resources tailored to user profile and preferences."""
    queryset = LearningResource.objects.filter(is_active=True)
    
    # Filter by stage if provided
    if stage:
        queryset = queryset.filter(
            models.Q(stage=stage) | models.Q(stage__isnull=True)
        )
    
    # Filter by stream if provided
    if stream:
        queryset = queryset.filter(
            models.Q(stream=stream) | models.Q(stream__isnull=True)
        )
    
    # Filter by skill if provided
    if skill:
        queryset = queryset.filter(
            models.Q(skill__name__icontains=skill) | models.Q(skill__isnull=True)
        )
    
    # Filter by career if provided
    if career:
        queryset = queryset.filter(
            models.Q(career__name__icontains=career) | models.Q(career__isnull=True)
        )
    
    # Filter by resource type if provided
    if resource_type:
        queryset = queryset.filter(resource_type=resource_type)
    
    return list(queryset[:limit])


def get_user_learning_progress(user: UserProfile, resource: LearningResource) -> UserLearningProgress:
    """Get or create learning progress record for a user and resource."""
    progress, created = UserLearningProgress.objects.get_or_create(
        user_profile=user,
        resource=resource,
        defaults={
            'status': UserLearningProgress.NOT_STARTED,
            'progress_percent': 0,
        }
    )
    return progress


def update_learning_progress(
    user: UserProfile, 
    resource: LearningResource, 
    status: Optional[str] = None,
    progress_percent: Optional[int] = None,
    notes: Optional[str] = None
) -> UserLearningProgress:
    """Update user's learning progress for a resource."""
    progress, created = UserLearningProgress.objects.get_or_create(
        user_profile=user,
        resource=resource,
        defaults={
            'status': UserLearningProgress.NOT_STARTED,
            'progress_percent': 0,
        }
    )
    
    # Update fields if provided
    if status:
        progress.status = status
        if status == UserLearningProgress.IN_PROGRESS and not progress.started_at:
            progress.started_at = timezone.now()
        elif status == UserLearningProgress.COMPLETED and not progress.completed_at:
            progress.completed_at = timezone.now()
    
    if progress_percent is not None:
        progress.progress_percent = progress_percent
    
    if notes:
        progress.notes = notes
    
    progress.updated_at = timezone.now()
    progress.save()
    
    return progress


def update_skill_step_progress(
    user: UserProfile,
    step: SkillPathStep,
    status: Optional[str] = None,
    progress_percent: Optional[int] = None,
    milestone_achieved: Optional[bool] = None
) -> UserSkillProgress:
    """Update user's progress for a specific skill step."""
    progress, created = UserSkillProgress.objects.get_or_create(
        user_profile=user,
        step=step,
        skill_path=step.skill_path,
        defaults={
            'status': UserSkillProgress.NOT_STARTED,
            'step_progress': 0,
            'milestone_achieved': False
        }
    )
    
    # Update fields if provided
    if status:
        progress.status = status
    
    if progress_percent is not None:
        progress.step_progress = progress_percent
        
        # Automatically set status based on progress
        if progress_percent >= 100:
            progress.status = UserSkillProgress.COMPLETED
        elif progress_percent > 0:
            progress.status = UserSkillProgress.IN_PROGRESS
        else:
            progress.status = UserSkillProgress.NOT_STARTED
    
    if milestone_achieved is not None:
        progress.milestone_achieved = milestone_achieved
        if milestone_achieved and not progress.milestone_date:
            from django.utils import timezone
            progress.milestone_date = timezone.now()
    
    progress.updated_at = timezone.now()
    progress.save()
    
    return progress


def get_personalized_youtube_recommendations(
    user: UserProfile,
    stage: Optional[EducationStage] = None,
    stream: Optional[Stream] = None
) -> List[LearningResource]:
    """Get personalized YouTube video recommendations based on user profile."""
    return get_learning_resources_for_user(
        user=user,
        stage=stage,
        stream=stream,
        resource_type='VIDEO',
        limit=15
    )


def get_user_milestones(user: UserProfile) -> List[Dict[str, str]]:
    """Get all milestones earned by a user."""
    from .models import UserMilestone
    
    user_milestones = UserMilestone.objects.filter(user_profile=user).select_related('milestone')
    milestones = []
    
    for um in user_milestones:
        milestones.append({
            'name': um.milestone.name,
            'badge_type': um.milestone.badge_type,
            'description': um.milestone.description,
            'achieved_at': um.achieved_at.strftime('%Y-%m-%d')
        })
    
    return milestones


def career_switch_roadmap(current_role: str, target_role: str) -> str:
    """Return a text roadmap for professionals switching careers using fixed rules."""
    
    cur = (current_role or "").lower()
    target = (target_role or "").lower()
    
    # Enhanced career switching roadmap with more detailed paths
    if "call" in cur and "support" in cur and "cloud" in target:
        return (
            "Call Center → Cloud Support Engineer roadmap:\n"
            "1. Linux basics (2–3 weeks)\n"
            "   • Command line fundamentals\n"
            "   • File system navigation\n"
            "2. Computer networking fundamentals (3 weeks)\n"
            "   • OSI model and TCP/IP\n"
            "   • DNS, DHCP, firewalls\n"
            "3. AWS core services: EC2, S3, IAM (4 weeks)\n"
            "   • Hands-on labs with AWS Free Tier\n"
            "   • Security best practices\n"
            "4. Monitoring & troubleshooting basics (2 weeks)\n"
            "   • CloudWatch, logging\n"
            "   • Common issue resolution\n"
            "5. Scripting with Python or Bash (3 weeks)\n"
            "   • Automation scripts\n"
            "   • Infrastructure as code basics"
        )
    
    if "teacher" in cur and ("designer" in target or "instructional" in target):
        return (
            "Teacher → Instructional Designer roadmap:\n"
            "1. Basics of curriculum design (2 weeks)\n"
            "   • Learning objectives and outcomes\n"
            "   • Assessment strategies\n"
            "2. E-learning tools and authoring basics (3 weeks)\n"
            "   • LMS platforms (Moodle, Canvas)\n"
            "   • Authoring tools (Articulate, Captivate)\n"
            "3. Educational psychology & assessment (3 weeks)\n"
            "   • Adult learning principles\n"
            "   • Measuring learning effectiveness\n"
            "4. Build 2–3 sample learning modules (4 weeks)\n"
            "   • Storyboarding\n"
            "   • Interactive content creation"
        )
    
    if "account" in cur and ("data" in target or "analyst" in target):
        return (
            "Accountant → Data Analyst roadmap:\n"
            "1. Excel and spreadsheets for analysis (2 weeks)\n"
            "   • Advanced formulas and pivot tables\n"
            "   • Data cleaning techniques\n"
            "2. SQL for data querying (3 weeks)\n"
            "   • SELECT, JOIN, GROUP BY statements\n"
            "   • Database design basics\n"
            "3. Python for data handling and reporting (4 weeks)\n"
            "   • Pandas for data manipulation\n"
            "   • Matplotlib/Seaborn for visualization\n"
            "4. Dashboarding and business communication (3 weeks)\n"
            "   • Tableau or Power BI basics\n"
            "   • Storytelling with data"
        )
    
    if "sales" in cur and ("marketing" in target or "digital" in target):
        return (
            "Sales Professional → Digital Marketing Specialist roadmap:\n"
            "1. Digital marketing fundamentals (2 weeks)\n"
            "   • SEO, SEM, social media marketing\n"
            "   • Content marketing basics\n"
            "2. Analytics and measurement tools (3 weeks)\n"
            "   • Google Analytics certification\n"
            "   • Conversion rate optimization\n"
            "3. Campaign management platforms (3 weeks)\n"
            "   • Google Ads, Facebook Ads\n"
            "   • Email marketing tools\n"
            "4. Content creation and copywriting (2 weeks)\n"
            "   • Writing for digital channels\n"
            "   • A/B testing principles"
        )
    
    if ("it" in cur or "tech" in cur) and ("product" in target or "manager" in target):
        return (
            "IT Professional → Product Manager roadmap:\n"
            "1. Product management fundamentals (3 weeks)\n"
            "   • Product lifecycle\n"
            "   • Market research techniques\n"
            "2. Business and strategy basics (2 weeks)\n"
            "   • Business model canvas\n"
            "   • Competitive analysis\n"
            "3. User experience and design thinking (3 weeks)\n"
            "   • User research methods\n"
            "   • Prototyping tools\n"
            "4. Data-driven decision making (2 weeks)\n"
            "   • Metrics and KPIs\n"
            "   • A/B testing frameworks"
        )
    
    return (
        "General career switch roadmap:\n"
        "1. List current strengths and experiences.\n"
        "   • Technical skills\n"
        "   • Soft skills\n"
        "   • Industry knowledge\n"
        "2. Learn core fundamentals of target domain (4–6 weeks).\n"
        "   • Online courses and certifications\n"
        "   • Industry publications\n"
        "3. Practice with small projects or case studies (4 weeks).\n"
        "   • Build a portfolio\n"
        "   • Contribute to open source\n"
        "4. Build a simple portfolio and update resume.\n"
        "   • GitHub profile\n"
        "   • Personal website\n"
        "5. Network and seek mentorship.\n"
        "   • LinkedIn connections\n"
        "   • Industry events"
    )


def get_professional_development_plan(
    user: UserProfile, 
    current_role: str, 
    target_role: str
) -> Dict[str, object]:
    """Generate a comprehensive professional development plan."""
    roadmap = career_switch_roadmap(current_role, target_role)
    
    # Get relevant learning resources
    resources = get_learning_resources_for_user(
        user=user,
        career=target_role,
        limit=10
    )
    
    # Get skill gaps analysis
    skill_gaps = analyze_skill_gaps(current_role, target_role)
    
    # Get timeline estimation based on hours per week
    estimated_timeline = estimate_transition_timeline(current_role, target_role)
    
    return {
        "roadmap": roadmap,
        "resources": resources,
        "skill_gaps": skill_gaps,
        "estimated_timeline": estimated_timeline,
        "key_skills": ["Adaptability", "Continuous Learning", "Networking"],
        "success_factors": [
            "Set clear milestones",
            "Track progress regularly",
            "Seek feedback from mentors",
            "Build relevant projects"
        ]
    }


def analyze_skill_gaps(current_role: str, target_role: str) -> List[str]:
    """Analyze skill gaps between current and target roles."""
    cur = (current_role or "").lower()
    target = (target_role or "").lower()
    
    gaps = []
    
    # Define skill mappings for common transitions
    skill_mappings = {
        ("sales", "digital marketing"): [
            "Digital marketing fundamentals",
            "Analytics and data interpretation",
            "Content creation",
            "Social media platform expertise",
            "SEO/SEM knowledge"
        ],
        ("accountant", "data analyst"): [
            "Statistical analysis",
            "Programming (Python/R)",
            "Data visualization",
            "Database querying (SQL)",
            "Machine learning basics"
        ],
        ("teacher", "instructional designer"): [
            "Learning management systems",
            "Instructional design models",
            "Multimedia authoring tools",
            "User experience design",
            "Assessment and evaluation methods"
        ],
        ("call center", "cloud support engineer"): [
            "Linux fundamentals",
            "Networking basics",
            "Cloud platforms (AWS/Azure/GCP)",
            "Scripting (Python/Bash)",
            "Troubleshooting methodologies"
        ],
        ("it", "product manager"): [
            "Product lifecycle management",
            "Market research and analysis",
            "User experience design",
            "Agile and Scrum methodologies",
            "Business strategy and planning"
        ]
    }
    
    # Check for predefined mappings
    for (source, destination), skills in skill_mappings.items():
        if source in cur and destination in target:
            gaps.extend(skills)
            break
    
    # If no specific mapping found, provide generic skills
    if not gaps:
        gaps = [
            "Industry-specific knowledge",
            "Technical skills for target role",
            "Soft skills (communication, leadership)",
            "Project management",
            "Data analysis and interpretation"
        ]
    
    return gaps


def estimate_transition_timeline(current_role: str, target_role: str) -> str:
    """Estimate timeline for career transition based on role similarity."""
    cur = (current_role or "").lower()
    target = (target_role or "").lower()
    
    # Define transition complexity mappings
    complexity_mappings = {
        ("sales", "digital marketing"): "4-6 months",
        ("accountant", "data analyst"): "8-12 months",
        ("teacher", "instructional designer"): "6-9 months",
        ("call center", "cloud support engineer"): "12-18 months",
        ("it", "product manager"): "9-15 months"
    }
    
    # Check for predefined mappings
    for (source, destination), timeline in complexity_mappings.items():
        if source in cur and destination in target:
            return timeline
    
    # Default timeline for other transitions
    return "6-12 months"


def get_career_transition_resources(current_role: str, target_role: str) -> List[LearningResource]:
    """Get learning resources specifically for career transitions."""
    # This would typically query a database of transition-specific resources
    # For now, we'll return general career switching resources
    return []


def offline_analytics_most_chosen_stream() -> Optional[str]:
    """Use raw SQL over RecommendationHistory.output_streams JSON to get a rough most-chosen stream.

    This implementation is intentionally simple and may be approximate, but satisfies the
    "offline analytics via raw SQL" requirement.
    """

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                CASE
                    WHEN output_streams LIKE '%SCIENCE%' THEN 'SCIENCE'
                    WHEN output_streams LIKE '%COMMERCE%' THEN 'COMMERCE'
                    WHEN output_streams LIKE '%ARTS%' THEN 'ARTS'
                    WHEN output_streams LIKE '%VOCATIONAL%' THEN 'VOCATIONAL'
                    ELSE NULL
                END AS stream_code,
                COUNT(*) AS cnt
            FROM recommender_recommendationhistory
            GROUP BY stream_code
            ORDER BY cnt DESC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
    if not row or row[0] is None:
        return None
    return str(row[0])


def offline_analytics_most_popular_skill_path() -> Optional[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT sp.name, COUNT(*) AS cnt
            FROM recommender_userskillprogress usp
            JOIN recommender_skillpath sp ON usp.skill_path_id = sp.id
            GROUP BY sp.name
            ORDER BY cnt DESC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
    if not row:
        return None
    return str(row[0])


def submit_user_feedback(
    user_profile: Optional[UserProfile],
    feedback_type: str,
    rating: Optional[int] = None,
    comment: str = "",
    suggestion: str = ""
) -> "Feedback":
    """Submit user feedback and return the created feedback object."""
    from .models import Feedback
    
    feedback = Feedback.objects.create(
        user_profile=user_profile,
        feedback_type=feedback_type,
        rating=rating,
        comment=comment,
        suggestion=suggestion
    )
    return feedback


def get_user_feedback_stats() -> Dict[str, object]:
    """Get statistics about user feedback for analytics dashboard."""
    from .models import Feedback
    
    total_feedback = Feedback.objects.count()
    resolved_feedback = Feedback.objects.filter(is_resolved=True).count()
    avg_rating = Feedback.objects.exclude(rating__isnull=True).aggregate(
        avg=models.Avg('rating')
    )['avg']
    
    # Feedback by type
    feedback_by_type = {}
    for feedback_type, _ in Feedback.FEEDBACK_TYPES:
        count = Feedback.objects.filter(feedback_type=feedback_type).count()
        feedback_by_type[feedback_type] = count
    
    # Recent feedback
    recent_feedback = Feedback.objects.select_related('user_profile').order_by('-created_at')[:5]
    
    return {
        'total_feedback': total_feedback,
        'resolved_feedback': resolved_feedback,
        'average_rating': round(avg_rating, 1) if avg_rating else None,
        'feedback_by_type': feedback_by_type,
        'recent_feedback': recent_feedback
    }
