import logging
import os

from accounts.models import Instructor
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.apps import apps
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count
from django.forms import modelform_factory
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views.generic import DetailView
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Course, Module, Content, Subject
from .forms import ModuleFormSet


class OwnerMixin(object):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user.instructor)


class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user.instructor
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
    model = Course  # used for querySets(used by all views)
    fields = ['faculty', 'subject', 'study_year', 'title', 'overview']  # The fields of the model to build the model form of the CreateView
    # and UpdateView views

    success_url = reverse_lazy('manage_course_list')  # redirect the user after the form is successfully submitted


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'

    def get_queryset(self):
        # Retrieve the instructor associated with the logged-in user
        instructor = self.request.user.instructor

        # Filter courses by the instructor
        queryset = Course.objects.filter(owner=instructor)

        return queryset


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'

    def form_valid(self, form):
        # Assign the current user as the owner of the course
        if self.request.user.is_authenticated:
            user = self.request.user
            print(f"User '{user.username}' is authenticated.")

            instructor = get_object_or_404(Instructor, user=user)
            print(f"Retrieved Instructor instance for user '{user.username}'.")

            course = form.save(commit=False)
            course.owner = instructor
            course.save()
            print(f"Course saved with owner '{instructor.user.username}'.")

            return redirect('manage_course_list')
        else:
            # Redirect the user to the login page if they're not authenticated
            print("User is not authenticated. Redirecting to login page.")
            return redirect('login')


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'


class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'courses/course/list.html'

    def get(self, request, subject=None):
        subjects = Subject.objects.annotate(total_courses=Count('courses'))
        courses = Course.objects.annotate(total_modules=Count('modules'))
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            courses = courses.filter(subject=subject)
        return self.render_to_response({'subjects': subjects, 'subject': subject, 'courses': courses})


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'


class CourseModuleUpdateView(TemplateResponseMixin, View):
    """handles adding, updating, and  deleting modules for a specific course"""
    template_name = 'courses/manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)

    """attempts to delegate to a lowercase method  that matches the HTTP method used. A GET request is delegated to the 
       get() method and a POST request to post() """
    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course, id=pk, owner=request.user.instructor)
        return super().dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course,
                                        'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course': self.course, 'formset': formset})


class ContentCreateUpdateView(TemplateResponseMixin, View):
    """allows to create and update different models' contents"""
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):
        """checks that the given model name is one of the four content models"""
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses', model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner', 'order', 'created', 'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module, id=module_id, course__owner=request.user.instructor)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model, id=id, owner=request.user.instructor)
        return super().dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user.instructor
            obj.save()

            if model_name == 'file' or model_name == 'image':
                file_instance = obj  # Assuming 'obj' is the File instance
                course = self.module.course
                faculty_name = course.faculty.name
                subject_name = course.subject.title
                instructor_name = request.user.username
                # Generate the directory path
                directory_path = os.path.join(settings.MEDIA_ROOT, 'courses_files', faculty_name, subject_name, instructor_name, model_name + "s")
                # Ensure the directory exists
                os.makedirs(directory_path, exist_ok=True)
                # Get the filename and its extension
                base_name, extension = os.path.splitext(file_instance.file.name)
                # Slugify the base name and concatenate with the extension
                file_slug = f"{slugify(base_name)}{extension}"
                # Save the file to the appropriate directory
                file_path = os.path.join(directory_path, file_slug)
                with open(file_path, 'wb+') as destination:
                    for chunk in file_instance.file.chunks():
                        destination.write(chunk)

            if not id:
                Content.objects.create(module=self.module, item=obj)
            return redirect('module_content_list', self.module.id)

        return self.render_to_response({'form': form, 'object': self.obj})


class ContentDeleteView(View):

    def post(self, request, id):
        content = get_object_or_404(Content, id=id, module__course__owner=request.user.instructor)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module, id=module_id, course__owner=request.user.instructor)
        return self.render_to_response({'module': module})


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id, course__owner=request.user.instructor).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id, module__course__owner=request.user.instructor).update(order=order)
        return self.render_json_response({'saved': 'OK'})
