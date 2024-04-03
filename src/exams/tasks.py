from celery import shared_task, current_app
from celery import current_task
from accounts.models import Student, CustomUser
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from exams.models import Exam, ExamToken, StudentAnswer, ExamQuestion, ExamChoice
import logging


logger = logging.getLogger(__name__)


@shared_task
def schedule_exam_task(exam_id):
    try:
        exam = Exam.objects.get(id=exam_id)
        if exam.emails_sent:
            return
        enrolled_students = Student.objects.filter(courses_joined__id=exam.modules.first().course.id)
        course = exam.modules.first().course
        faculty = course.faculty
        subject = course.subject
        study_year = course.study_year
        for student in enrolled_students:
            token = get_random_string(length=32)
            ExamToken.objects.create(exam=exam, token=token, student_email=student.user.email)
            exam_link = f"https://abi-hanifah-university.net/exam/take/{token}"
            subject = f"اختبار {subject}"
            message = render_to_string('exams/exam_email.html', {'exam_link': exam_link, 'faculty': faculty, 'subject': subject, 'study_year': study_year})
            try:
                send_mail(subject, message, 'exams@abi-hanifah-university.net', [student.user.email], fail_silently=False, auth_user='exams@abi-hanifah-university.net', auth_password='XK?Hna}g68+ke')
                logger.info(f"Email sent successfully to {student.user.email} for exam ID: {exam_id}")
            except Exception as e:
                logger.error(f"Failed to send email to {student.user.email} for exam ID: {exam_id}. Error: {e}")
        exam.emails_sent = True
        exam.task_id = current_task.request.id
        exam.save()
        perform_periodic_exam_actions.apply_async(args=[exam_id])
    except Exam.DoesNotExist:
        pass


@shared_task
def perform_periodic_exam_actions(exam_id):
    try:
        exam = Exam.objects.get(id=exam_id)
        if not exam.is_accessible():
            # If the exam is not accessible anymore, revoke the task
            current_app.control.revoke(schedule_exam_task.request.id)

        if timezone.now() >= exam.scheduled_datetime + timezone.timedelta(minutes=exam.duration_minutes):
            # Exam time is up, automatically submit the exam for all students
            for exam_token in ExamToken.objects.filter(exam=exam, used=False):
                exam_token.used = True
                submit_exam_automatically(exam_token.student_email, exam_token)

    except Exam.DoesNotExist:
        pass


def submit_exam_automatically(student_email, exam_token):
    user = CustomUser.objects.get(email=student_email)
    exam = exam_token.exam
    exam_questions = ExamQuestion.objects.filter(exam=exam)
    with transaction.atomic():
        total_marks_obtained = 0
        # Save student's answers
        for exam_question in exam_questions:
            # Access the related Question for the ExamQuestion
            question = exam_question.question

            try:
                # Get the correct choice for the question
                correct_choice = question.choices.get(is_correct=True)
            except ObjectDoesNotExist:
                correct_choice = None

            if correct_choice:
                # A choice was selected (question was answered)
                exam_choice, _ = ExamChoice.objects.get_or_create(exam_question=exam_question, choice_text=correct_choice.choice_text)
                StudentAnswer.objects.create(student=user.student_profile, exam_question=exam_question, exam=exam,
                                             selected_choice=exam_choice, mark_obtained=exam_question.mark)
                total_marks_obtained += exam_question.mark
            else:
                # No choice was selected (question was not answered)
                StudentAnswer.objects.create(student=user.student_profile, exam_question=exam_question, exam=exam,
                                             selected_choice=None, mark_obtained=0)

    # Mark the token as used
    exam_token.used = True
    exam_token.save()
    redirect_url = reverse('display_corrected_answers', kwargs={'token': exam_token.token})
    return redirect(redirect_url)

#@shared_task
#def check_exam_time(token):
#    from .models import ExamToken
#    from django.utils import timezone
#
#    exam_token = ExamToken.objects.filter(token=token, used=False).first()
#    if exam_token and timezone.now() > exam_token.exam.scheduled_datetime:
#        # Automatically submit the exam
#        from .tasks import submit_exam
#        submit_exam.delay(token)


#class Command(BaseCommand):
#    help = 'Updates the is_exam_active field of associated courses based on exam schedules.'
#
#    def handle(self, *args, **options):
#        print("checking active emails")
#        # Get exams scheduled for the current time
#        current_time = timezone.now()
#        exams_to_lock = Exam.objects.filter(scheduled_datetime__lte=current_time,
#                                           scheduled_datetime__gte=current_time - timezone.timedelta(minutes=30),
#                                           lock_course_during_exam=True)
#
#        # Update is_exam_active field for associated courses
#        for exam in exams_to_lock:
#            course = exam.modules.first().course
#            course.is_exam_active = True
#            course.save()
#
#        # Deactivate exams that have ended
#        expired_exams = Exam.objects.filter(scheduled_datetime__lte=current_time - timezone.timedelta(minutes=30))
#        for exam in expired_exams:
#            course = exam.modules.first().course
#            course.is_exam_active = False
#            course.save()
#
#@shared_task
#def update_course_exam_status():
#    call_command('update_course_exam_status')