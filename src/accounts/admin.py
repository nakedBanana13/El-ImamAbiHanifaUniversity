from os.path import basename

from django.conf import settings
from django.contrib import admin
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.admin import ModelAdmin
from django.utils.safestring import mark_safe
from .models import CustomUser, Student, Instructor, Document
from .forms import InstructorAdminForm


class BaseUserAdminMixin():
    list_display = ('get_first_name', 'get_last_name', 'get_email', 'get_username', 'get_date_of_birth', 'get_is_active', 'get_is_approved', 'view_photo_link')

    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = 'Username'

    def get_first_name(self, obj):
        return obj.user.first_name

    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.user.last_name

    get_last_name.short_description = 'Last Name'

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = 'Email'

    def view_photo_link(self, obj):
        if obj.user.photo:
            url = reverse('serve_photo', kwargs={'username': obj.user.username})
            return format_html('<a href="{}">View Photo</a>', url)
        return "No photo"

    view_photo_link.short_description = "Photo Link"

    def get_date_of_birth(self, obj):
        return obj.user.date_of_birth

    def get_is_active(self, obj):
        return obj.user.is_active if obj.user else False

    get_is_active.short_description = 'Is Active ?'
    get_is_active.boolean = True

    def get_is_approved(self, obj):
        return obj.user.is_approved if obj.user else False

    get_is_approved.short_description = 'Is Approved ?'
    get_is_approved.boolean = True

    get_date_of_birth.short_description = 'Date of Birth'


class UserActionMixin():
    def send_approval_email(self, user_email, subject, message):
        sender_email = settings.EMAIL_HOST_USER
        send_mail(subject, message, sender_email, [user_email])

    def make_approved(self, request, queryset):
        for obj in queryset:
            obj.user.is_approved = True
            obj.user.save()
            self.send_approval_email(obj.user.email, 'Your account has been approved', 'Your account has been approved. You can now login.')

    make_approved.short_description = "Mark selected as approved"

    def make_not_approved(self, request, queryset):
        for obj in queryset:
            obj.user.is_approved = False
            obj.user.save()

    make_not_approved.short_description = "Mark selected as not approved"

    def make_inactive(self, request, queryset):
        for obj in queryset:
            obj.user.is_active = False
            obj.user.save()
            self.send_approval_email(obj.user.email, 'Your account has been deactivated', 'Your account has been deactivated. You can no longer login.')


    make_inactive.short_description = "Mark selected as inactive"

    def make_active(self, request, queryset):
        for obj in queryset:
            obj.user.is_active = True
            obj.user.save()
            self.send_approval_email(obj.user.email, 'Your account has been activated', 'Your account has been deactivated. You can now login.')


    make_active.short_description = "Mark selected as active"
    actions = ['make_approved', 'make_not_approved', 'make_inactive', 'make_active']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin, BaseUserAdminMixin, UserActionMixin):
    list_display = BaseUserAdminMixin.list_display + ('faculty', 'study_year', 'view_documents')
    list_filter = ('faculty', 'study_year', 'user__is_active', 'user__is_approved')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    search_help_text = 'Search by first name, last name, email'
    actions = UserActionMixin.actions

    def view_documents(self, obj):
        documents = Document.objects.filter(user=obj.user)
        if documents.exists():
            document_list = ['<li><a href="{}">{}</a></li>'.format(
                reverse('serve_document', kwargs={'username': obj.user.username, 'document_id': doc.id}),
                basename(doc.document.name)
            ) for doc in documents]
            return mark_safe('<ul>{}</ul>'.format(''.join(document_list)))
        else:
            return "No documents"

    view_documents.short_description = "Documents"


#@admin.register(CustomUser)
#class CustomUserAdmin(ModelAdmin):
#    list_display = ('id', 'first_name', 'last_name', 'email', 'username', 'date_of_birth', 'is_student', 'is_active', 'is_approved', 'view_photo_link')
#    list_filter = ('is_active', 'is_approved', 'is_student')
#    search_fields = ('first_name', 'last_name', 'email', 'username')
#    search_help_text = 'Search by first name, last name, email, username'
#
#    def view_photo_link(self, obj):
#        if obj.photo:
#            url = reverse('serve_photo', kwargs={'username': obj.username})
#            return format_html('<a href="{}">View Photo</a>', url)
#        return "No photo"
#
#    view_photo_link.short_description = "Photo Link"


@admin.register(Instructor)
class InstructorAdmin(ModelAdmin, BaseUserAdminMixin, UserActionMixin):
    list_display = BaseUserAdminMixin.list_display
    form = InstructorAdminForm
    actions = UserActionMixin.actions


class ExtensionListFilter(admin.SimpleListFilter):
    title = 'Extension'
    parameter_name = 'extension'

    def lookups(self, request, model_admin):
        documents = Document.objects.exclude(document='').values_list('document', flat=True)
        extensions = {doc.split('.')[-1] for doc in documents}
        return [(ext, ext) for ext in extensions]

    def queryset(self, request, queryset):
        if self.value():
            documents = Document.objects.exclude(document='').filter(document__endswith=f".{self.value()}")
            document_ids = documents.values_list('id', flat=True)
            return queryset.filter(id__in=document_ids)
        return queryset


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'uploaded_at', 'view_document_link')
    list_filter = (ExtensionListFilter, 'user')
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email', 'uploaded_at']
    search_help_text = 'Search by first name, last name, email, username, uploaded date'

    def view_document_link(self, obj):
        if obj.document:
            url = reverse('serve_document', kwargs={'username': obj.user.username, 'document_id': obj.id})
            return format_html('<a href="{}">View Document</a>', url)
        return "No document"

    view_document_link.short_description = "Document Link"
