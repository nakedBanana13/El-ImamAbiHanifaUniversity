from audioop import reverse

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
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
                        print(f"Student {student} enrolled in course: {course}")
            except ObjectDoesNotExist:
                # Handle case where CustomUser has no associated Student instance
                print("CustomUser has no associated Student instance")
                pass

class ExamAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            # Check if an exam is active for any of the user's enrolled courses
            enrolled_courses = request.user.student_profile.courses_joined.all()
            for course in enrolled_courses:
                if course.is_exam_active:
                    # Redirect user to "Exam in Progress" page
                    return redirect(reverse('/'))
        return response
