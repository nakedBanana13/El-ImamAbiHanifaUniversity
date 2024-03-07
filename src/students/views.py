from accounts.forms import StudentRegistrationForm
from accounts.models import Student
from braces.views import LoginRequiredMixin
from courses.models import Course
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView, ListView, DetailView


class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentRegistrationForm
    template_name = 'students/student_edit.html'
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


class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/dashboard.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user.student])


class StudentCourseDetailView(DetailView):
    model = Course
    template_name = 'students/course_details.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user.student])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get course object
        course = self.get_object()
        if 'module_id' in self.kwargs:
            # get current module
            context['module'] = course.modules.get(id=self.kwargs['module_id'])
        else:
            # get first module
            context['module'] = course.modules.all()[0]
        return context
