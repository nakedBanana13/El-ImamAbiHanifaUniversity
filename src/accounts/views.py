import os

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView, FormView, UpdateView
from .models import CustomUser, Student, Document
from .forms import StudentRegistrationForm


class StudentRegistrationView(FormView):
    template_name = 'accounts/register.html'
    form_class = StudentRegistrationForm
    success_url = reverse_lazy('registration_done')

    def form_valid(self, form):
        # Extract user information including the birth_date
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']
        date_of_birth = form.cleaned_data['date_of_birth']
        photo = form.cleaned_data['photo']

        # Save user instance
        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            date_of_birth=date_of_birth,
            photo=photo
        )

        # Extract faculty and study_year from the form
        faculty = form.cleaned_data['faculty']
        study_year = form.cleaned_data['study_year']

        # Create Student instance and associate it with the user
        Student.objects.create(user=user, faculty=faculty, study_year=study_year)

        # Save uploaded documents associated with the user
        documents = self.request.FILES.getlist('documents')
        if documents:
            for doc in documents:
                Document.objects.create(user=user, document=doc)

        return HttpResponseRedirect(self.get_success_url())


class RegistrationDoneView(TemplateView):
    template_name = 'accounts/registration_done.html'


class CustomLoginView(LoginView):
    def get_success_url(self):
        # Call the parent class's get_success_url method to get the default URL
        success_url = super().get_success_url()

        # Retrieve the authenticated user
        user = self.request.user

        # Determine the user type
        if user.is_authenticated:
            if user.is_student:
                return '/account/dashboard/'  # Redirect to the student dashboard
            return '/course/mine/'  # Redirect to the instructor dashboard

        # If user type is not recognized, redirect to the default success URL
        return success_url


class StudentDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/student_dashboard.html'


class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentRegistrationForm
    template_name = 'accounts/student_edit.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self, queryset=None):
        return self.request.user.student

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        excluded_fields = ['password', 'confirm_password', 'photo', 'documents']
        for field_name in excluded_fields:
            if field_name in form.fields:
                del form.fields[field_name]

        user = self.request.user
        form.initial['username'] = user.username
        form.initial['email'] = user.email
        form.initial['first_name'] = user.first_name
        form.initial['last_name'] = user.last_name
        form.initial['date_of_birth'] = user.date_of_birth
        form.initial['faculty'] = user.student.faculty
        form.initial['study_year'] = user.student.study_year

        disabled_fields = ['username', 'first_name', 'last_name', 'date_of_birth', 'faculty', 'study_year']
        for field_name in disabled_fields:
            if field_name in form.fields:
                form.fields[field_name].disabled = True

        return form

    def form_valid(self, form):
        self.object = form.save(commit=False)

        # Handle clearing photo
        if 'clear_photo' in self.request.POST:
            if self.object.user.photo:
                self.object.user.photo.delete()

        # Handle updating photo
        if 'photo' in self.request.FILES:
            self.object.user.photo.save(
                self.request.FILES['photo'].name,
                ContentFile(self.request.FILES['photo'].read())
            )

        self.object.save()

        user = self.request.user
        user.email = form.cleaned_data['email']
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.date_of_birth = form.cleaned_data['date_of_birth']
        user.save()

        return HttpResponseRedirect(self.get_success_url())


class ServeDocumentView(View):
    def get(self, request, username, document_id):
        document = get_object_or_404(Document, user__username=username, pk=document_id)
        document_path = document.document.path
        if os.path.exists(document_path):
            with open(document_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(document_path)
                return response
        else:
            return HttpResponseNotFound("Document not found")


class ServePhotoView(View):
    def get(self, request, username):
        user = get_object_or_404(CustomUser, username=username)
        if user.photo:
            photo_path = user.photo.path
            if os.path.exists(photo_path):
                with open(photo_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='image/jpeg')
                    return response
        return HttpResponseNotFound("Photo not found")

