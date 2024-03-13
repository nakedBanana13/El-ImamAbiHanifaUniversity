from ElImamAbiHanifaUniversity.settings import FILES_ALLOWED_EXTENSIONS, IMAGES_ALLOWED_EXTENSIONS
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import FileExtensionValidator
from django.db import models


class CustomUser(AbstractUser):
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_student = models.BooleanField(default=True)
    date_of_birth = models.DateField(null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True, validators=[FileExtensionValidator(allowed_extensions=IMAGES_ALLOWED_EXTENSIONS)])
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    groups = models.ManyToManyField(Group, verbose_name='groups', blank=True, related_name='customuser_set')
    user_permissions = models.ManyToManyField(Permission, verbose_name='user permissions', blank=True,
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


class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    faculty = models.ForeignKey('courses.Faculty', on_delete=models.CASCADE)
    study_year = models.ForeignKey('courses.StudyYear', on_delete=models.CASCADE)

    def __str__(self):
        return f'Student: {self.user.first_name} {self.user.last_name}'


class Instructor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f'Instructor: {self.user.first_name} {self.user.last_name}'


def user_directory_path(instance, filename):
    return f"documents/{instance.user.username}/{filename}"


class Document(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    document = models.FileField(upload_to=user_directory_path, validators=[FileExtensionValidator(allowed_extensions=FILES_ALLOWED_EXTENSIONS)])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.document.name}'
