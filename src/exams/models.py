from accounts.models import Instructor
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
    mark = models.PositiveIntegerField(default=1)

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


class ExamChoice(models.Model):
    exam_question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE, related_name='exam_choices')
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)