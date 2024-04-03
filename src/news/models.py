from accounts.models import Instructor
from courses.models import Course
from django.db import models
from django.utils import timezone


class NewsItem(models.Model):
    title = models.CharField(max_length=200, verbose_name='العنوان')
    content = models.TextField(verbose_name='المحتوى')
    published_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ النشر')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'خبر'
        verbose_name_plural = 'أخبار'


class Announcement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='announcements', verbose_name='الدورة')
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, verbose_name='المدرس')
    content = models.TextField(verbose_name='المحتوى')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='تاريخ الإنشاء')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'إعلان'
        verbose_name_plural = 'الإعلانات'

    def __str__(self):
        return self.content
