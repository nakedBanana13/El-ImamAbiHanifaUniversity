from django.contrib import admin
from .models import QuestionBank, Question, Choice, Exam


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0


@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'owner', 'created', 'updated')
    list_filter = ('course', 'owner', 'created', 'updated')
    search_fields = ('course__title', 'owner__username')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_bank', 'module', 'question_text', 'mark')
    list_filter = ('question_bank', 'module')
    search_fields = ('question_bank__course__title', 'module__title', 'question_text')
    inlines = [ChoiceInline]


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_modules', 'number_of_questions', 'duration_hours', 'scheduled_datetime', 'created')
    list_filter = ('modules', 'number_of_questions', 'duration_hours', 'scheduled_datetime', 'created')
    search_fields = ('modules__title',)

    def get_modules(self, obj):
        return ", ".join([module.title for module in obj.modules.all()])
    get_modules.short_description = 'Modules'
