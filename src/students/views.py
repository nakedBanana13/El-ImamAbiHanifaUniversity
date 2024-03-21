from accounts.forms import StudentRegistrationForm
from accounts.models import Student
from braces.views import LoginRequiredMixin
from courses.models import Course, Module
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import UpdateView, ListView, DetailView


class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentRegistrationForm
    template_name = 'students/student_edit.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self, queryset=None):
        return self.request.user.student_profile

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        excluded_fields = ['password', 'confirm_password', 'certificate_photo', 'id_photo', 'qualification', 'username', 'first_name', 'father_name', 'last_name', 'date_of_birth', 'faculty', 'study_year', 'country_born', 'country_of_residence', 'language']
        for field_name in excluded_fields:
            if field_name in form.fields:
                del form.fields[field_name]

        user = self.request.user
        form.initial['username'] = user.username
        form.initial['photo'] = user.photo
        form.initial['first_name'] = user.first_name
        form.initial['father_name'] = user.student_profile.father_name
        form.initial['last_name'] = user.last_name
        form.initial['email'] = user.email
        form.initial['phone_number'] = user.student_profile.phone_number
        form.initial['date_of_birth'] = user.date_of_birth
        form.initial['faculty'] = user.student_profile.faculty
        form.initial['study_year'] = user.student_profile.study_year
        form.initial['country_born'] = user.student_profile.country_born
        form.initial['country_of_residence'] = user.student_profile.country_of_residence
        form.initial['language'] = user.student_profile.language

        disabled_fields = []
        for field_name in disabled_fields:
            if field_name in form.fields:
                form.fields[field_name].disabled = True

        return form

    def clean(self):
        cleaned_data = super().clean()
        disabled_fields = ['username', 'first_name', 'father_name', 'last_name', 'date_of_birth', 'faculty', 'study_year', 'country_born', 'country_of_residence', 'language']
        for field_name in disabled_fields:
            if field_name in cleaned_data:
                del cleaned_data[field_name]
        return cleaned_data

    def form_valid(self, form):
        self.object = form.save(commit=False)

        user = self.request.user
        user.email = form.cleaned_data['email']
        user.student_profile.phone_number = form.cleaned_data['phone_number']

        if 'photo' in self.request.FILES:
            # Delete old photo if it exists
            if user.photo:
                # Get the path of the old photo
                old_photo_path = user.photo.path
                # Delete the old photo from storage
                default_storage.delete(old_photo_path)

            user.photo.save(
                self.request.FILES['photo'].name,
                ContentFile(self.request.FILES['photo'].read())
            )

        user.save()

        messages.success(self.request, 'تم تحديث الملف الشخصي بنجاح.')
        return HttpResponseRedirect(self.get_success_url())


class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/dashboard.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user.student_profile], is_active=True)


class StudentCourseDetailView(DetailView):
    model = Course
    template_name = 'students/course_details.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user.student_profile])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get course object
        course = self.get_object()
        if 'module_id' in self.kwargs:
            # get current module
            context['module'] = get_object_or_404(Module, id=self.kwargs['module_id'], course=course, is_active=True)
        else:
            # get first active module
            context['module'] = course.modules.filter(is_active=True).first()
        return context