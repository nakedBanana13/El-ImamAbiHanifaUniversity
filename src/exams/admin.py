from django.contrib import admin
from .models import QuestionBank, Question, Choice, Exam, ExamQuestion, ExamChoice, ExamToken, StudentAnswer


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
    list_display = ('id', 'question_bank', 'module', 'question_text')
    list_filter = ('question_bank', 'module')
    search_fields = ('question_bank__course__title', 'module__title', 'question_text')
    inlines = [ChoiceInline]


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_modules', 'number_of_questions', 'total_marks', 'duration_hours', 'scheduled_datetime', 'emails_sent', 'created')
    list_filter = ('modules', 'number_of_questions', 'duration_hours', 'scheduled_datetime', 'created')
    search_fields = ('modules__title',)

    def get_modules(self, obj):
        return ", ".join([module.title for module in obj.modules.all()])
    get_modules.short_description = 'Modules'


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ['exam', 'question', 'mark']


@admin.register(ExamChoice)
class ExamChoiceAdmin(admin.ModelAdmin):
    list_display = ['exam_question', 'choice_text', 'is_correct']
    list_filter = ['exam_question', 'is_correct']


@admin.register(ExamToken)
class ExamTokenAdmin(admin.ModelAdmin):
    list_display = ('exam', 'token', 'student_email', 'used', 'created_at')
    list_filter = ('used',)
    search_fields = ('exam__scheduled_datetime', 'student_email')
    readonly_fields = ('token', 'created_at')


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'exam_question', 'selected_choice', 'mark_obtained']
    list_filter = ('exam', 'student')
    search_fields = ('exam', 'student', 'exam_question')
