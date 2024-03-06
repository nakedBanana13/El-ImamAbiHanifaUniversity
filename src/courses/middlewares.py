from django.core.exceptions import ObjectDoesNotExist
from django.utils.deprecation import MiddlewareMixin
from courses.models import Course


class EnrollStudentMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'student'):
            try:
                student = request.user.student
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
