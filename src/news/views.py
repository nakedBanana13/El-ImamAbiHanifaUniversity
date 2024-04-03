from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, UpdateView, CreateView
from .models import NewsItem, Announcement


class NewsListView(ListView):
    model = NewsItem
    template_name = 'news/news_list.html'
    context_object_name = 'news_items'
    paginate_by = 13


def contact_us(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if email and message and subject:
            message += f"\n\nبريد المرسل: {email}"
            email_message = EmailMessage(
                subject,
                message,
                settings.EMAIL_HOST_USER,  # From
                [settings.EMAIL_HOST_USER],  # To
                reply_to=[email],
            )
            email_message.send(fail_silently=False)

            return render(request, 'news/email_recieved.html')
        else:
            return render(request, 'news/email_failed.html')
    return render(request, 'base.html')


class AnnouncementListView(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'announcement/list.html'
    context_object_name = 'announcements'

    def get_queryset(self):
        # Filter announcements based on the courses the instructor is teaching
        courses = self.request.user.instructor.courses_created.all()
        return Announcement.objects.filter(course__in=courses)


class AnnouncementCreateView(LoginRequiredMixin, CreateView):
    model = Announcement
    template_name = 'announcement/form.html'
    fields = ['course', 'content']
    success_url = reverse_lazy('announcement_list')

    def form_valid(self, form):
        form.instance.instructor = self.request.user.instructor
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['course'].queryset = self.request.user.instructor.courses_created.all()
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create_form'] = True
        return context


class AnnouncementUpdateView(LoginRequiredMixin, UpdateView):
    model = Announcement
    template_name = 'announcement/form.html'
    fields = ['course', 'content']
    success_url = reverse_lazy('announcement_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create_form'] = False
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['course'].queryset = self.request.user.instructor.courses_created.all()
        return form

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.instructor != self.request.user.instructor:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class AnnouncementDeleteView(LoginRequiredMixin, DeleteView):
    model = Announcement
    success_url = reverse_lazy('announcement_list')
    template_name = 'announcement/confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.instructor != self.request.user.instructor:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            return HttpResponseRedirect(self.success_url)
        else:
            return super().post(request, *args, **kwargs)