from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
from courses.models import Course


class EnrollStudentMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'student'):
            try:
                student = request.user.student_profile
                faculty = student.faculty
                study_year = student.study_year
                matching_courses = Course.objects.filter(faculty=faculty, study_year=study_year)
                for course in matching_courses:
                    if not student.courses_joined.filter(pk=course.pk).exists():
                        student.courses_joined.add(course)
            except ObjectDoesNotExist:
                # Handle case where CustomUser has no associated Student instance
                pass


class ExamAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user and request.user.is_authenticated and not request.user.is_superuser and request.user.is_student:
            if request.path.startswith('/student/'):
                student_courses = request.user.student_profile.courses_joined.all()
                for course in student_courses:
                    modules = course.modules.all()
                    for module in modules:
                        exams = module.exams.filter(lock_course_during_exam=True)
                        for exam in exams:
                            if exam.is_accessible():
                                course.is_exam_active = True
                                course.save()
                                return render(request, 'exams/locked_during_exam.html')
                            else:
                                course.is_exam_active = False
                                course.save()
        return response
