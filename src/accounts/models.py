from ElImamAbiHanifaUniversity.settings import IMAGES_ALLOWED_EXTENSIONS
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import FileExtensionValidator
from django.db import models
from django_countries.fields import CountryField


def user_profile_photo_path(instance, filename):
    username = instance.username
    return f"profile_pics/{username}/{filename}"


def student_certificate_photo_path(instance, filename):
    username = instance.user.username
    return f"certificates/{username}/{filename}"


def student_id_photo_path(instance, filename):
    username = instance.user.username
    return f"ids/{username}/{filename}"


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_approved = models.BooleanField(default=False, verbose_name='موافق عليه')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    is_student = models.BooleanField(default=True, verbose_name='طالب')
    date_of_birth = models.DateField(null=True, verbose_name='تاريخ الميلاد')
    photo = models.ImageField(
        upload_to=user_profile_photo_path,
        blank=False,
        validators=[FileExtensionValidator(allowed_extensions=IMAGES_ALLOWED_EXTENSIONS)],
        verbose_name='الصورة الشخصية'
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    groups = models.ManyToManyField(
        Group,
        verbose_name='المجموعات',
        blank=True,
        related_name='customuser_set'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='صلاحيات المستخدم',
        blank=True,
        related_name='customuser_set'
    )

    @property
    def student_profile(self):
        try:
            return self.student
        except Student.DoesNotExist:
            return None

    @property
    def instructor_profile(self):
        try:
            return self.instructor
        except Instructor.DoesNotExist:
            return None

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'المستخدم'
        verbose_name_plural = 'المستخدمين'


class Student(models.Model):
    QUALIFICATION_CHOICES = [
        ('شهادة ثانوية أو ما يعادلها من المعاهد الشرعية', 'شهادة ثانوية أو ما يعادلها من المعاهد الشرعية'),
        ('إجازة بالقرآن الكريم', 'إجازة بالقرآن الكريم'),
        ('شهادة أكاديمية الإمام الأعظم أبي حنيفة النعمان رضي الله تعالى عنه', 'شهادة أكاديمية الإمام الأعظم أبي حنيفة النعمان رضي الله تعالى عنه'),
        ('بكالوريوس', 'بكالوريوس'),
        ('ماجستير', 'ماجستير'),
        ('دكتوراة', 'دكتوراة'),
    ]

    LANGUAGES_CHOICES = [
        ('العربية', 'العربية'),
        ('الإنجليزية', 'الإنجليزية'),
        ('الفرنسية', 'الفرنسية'),
        ('الفارسية', 'الفارسية'),
        ('آردو', 'آردو'),
        ('الأندونيسية', 'الأندونيسية'),
        ('الباكستانية', 'الباكستانية'),
        ('غير ذلك', 'غير ذلك'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True, verbose_name='المستخدم')
    faculty = models.ForeignKey('courses.Faculty', on_delete=models.CASCADE, verbose_name='الكلية')
    study_year = models.ForeignKey('courses.StudyYear', on_delete=models.CASCADE, verbose_name='العام الدراسي')
    father_name = models.CharField(max_length=100, verbose_name='اسم الأب')
    country_born = models.CharField(max_length=200,  null=True, choices=CountryField().choices + [('', 'Select Country')], verbose_name='بلد الميلاد')
    country_of_residence = models.CharField(max_length=200,  null=True, choices=CountryField().choices + [('', 'Select Country')], verbose_name='بلد الإقامة')
    phone_number = models.CharField(max_length=25, verbose_name='رقم الموبايل مع الرمز الدولي')
    qualification = models.CharField(max_length=100, choices=QUALIFICATION_CHOICES, verbose_name='المؤهل العلمي')
    language = models.CharField(max_length=50, choices=LANGUAGES_CHOICES, verbose_name='اللغة الأم')
    certificate_photo = models.ImageField(upload_to=student_certificate_photo_path, blank=False, validators=[FileExtensionValidator(allowed_extensions=IMAGES_ALLOWED_EXTENSIONS)], verbose_name='الشهادة الثانوية أو إجازة في القرآن الكريم أو شهادة شرعية')
    id_photo = models.ImageField(upload_to=student_id_photo_path, blank=False, validators=[FileExtensionValidator(allowed_extensions=IMAGES_ALLOWED_EXTENSIONS)], verbose_name='صورة إثبات الشخصية (جواز السفر أو بطاقة الهوية أو قيد مدني)')

    def __str__(self):
        return f' الطالب:{self.user.first_name} {self.user.last_name}'

    class Meta:
        verbose_name = 'الطالب'
        verbose_name_plural = 'الطلاب'


class Instructor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True, verbose_name='المستخدم')

    def __str__(self):
        return f'المدرس: {self.user.first_name} {self.user.last_name}'

    class Meta:
        verbose_name = 'المدرس'
        verbose_name_plural = 'المدرسون'


#def user_directory_path(instance, filename):
#    return f"students_documents/{instance.user.username}/{filename}"
#
#
#class Document(models.Model):
#    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='المستخدم')
#    document = models.FileField(upload_to=user_directory_path, validators=[FileExtensionValidator(allowed_extensions=FILES_ALLOWED_EXTENSIONS)], verbose_name='المستند')
#    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الرفع')
#
#    def __str__(self):
#        return f'{self.document.name}'
#
#    class Meta:
#        verbose_name = 'المستند'
#        verbose_name_plural = 'المستندات'
