from os.path import basename
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.admin import ModelAdmin
from django.utils.safestring import mark_safe
from .models import CustomUser, Student, Instructor, Document
from accounts.forms import InstructorAdminForm


@admin.register(Document)
class DocumentAdmin(ModelAdmin):
    list_display = ('user', 'uploaded_at', 'view_document_link')

    def view_document_link(self, obj):
        if obj.document:
            url = reverse('serve_document', kwargs={'username': obj.user.username, 'document_id': obj.id})
            return format_html('<a href="{}">View Document</a>', url)
        return "No document"
    view_document_link.short_description = "Document Link"


@admin.register(CustomUser)
class CustomUserAdmin(ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'username', 'date_of_birth', 'is_active', 'is_approved', 'view_photo_link')

    def view_photo_link(self, obj):
        if obj.photo:
            url = reverse('serve_photo', kwargs={'username': obj.username})
            return format_html('<a href="{}">View Photo</a>', url)
        return "No photo"
    view_photo_link.short_description = "Photo Link"


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('get_first_name', 'get_last_name', 'get_email', 'get_username', 'get_date_of_birth', 'faculty',
                    'study_year', 'get_is_active', 'get_is_approved', 'view_photo_link', 'view_documents')
    list_filter = ('faculty', 'study_year', 'user__is_active', 'user__is_approved')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')

    def get_username(self, obj):
        return obj.user.username

    get_username.allow_tags = False
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

    def make_approved(self, request, queryset):
        for student in queryset:
            student.user.is_approved = True
            student.user.save()

    make_approved.short_description = "Mark selected students as approved"

    def make_not_approved(self, request, queryset):
        for student in queryset:
            student.user.is_approved = False
            student.user.save()

    make_not_approved.short_description = "Mark selected students as not approved"

    def make_inactive(self, request, queryset):
        for student in queryset:
            student.user.is_active = False
            student.user.save()

    make_inactive.short_description = "Mark selected students as inactive"

    def make_active(self, request, queryset):
        for student in queryset:
            student.user.is_active = True
            student.user.save()

    make_active.short_description = "Mark selected students as active"

    actions = [make_approved, make_inactive, make_active]


@admin.register(Instructor)
class InstructorAdmin(ModelAdmin):
    form = InstructorAdminForm
    list_display = ('get_first_name', 'get_last_name', 'get_email', 'get_username', 'get_date_of_birth', 'get_is_active', 'get_is_approved', 'view_photo_link')

    def get_username(self, obj):
        return obj.user.username

    get_username.allow_tags = False
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
