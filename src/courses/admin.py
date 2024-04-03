from django.contrib import admin
from .models import Subject, Course, Module, Faculty, StudyYear


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(StudyYear)
class StudyYearAdmin(admin.ModelAdmin):
    list_display = ['year', 'semester']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}


class ModuleInline(admin.StackedInline):
    model = Module


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'faculty', 'subject', 'owner', 'study_year', 'is_active', 'is_exam_active',  'created']
    list_filter = ['subject', 'faculty', 'study_year', 'is_active']
    search_fields = ['title', 'overview']
    search_help_text = 'Search by title, overview'
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['course', 'title', 'description', 'is_active', 'order']
    list_filter = ['course',]
    search_fields = ['title', 'description']
    search_help_text = 'ابحث عن طريق العنوان أو الشرح'
