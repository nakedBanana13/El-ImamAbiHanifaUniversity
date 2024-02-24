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
    list_display = ['title', 'faculty', 'subject', 'owner', 'study_year', 'created']
    list_filter = ['created', 'subject', 'faculty', 'study_year']
    search_fields = ['title', 'overview']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]
