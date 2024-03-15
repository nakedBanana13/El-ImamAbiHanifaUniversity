from ElImamAbiHanifaUniversity.settings import FILES_ALLOWED_EXTENSIONS, IMAGES_ALLOWED_EXTENSIONS
from accounts.models import Instructor
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import FileExtensionValidator
from django.db import models
from django.template.loader import render_to_string
from django.utils.text import slugify
from .fields import OrderField


class Faculty(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='الكلية')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'الكلية'
        verbose_name_plural = 'الكليات'


class StudyYear(models.Model):
    year = models.CharField(max_length=50, verbose_name='السنة')
    semester = models.CharField(max_length=50, verbose_name='الفصل')

    def __str__(self):
        return f"السنة: {self.year}---الفصل: {self.semester}"

    class Meta:
        verbose_name = 'السنة الدراسية'
        verbose_name_plural = 'السنوات الدراسية'


class Subject(models.Model):
    title = models.CharField(max_length=200, verbose_name='العنوان')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='الرابط')
    faculty = models.ForeignKey(Faculty, related_name='subjects', on_delete=models.CASCADE, verbose_name='الكلية')

    class Meta:
        ordering = ['title']
        verbose_name = 'المادة'
        verbose_name_plural = 'المواد'

    def __str__(self):
        return self.title


class Course(models.Model):
    owner = models.ForeignKey(Instructor, related_name='courses_created',
                              on_delete=models.CASCADE, verbose_name='المدرس')  # The instructor who created this course
    faculty = models.ForeignKey(Faculty, related_name='courses', on_delete=models.CASCADE, verbose_name='الكلية')
    subject = models.ForeignKey(Subject, related_name='courses',
                                on_delete=models.CASCADE, verbose_name='المادة')  # The subject that this course belongs to
    study_year = models.ForeignKey(StudyYear, related_name='courses', on_delete=models.CASCADE, verbose_name='العام الدراسي')
    title = models.CharField(max_length=200, verbose_name='العنوان')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='الرابط')  # The slug of the course. This will be used in URLs
    overview = models.TextField(verbose_name='نبذة عن الدورة')
    created = models.DateTimeField(
        auto_now_add=True, verbose_name='تاريخ الإنشاء')  # The date and time when the course was created (automatically set)
    is_active = models.BooleanField(default=False, verbose_name='نشطة')
    from accounts.models import Student
    students = models.ManyToManyField(Student, related_name='courses_joined', blank=True, verbose_name='الطلاب')
    is_exam_active = models.BooleanField(default=False, verbose_name='هل الامتحان نشط؟')

    class Meta:
        ordering = ['-created']
        verbose_name = 'الدورة'
        verbose_name_plural = 'الدورات'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)  # Generate slug from title
        super().save(*args, **kwargs)

    def is_content_locked(self):
        return self.is_exam_active


class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE, verbose_name='الدورة')
    title = models.CharField(max_length=200, verbose_name='العنوان')
    description = models.TextField(blank=True, verbose_name='الوصف')
    order = OrderField(blank=True, for_fields=['course'], verbose_name='الترتيب')
    is_active = models.BooleanField(default=True, verbose_name='نشطة')

    def __str__(self):
        return f'{self.order}. {self.title}'

    class Meta:
        verbose_name = 'الوحدة'
        verbose_name_plural = 'الوحدات'


class Content(models.Model):
    module = models.ForeignKey(Module, related_name='contents', on_delete=models.CASCADE, verbose_name='الوحدة')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'model__in': ('text',
                                                                                                            'video',
                                                                                                            'image',
                                                                                                            'file')}, verbose_name='نوع المحتوى')
    object_id = models.PositiveIntegerField(verbose_name='رقم الكائن')  # to store the primary key of the related object
    item = GenericForeignKey('content_type', 'object_id')  # A GenericForeignKey field to the related object combining
    # the two previous fields

    order = OrderField(blank=True, for_fields=['module'], verbose_name='الترتيب')

    class Meta:
        ordering = ['order']
        verbose_name = 'المحتوى'
        verbose_name_plural = 'المحتويات'


class ItemBase(models.Model):
    owner = models.ForeignKey(
        Instructor,
        related_name='%(class)s_related',
        on_delete=models.CASCADE,
        verbose_name='المالك'
    )
    title = models.CharField(max_length=250, verbose_name='العنوان')
    created = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated = models.DateTimeField(auto_now=True, verbose_name='تاريخ آخر تحديث')

    class Meta:
        abstract = True
        verbose_name = 'العنصر'
        verbose_name_plural = 'العناصر'

    def __str__(self):
        return self.title

    def render(self):
        return render_to_string(f'courses/content/{self._meta.model_name}.html', {'item': self})


class Text(ItemBase):
    content = models.TextField(verbose_name='المحتوى')


def file_upload_path(instance, filename):
    return f"courses_files/{filename}"


class File(ItemBase):
    file = models.FileField(
        upload_to=file_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=FILES_ALLOWED_EXTENSIONS)],
        verbose_name='الملف'
    )


def image_upload_path(instance, filename):
    return f"courses_images/{filename}"


class Image(ItemBase):
    file = models.FileField(
        upload_to=image_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=IMAGES_ALLOWED_EXTENSIONS)],
        verbose_name='الصورة'
    )


class Video(ItemBase):
    url = models.URLField(blank=False, verbose_name='رابط الفيديو')
    # video_file = models.FileField(upload_to='videos', blank=True, null=True)