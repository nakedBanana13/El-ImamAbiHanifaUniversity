from django import forms
from django.contrib.auth.models import Group
from django.forms.widgets import ClearableFileInput
from .models import Instructor, CustomUser
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


class MultiFileField(forms.FileField):
    widget = MultiFileInput


class StudentRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(render_value=True))
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    faculty = forms.ModelChoiceField(queryset=Faculty.objects.all())
    study_year = forms.ModelChoiceField(queryset=StudyYear.objects.all())
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    documents = MultiFileField(required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'confirm_password', 'first_name', 'last_name', 'email', 'date_of_birth', 'photo', 'faculty', 'study_year', 'documents']

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return confirm_password

    def clean_documents(self):
        documents = self.cleaned_data.get('documents')
        if documents:
            # Ensure each uploaded file size is not more than 10MB
            for doc in documents:
                if len(doc) > 10 * 1024 * 1024:  # Check file size in bytes
                    raise forms.ValidationError("File size exceeds 10MB limit")
        return documents


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
            raise forms.ValidationError("Password and Confirm Password do not match.")

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