from accounts.models import Instructor, Student
from django.db import models
from courses.models import Course, Module, Subject
from django.utils import timezone


class QuestionBank(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='question_bank', verbose_name='الدورة')
    owner = models.ForeignKey(Instructor, on_delete=models.CASCADE, verbose_name='المالك')
    created = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        verbose_name = "بنك الأسئلة"
        verbose_name_plural = "بنوك الأسئلة"

    def __str__(self):
        return f"مصرف الأسئلة لـ {self.course.title}"


class Question(models.Model):
    question_bank = models.ForeignKey(QuestionBank, on_delete=models.CASCADE, related_name='questions', verbose_name='مصرف الأسئلة')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='questions', verbose_name='الوحدة')
    question_text = models.TextField(verbose_name='نص السؤال')

    class Meta:
        verbose_name = "السؤال"
        verbose_name_plural = "الأسئلة"

    def __str__(self):
        return self.question_text

    def save(self, *args, **kwargs):
        if self.question_bank.course != self.module.course:
            raise ValueError("الوحدة يجب أن تنتمي إلى نفس الدورة التي ينتمي إليها مصرف الأسئلة")
        super().save(*args, **kwargs)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', verbose_name='السؤال')
    choice_text = models.CharField(max_length=200, verbose_name='نص الخيار')
    is_correct = models.BooleanField(default=False, verbose_name='صحيح')

    class Meta:
        verbose_name = "الخيار"
        verbose_name_plural = "الخيارات"

    def __str__(self):
        return self.choice_text


class Exam(models.Model):
    modules = models.ManyToManyField(Module, related_name='exams', verbose_name='الوحدات')
    number_of_questions = models.PositiveIntegerField(verbose_name='عدد الأسئلة')
    duration_minutes = models.PositiveIntegerField(verbose_name='المدة بالدقائق')
    scheduled_datetime = models.DateTimeField(verbose_name='التاريخ والوقت المجدول للامتحان')
    created = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    emails_sent = models.BooleanField(default=False, verbose_name='تم إرسال البريد الإلكتروني')
    total_marks = models.PositiveIntegerField(verbose_name='العلامة')
    lock_course_during_exam = models.BooleanField(default=False, verbose_name='قفل الدروس خلال الامتحان')

    class Meta:
        verbose_name = "امتحان"
        verbose_name_plural = "الامتحانات"

    def __str__(self):
        course = self.modules.first().course
        faculty = course.faculty
        subject = course.subject
        study_year = course.study_year
        return f"امتحان - كلية {faculty} مادة {subject} {study_year}"

    def is_accessible(self):
        """
        Method to check if the exam is accessible based on its scheduled datetime.
        """
        return timezone.now() < self.scheduled_datetime + timezone.timedelta(minutes=self.duration_minutes)


class ExamQuestion(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_questions', verbose_name='الامتحان')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='exam_questions', verbose_name='السؤال')
    mark = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name='العلامة')

    def __str__(self):
        return self.question.question_text


class ExamChoice(models.Model):
    exam_question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE, related_name='exam_choices', verbose_name='سؤال الامتحان')
    choice_text = models.CharField(max_length=200, verbose_name='نص الخيار')
    is_correct = models.BooleanField(default=False, verbose_name='صحيح')

    def __str__(self):
        return f'{self.choice_text} - ({self.is_correct})'


class ExamToken(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_tokens', verbose_name='الامتحان')
    token = models.CharField(max_length=100, unique=True, verbose_name='الرمز')
    student_email = models.EmailField(verbose_name='بريد الطالب')
    used = models.BooleanField(default=False, verbose_name='تم الاستخدام')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        verbose_name = 'رمز الامتحان'
        verbose_name_plural = 'رموز الامتحانات'

    def __str__(self):
        return self.token


class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='الطالب')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, verbose_name='الامتحان')
    exam_question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE, verbose_name='سؤال الامتحان')
    selected_choice = models.ForeignKey(ExamChoice, on_delete=models.CASCADE, verbose_name='الخيار المحدد')
    mark_obtained = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name='العلامات المحصلة لهذا السؤال')

    class Meta:
        verbose_name = 'إجابة الطالب'
        verbose_name_plural = 'إجابات الطلاب'

