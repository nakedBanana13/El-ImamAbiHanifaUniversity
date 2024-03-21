import os
import re
from datetime import date
from django import forms
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.forms.widgets import ClearableFileInput
from django.utils.translation import gettext_lazy as _
from .models import Instructor, CustomUser, Student
from courses.models import Faculty, StudyYear


class PhotoThumbnailWidget(ClearableFileInput):
    template_name = 'widgets/photo_thumbnail_widget.html'

    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username', '')  # Get the username from kwargs
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['username'] = self.username  # Add username to the context
        return context


class MultiFileInput(forms.ClearableFileInput):
    template_name = 'widgets/multiple_file_input.html'


#class MultiFileField(forms.FileField):
#    widget = MultiFileInput


class StudentRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(render_value=True))
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    faculty = forms.ModelChoiceField(queryset=Faculty.objects.all())
    study_year = forms.ModelChoiceField(queryset=StudyYear.objects.all())
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    #documents = MultiFileField(required=False)

    father_name = forms.CharField(max_length=100)
    country_born = forms.CharField(max_length=200)
    country_of_residence = forms.CharField(max_length=200)
    phone_number = forms.CharField(max_length=25)
    qualification = forms.ChoiceField(choices=Student.QUALIFICATION_CHOICES)
    language = forms.ChoiceField(choices=Student.LANGUAGES_CHOICES)
    certificate_photo = forms.ImageField()
    id_photo = forms.ImageField()

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'confirm_password', 'first_name', 'last_name', 'email', 'date_of_birth', 'photo', 'faculty', 'study_year', 'father_name', 'country_born', 'country_of_residence', 'phone_number', 'qualification', 'language', 'certificate_photo', 'id_photo']

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("كلمات المرور غير متطابقة")
        return confirm_password

    #def clean_documents(self):
    #    documents = self.cleaned_data.get('documents')
    #    if documents:
    #        # Ensure each uploaded file size is not more than 10MB
    #        for doc in documents:
    #            if len(doc) > 10 * 1024 * 1024:  # Check file size in bytes
    #                raise forms.ValidationError("File size exceeds 10MB limit")
    #    return documents

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if date_of_birth:
            # Calculate age based on date of birth
            today = date.today()  # Explicitly reference the date class
            age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            # Check if age is reasonable
            if age < 10 or age > 100:
                raise forms.ValidationError("يرجى إدخال تاريخ ميلاد صحيح.")
        return date_of_birth

    def clean_email(self):
        email = self.cleaned_data.get('email')
        domain = email.split('@')[-1]
        allowed_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'icloud.com', 'protonmail.com',
                           'mail.com', 'yandex.com']
        if domain not in allowed_domains:
            allowed_domains_str = ', '.join(allowed_domains)
            raise ValidationError(f"عذرًا، لتسجيل فقط باستخدام مزودي البريد الإلكتروني التالية: {allowed_domains_str}.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # Regular expression to match phone numbers consisting only of numbers,
        # which may or may not start with '+'
        # The pattern allows for '+' at the beginning, followed by zero or more digits
        if not re.match(r'^\+?\d+$', phone_number):
            raise ValidationError(_('الرجاء إدخال رقم هاتف صحيح، يجب أن يتكون فقط من أرقام وقد يبدأ بـ "+".'))
        return phone_number


class InstructorAdminForm(forms.ModelForm):
    class Meta:
        model = Instructor
        exclude = ('user',)

    # Additional fields for CustomUser model
    username = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput(render_value=True), required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    is_active = forms.BooleanField(required=False)
    is_approved = forms.BooleanField(required=False)
    photo = forms.ImageField(widget=PhotoThumbnailWidget, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')

        if instance:
            # Populate the form fields with instance data
            self.fields['username'].initial = instance.user.username
            self.fields['first_name'].initial = instance.user.first_name
            self.fields['last_name'].initial = instance.user.last_name
            self.fields['email'].initial = instance.user.email
            self.fields['date_of_birth'].initial = instance.user.date_of_birth
            self.fields['is_active'].initial = instance.user.is_active
            self.fields['is_approved'].initial = instance.user.is_approved
            self.fields['photo'].initial = instance.user.photo

            # Hide password and confirm_password fields
            self.fields['password'].widget = forms.HiddenInput()
            self.fields['confirm_password'].widget = forms.HiddenInput()
        else:
            self.fields['is_active'].initial = True
            self.fields['is_approved'].initial = True

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("كلمة السر و تأكيد كلمة السر غير متطابقين")

    def save(self, commit=True):
        instructor = super().save(commit=False)

        # If the instructor instance is new or being created
        if not instructor.pk:
            # Create a corresponding CustomUser instance
            user = CustomUser.objects.create_user(
                username=self.cleaned_data['username'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email'],
                date_of_birth=self.cleaned_data['date_of_birth'],
                is_active=self.cleaned_data['is_active'],
                is_approved=self.cleaned_data['is_approved'],
                is_student=False,
                photo=self.cleaned_data['photo'],
            )
            # Set the password if provided
            if self.cleaned_data['password']:
                user.set_password(self.cleaned_data['password'])
                user.save()

            # Associate the newly created user with the instructor
            instructor.user = user
            group = Group.objects.get(name='Instructors')
            user.groups.add(group)

        # If the instructor instance already exists and is being updated
        else:
            # Update fields of the associated CustomUser instance
            user = instructor.user
            if self.cleaned_data['photo']:
                old_photo_path = user.photo.path
                if os.path.exists(old_photo_path):
                    os.remove(old_photo_path)
            user.username = self.cleaned_data['username']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.date_of_birth = self.cleaned_data['date_of_birth']
            user.is_active = self.cleaned_data['is_active']
            user.is_approved = self.cleaned_data['is_approved']
            user.photo = self.cleaned_data['photo']
            # Save the updated CustomUser instance
            user.save()

        # Save the instructor instance
        if commit:
            instructor.save()
        return instructor
