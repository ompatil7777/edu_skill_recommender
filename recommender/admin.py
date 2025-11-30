from django.contrib import admin

from . import models


@admin.register(models.EducationStage)
class EducationStageAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "min_class", "max_class")
    search_fields = ("code", "name")


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "education_stage", "current_class", "current_role", "target_role", "is_parent_mode")
    list_filter = ("education_stage", "is_parent_mode")
    search_fields = ("name", "current_role", "target_role")


@admin.register(models.InterestCategory)
class InterestCategoryAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


class OptionScoreInline(admin.TabularInline):
    model = models.OptionScore
    extra = 1


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "stage", "question_type", "is_active")
    list_filter = ("stage", "question_type", "is_active")
    search_fields = ("text",)
    inlines = [OptionScoreInline]


@admin.register(models.Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(models.Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ("name", "stream")
    list_filter = ("stream",)
    search_fields = ("name",)


@admin.register(models.SkillDifficulty)
class SkillDifficultyAdmin(admin.ModelAdmin):
    list_display = ("code", "label")


class SkillPathStepInline(admin.TabularInline):
    model = models.SkillPathStep
    extra = 1


@admin.register(models.Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(models.SkillPath)
class SkillPathAdmin(admin.ModelAdmin):
    list_display = ("name", "stage", "primary_stream")
    list_filter = ("stage", "primary_stream")
    search_fields = ("name",)
    inlines = [SkillPathStepInline]


@admin.register(models.RecommendationRule)
class RecommendationRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "stage", "recommended_stream", "priority")
    list_filter = ("stage", "recommended_stream")


@admin.register(models.RecommendationHistory)
class RecommendationHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "user_profile", "created_at", "stage_snapshot")
    list_filter = ("stage_snapshot", "created_at")
    search_fields = ("notes",)


@admin.register(models.UserSkillProgress)
class UserSkillProgressAdmin(admin.ModelAdmin):
    list_display = ("user_profile", "skill_path", "step", "status", "updated_at")
    list_filter = ("status", "skill_path")


@admin.register(models.MotivationTip)
class MotivationTipAdmin(admin.ModelAdmin):
    list_display = ("audience", "stage", "text")
    list_filter = ("audience", "stage")


@admin.register(models.ActivitySuggestion)
class ActivitySuggestionAdmin(admin.ModelAdmin):
    list_display = ("title", "stage", "focus_area")
    list_filter = ("stage", "focus_area")
    search_fields = ("title",)
