from accounts.models import Instructor
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.apps import apps
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count
from django.forms import modelform_factory, model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Course, Module, Content, Subject
from .forms import ModuleFormSet


class OwnerMixin(object):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user.instructor_profile)


class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user.instructor_profile
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
    model = Course  # used for querySets(used by all views)
    fields = ['faculty', 'subject', 'study_year', 'title', 'overview', 'is_active']  # The fields of the model to build the model form of the CreateView
    # and UpdateView views

    success_url = reverse_lazy('manage_course_list')  # redirect the user after the form is successfully submitted


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'

    def get_queryset(self):
        # Retrieve the instructor associated with the logged-in user
        instructor = self.request.user.instructor_profile

        # Filter courses by the instructor
        queryset = Course.objects.filter(owner=instructor)

        return queryset


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'

    def form_valid(self, form):
        # Assign the current user as the owner of the course
        if self.request.user.is_authenticated:
            user = self.request.user

            instructor = get_object_or_404(Instructor, user=user)

            course = form.save(commit=False)
            course.owner = instructor
            course.save()
            messages.success(self.request, 'تم إنشاء الدورة بنجاح.')
            return redirect('manage_course_list')
        else:
            # Redirect the user to the login page if they're not authenticated
            return redirect('login')


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'

    def get_initial(self):
        initial = super().get_initial()
        # Get the current instance of the course
        course_instance = self.get_object()
        # Convert the faculty instance to a dictionary
        faculty_dict = model_to_dict(course_instance.faculty)
        # Set the initial value for the faculty field
        initial['faculty'] = faculty_dict['id']
        return initial

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            user = self.request.user
            instructor = get_object_or_404(Instructor, user=user)

            course = form.save(commit=False)
            course.owner = instructor
            course.save()

            messages.success(self.request, 'تم تحديث الدورة بنجاح.')
            return super().form_valid(form)
        else:
            return redirect('login')


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف الدورة بنجاح.')
        return super().delete(request, *args, **kwargs)


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


class ModuleCreateView(CreateView):
    model = Module
    fields = ['title', 'description', 'is_active']
    template_name = 'courses/manage/module/module_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course_id'] = self.kwargs['pk']
        return context

    def form_valid(self, form):
        form.instance.course = Course.objects.get(pk=self.kwargs['pk'])
        messages.success(self.request, 'تم إنشاء الوحدة بنجاح.')
        return super().form_valid(form)

    def get_success_url(self):
        # If 'action' is 'save_and_add_another', redirect to the module create view again
        if self.request.POST.get('action') == 'save_and_add_another':
            return reverse_lazy('module_create', kwargs={'pk': self.kwargs['pk']})
        messages.success(self.request, 'تم إنشاء الوحدة بنجاح.')
        return reverse_lazy('course_module_update', kwargs={'pk': self.kwargs['pk']})


class CourseModuleUpdateView(TemplateResponseMixin, View):
    """handles adding, updating, and  deleting modules for a specific course"""
    template_name = 'courses/manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        ordered_modules = self.course.modules.order_by('order')
        return ModuleFormSet(instance=self.course, queryset=ordered_modules, data=data)

    """attempts to delegate to a lowercase method  that matches the HTTP method used. A GET request is delegated to the 
       get() method and a POST request to post() """
    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course, id=pk, owner=request.user.instructor_profile)
        return super().dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course,
                                        'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'تم حفظ التغييرات بنجاح.')
            return redirect('manage_course_list')
        messages.error(request, 'يرجى تصحيح الأخطاء في النموذج أدناه.')
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
        self.module = get_object_or_404(Module, id=module_id, course__owner=request.user.instructor_profile)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model, id=id, owner=request.user.instructor_profile)
        return super().dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj, 'module_id': module_id})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)

            #if model_name == 'file' or model_name == 'image':
            #    file_instance = obj  # Assuming 'obj' is the File instance
            #    course = self.module.course
            #    faculty_name = course.faculty.name
            #    subject_name = course.subject.title
            #    instructor_name = request.user.username
            #    # Generate the directory path
            #    directory_path = os.path.join(settings.MEDIA_ROOT, 'courses_files', faculty_name, subject_name, instructor_name, model_name + "s")
            #    # Ensure the directory exists
            #    os.makedirs(directory_path, exist_ok=True)
            #    # Get the filename and its extension
            #    base_name, extension = os.path.splitext(file_instance.file.name)
            #    # Slugify the base name and concatenate with the extension
            #    file_slug = f"{slugify(base_name)}{extension}"
            #    # Save the file to the appropriate directory
            #    file_path = os.path.join(directory_path, file_slug)
            #    with open(file_path, 'wb+') as destination:
            #        for chunk in file_instance.file.chunks():
            #            destination.write(chunk)
            obj.owner = request.user.instructor_profile
            obj.save()

            if not id:
                Content.objects.create(module=self.module, item=obj)
            messages.success(request, 'تم حفظ المحتوى بنجاح.')
            return redirect('module_content_list', self.module.id)
        messages.error(request, 'يرجى تصحيح الأخطاء في النموذج أدناه.')
        return self.render_to_response({'form': form, 'object': self.obj, 'module_id': module_id})


class ContentDeleteView(View):

    def post(self, request, id):
        content = get_object_or_404(Content, id=id, module__course__owner=request.user.instructor_profile)
        module = content.module
        content.item.delete()
        content.delete()
        messages.success(request, 'تم حذف المحتوى بنجاح.')
        return redirect('module_content_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module, id=module_id, course__owner=request.user.instructor_profile)
        return self.render_to_response({'module': module})


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id, course__owner=request.user.instructor).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id, module__course__owner=request.user.instructor_profile).update(order=order)
        return self.render_json_response({'saved': 'OK'})


def get_subjects_view(request):
    if request.method == 'GET' and 'faculty_id' in request.GET:
        faculty_id = request.GET.get('faculty_id')
        subjects = Subject.objects.filter(faculty_id=faculty_id)
        subjects_data = [{'id': subject.id, 'title': subject.title} for subject in subjects]
        return JsonResponse(subjects_data, safe=False)
    else:
        return JsonResponse({'error': 'Invalid request'})
