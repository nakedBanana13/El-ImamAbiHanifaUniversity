from celery import shared_task
from accounts.models import Student
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from exams.models import Exam, ExamToken


@shared_task
def schedule_exam_task(exam_id):
    try:
        exam = Exam.objects.get(id=exam_id)
        if exam.emails_sent:
            return
        enrolled_students = Student.objects.filter(courses_joined__id=exam.modules.first().course.id)
        for student in enrolled_students:
            print(student.user.email)
            token = get_random_string(length=32)
            ExamToken.objects.create(exam=exam, token=token, student_email=student.user.email)
            exam_link = f"http://domain.com/exam/{token}"
            subject = "Exam"
            message = render_to_string('exam_email.html', {'exam_link': exam_link})
            send_mail(subject, message, 'university@email.com', [student.user.email], fail_silently=False)
        exam.emails_sent = True
        exam.save()
    except Exam.DoesNotExist:
        pass


@shared_task
def check_exam_time(token):
    from .models import ExamToken
    from django.utils import timezone

    exam_token = ExamToken.objects.filter(token=token, used=False).first()
    if exam_token and timezone.now() > exam_token.exam.scheduled_datetime:
        # Automatically submit the exam
        from .tasks import submit_exam
        submit_exam.delay(token)
