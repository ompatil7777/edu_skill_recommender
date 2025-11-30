import json
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

from django.db import connection, models

from .models import (
    ActivitySuggestion,
    Career,
    EducationStage,
    MotivationTip,
    RecommendationHistory,
    RecommendationRule,
    SkillPath,
    SkillPathStep,
    Stream,
    UserProfile,
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
    stage: EducationStage, stream: Optional[Stream], target_role: str
) -> Dict[str, SkillPath]:
    """Return Plan A/B/C skill paths based on stage, stream, and textual target role."""

    queryset = SkillPath.objects.all()
    if stage:
        queryset = queryset.filter(models.Q(stage=stage) | models.Q(stage__isnull=True))
    if stream:
        queryset = queryset.filter(models.Q(primary_stream=stream) | models.Q(primary_stream__isnull=True))

    target_lower = (target_role or "").lower()

    def path_score(path: SkillPath) -> int:
        score = 0
        name_l = path.name.lower()
        if any(k in target_lower for k in ["cloud", "aws"]):
            if "cloud" in name_l or "aws" in name_l:
                score += 3
        if any(k in target_lower for k in ["data", "analytics"]):
            if "data" in name_l or "analytics" in name_l:
                score += 3
        if any(k in target_lower for k in ["developer", "software", "python"]):
            if "developer" in name_l or "python" in name_l:
                score += 3
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

    return {
        "total": total,
        "completed": completed,
        "in_progress": in_progress,
        "percent": percent,
        "difficulty_text": difficulty_text,
    }


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


def career_switch_roadmap(current_role: str, target_role: str) -> str:
    """Return a text roadmap for professionals switching careers using fixed rules."""

    cur = (current_role or "").lower()
    target = (target_role or "").lower()

    if "call" in cur and "support" in cur and "cloud" in target:
        return (
            "Call Center → Cloud Support Engineer roadmap:\n"
            "1. Linux basics (2–3 weeks)\n"
            "2. Computer networking fundamentals (3 weeks)\n"
            "3. AWS core services: EC2, S3, IAM (4 weeks)\n"
            "4. Monitoring & troubleshooting basics (2 weeks)\n"
            "5. Scripting with Python or Bash (3 weeks)"
        )

    if "teacher" in cur and ("designer" in target or "instructional" in target):
        return (
            "Teacher → Instructional Designer roadmap:\n"
            "1. Basics of curriculum design (2 weeks)\n"
            "2. E-learning tools and authoring basics (3 weeks)\n"
            "3. Educational psychology & assessment (3 weeks)\n"
            "4. Build 2–3 sample learning modules (4 weeks)"
        )

    if "account" in cur and ("data" in target or "analyst" in target):
        return (
            "Accountant → Data Analyst roadmap:\n"
            "1. Excel and spreadsheets for analysis (2 weeks)\n"
            "2. SQL for data querying (3 weeks)\n"
            "3. Python for data handling and reporting (4 weeks)\n"
            "4. Dashboarding and business communication (3 weeks)"
        )

    return (
        "General career switch roadmap:\n"
        "1. List current strengths and experiences.\n"
        "2. Learn core fundamentals of target domain (4–6 weeks).\n"
        "3. Practice with small projects or case studies (4 weeks).\n"
        "4. Build a simple portfolio and update resume."
    )


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
