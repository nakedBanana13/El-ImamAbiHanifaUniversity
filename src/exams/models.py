from accounts.models import Instructor, Student
from django.db import models
from courses.models import Course, Module
from django.utils import timezone


class QuestionBank(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='question_bank')
    owner = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Question Bank"
        verbose_name_plural = "Question Banks"

    def __str__(self):
        return f"Question Bank for {self.course.title}"


class Question(models.Model):
    question_bank = models.ForeignKey(QuestionBank, on_delete=models.CASCADE, related_name='questions')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def __str__(self):
        return self.question_text

    def save(self, *args, **kwargs):
        if self.question_bank.course != self.module.course:
            raise ValueError("Module must belong to the same course as the question bank")
        super().save(*args, **kwargs)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Choice"
        verbose_name_plural = "Choices"

    def __str__(self):
        return self.choice_text


class Exam(models.Model):
    modules = models.ManyToManyField(Module, related_name='exams')
    number_of_questions = models.PositiveIntegerField()
    duration_hours = models.PositiveIntegerField(help_text="Duration of the exam in hours")
    scheduled_datetime = models.DateTimeField(help_text="Scheduled datetime for the exam")
    created = models.DateTimeField(auto_now_add=True)
    emails_sent = models.BooleanField(default=False)
    total_marks = models.PositiveIntegerField(help_text="Total marks for the exam")

    class Meta:
        verbose_name = "Exam"
        verbose_name_plural = "Exams"

    def __str__(self):
        return f"Exam - Scheduled at {self.scheduled_datetime}"

    def is_accessible(self):
        """
        Method to check if the exam is accessible based on its scheduled datetime.
        """
        return timezone.now() < self.scheduled_datetime + timezone.timedelta(hours=self.duration_hours)


class ExamQuestion(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='exam_questions')
    mark = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text="Marks for this choice")

    def __str__(self):
        return self.question.question_text


class ExamChoice(models.Model):
    exam_question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE, related_name='exam_choices')
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.choice_text} - ({self.is_correct})'


class ExamToken(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_tokens')
    token = models.CharField(max_length=100, unique=True)
    student_email = models.EmailField()
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token


class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    exam_question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(ExamChoice, on_delete=models.CASCADE)
    mark_obtained = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text="Marks obtained for this question")
