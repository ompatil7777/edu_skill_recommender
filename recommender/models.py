from django.db import models


class EducationStage(models.Model):
    PRIMARY = "PRIMARY"
    MIDDLE = "MIDDLE"
    HIGH_SCHOOL = "HIGH_SCHOOL"
    HIGHER_SECONDARY = "HIGHER_SECONDARY"
    UG = "UG"
    PG = "PG"
    PROFESSIONAL = "PROFESSIONAL"
    COUNSELOR = "COUNSELOR"

    STAGE_CHOICES = [
        (PRIMARY, "Primary (Class 1-5)"),
        (MIDDLE, "Middle (Class 6-8)"),
        (HIGH_SCHOOL, "High School (Class 9-10)"),
        (HIGHER_SECONDARY, "Higher Secondary (Class 11-12)"),
        (UG, "Undergraduate"),
        (PG, "Postgraduate"),
        (PROFESSIONAL, "Working Professional"),
        (COUNSELOR, "Parent / Teacher / Counselor"),
    ]

    code = models.CharField(max_length=32, unique=True, choices=STAGE_CHOICES)
    name = models.CharField(max_length=64)
    min_class = models.PositiveIntegerField(null=True, blank=True)
    max_class = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


class UserProfile(models.Model):
    name = models.CharField(max_length=128)
    age = models.PositiveIntegerField(null=True, blank=True)
    education_stage = models.ForeignKey(EducationStage, on_delete=models.PROTECT)
    current_class = models.PositiveIntegerField(null=True, blank=True)
    current_role = models.CharField(max_length=128, blank=True)
    target_role = models.CharField(max_length=128, blank=True)
    is_parent_mode = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class InterestCategory(models.Model):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


class Question(models.Model):
    INTEREST = "INTEREST"
    SUBJECT_STRENGTH = "SUBJECT_STRENGTH"

    QUESTION_TYPE_CHOICES = [
        (INTEREST, "Interest / Aptitude"),
        (SUBJECT_STRENGTH, "Subject Strength"),
    ]

    text = models.TextField()
    stage = models.ForeignKey(EducationStage, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    question_type = models.CharField(max_length=32, choices=QUESTION_TYPE_CHOICES, default=INTEREST)

    def __str__(self) -> str:
        return self.text[:80]


class OptionScore(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    option_text = models.CharField(max_length=255)

    logical_score = models.IntegerField(default=0)
    analytical_score = models.IntegerField(default=0)
    creative_score = models.IntegerField(default=0)
    practical_score = models.IntegerField(default=0)
    people_score = models.IntegerField(default=0)
    scientific_score = models.IntegerField(default=0)
    design_score = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.question_id}: {self.option_text}"[:80]


class Stream(models.Model):
    SCIENCE = "SCIENCE"
    COMMERCE = "COMMERCE"
    ARTS = "ARTS"
    VOCATIONAL = "VOCATIONAL"

    STREAM_CHOICES = [
        (SCIENCE, "Science"),
        (COMMERCE, "Commerce"),
        (ARTS, "Arts"),
        (VOCATIONAL, "Vocational"),
    ]

    code = models.CharField(max_length=32, unique=True, choices=STREAM_CHOICES)
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    pros = models.TextField(blank=True)
    cons = models.TextField(blank=True)
    required_strengths = models.TextField(blank=True)
    key_subjects = models.TextField(blank=True)
    early_preparation_ideas = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


class Career(models.Model):
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name="careers")
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    why_it_fits_template = models.TextField(
        blank=True,
        help_text="Short explanation template, e.g. 'You enjoy maths and logical thinking, so engineering suits you.'",
    )
    suggested_exams_text = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


class SkillDifficulty(models.Model):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

    DIFFICULTY_CHOICES = [
        (EASY, "Easy"),
        (MEDIUM, "Medium"),
        (HARD, "Hard"),
    ]

    code = models.CharField(max_length=16, unique=True, choices=DIFFICULTY_CHOICES)
    label = models.CharField(max_length=32)

    def __str__(self) -> str:
        return self.label


class Skill(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


class SkillPath(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    stage = models.ForeignKey(EducationStage, on_delete=models.SET_NULL, null=True, blank=True)
    primary_stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class SkillPathStep(models.Model):
    LEVEL_CHOICES = [
        (1, "Level 1 - Foundations"),
        (2, "Level 2 - Core"),
        (3, "Level 3 - Tools / Frameworks"),
        (4, "Level 4 - Projects / Deployment"),
    ]

    skill_path = models.ForeignKey(SkillPath, on_delete=models.CASCADE, related_name="steps")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    order_index = models.PositiveIntegerField()
    difficulty = models.ForeignKey(SkillDifficulty, on_delete=models.PROTECT)
    level = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES)
    estimated_weeks = models.PositiveIntegerField(default=2)

    class Meta:
        ordering = ["order_index"]

    def __str__(self) -> str:
        return f"{self.skill_path.name}: {self.skill.name}"


class RecommendationRule(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    stage = models.ForeignKey(EducationStage, on_delete=models.SET_NULL, null=True, blank=True)

    min_science_score = models.IntegerField(null=True, blank=True)
    min_commerce_score = models.IntegerField(null=True, blank=True)
    min_arts_score = models.IntegerField(null=True, blank=True)

    recommended_stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True)
    primary_career = models.ForeignKey(Career, on_delete=models.SET_NULL, null=True, blank=True)
    primary_skill_path = models.ForeignKey(SkillPath, on_delete=models.SET_NULL, null=True, blank=True)

    priority = models.IntegerField(default=100)

    def __str__(self) -> str:
        return self.name


class RecommendationHistory(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    stage_snapshot = models.CharField(max_length=64, blank=True)
    input_data = models.TextField(blank=True)
    output_streams = models.TextField(blank=True)
    output_careers = models.TextField(blank=True)
    output_skill_paths = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"Session {self.id} - {self.created_at:%Y-%m-%d}" if self.id else "Unsaved session"


class UserSkillProgress(models.Model):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

    STATUS_CHOICES = [
        (NOT_STARTED, "Not started"),
        (IN_PROGRESS, "In progress"),
        (COMPLETED, "Completed"),
    ]

    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    skill_path = models.ForeignKey(SkillPath, on_delete=models.CASCADE)
    step = models.ForeignKey(SkillPathStep, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=NOT_STARTED)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user_profile", "step")

    def __str__(self) -> str:
        return f"{self.user_profile} - {self.step} - {self.status}"


class MotivationTip(models.Model):
    AUDIENCE_SCHOOL = "SCHOOL"
    AUDIENCE_UG_PG = "UG_PG"
    AUDIENCE_PROFESSIONAL = "PROFESSIONAL"
    AUDIENCE_PARENT = "PARENT"

    AUDIENCE_CHOICES = [
        (AUDIENCE_SCHOOL, "School student"),
        (AUDIENCE_UG_PG, "UG/PG student"),
        (AUDIENCE_PROFESSIONAL, "Professional"),
        (AUDIENCE_PARENT, "Parent / Counselor"),
    ]

    text = models.TextField()
    audience = models.CharField(max_length=32, choices=AUDIENCE_CHOICES)
    stage = models.ForeignKey(EducationStage, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return self.text[:80]


class ActivitySuggestion(models.Model):
    stage = models.ForeignKey(EducationStage, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    focus_area = models.CharField(max_length=64, blank=True)

    def __str__(self) -> str:
        return self.title
