from django.db import models


class NewsItem(models.Model):
    title = models.CharField(max_length=200, verbose_name='العنوان')
    content = models.TextField(verbose_name='المحتوى')
    published_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ النشر')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'خبر'
        verbose_name_plural = 'أخبار'
