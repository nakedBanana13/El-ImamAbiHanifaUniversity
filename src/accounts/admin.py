from django.conf import settings
from django.contrib import admin
from django.core.mail import send_mail
from django.utils.html import format_html
from django.contrib.admin import ModelAdmin
from .models import Student, Instructor, CustomUser
from .forms import InstructorAdminForm


class BaseUserAdminMixin():
    list_display = ('get_first_name', 'get_last_name', 'get_email', 'get_username', 'get_date_of_birth', 'get_is_active', 'get_is_approved', 'view_photo_link')

    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = 'اسم المستخدم'

    def get_first_name(self, obj):
        return obj.user.first_name

    get_first_name.short_description = 'الاسم الأول'

    def get_last_name(self, obj):
        return obj.user.last_name

    get_last_name.short_description = 'الاسم الأخير'

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = 'البريد الإلكتروني'

    def view_photo_link(self, obj):
        if obj.user.photo:
            photo_url = obj.user.photo.url
            return format_html('<a href="{}" target="_blank">عرض الصورة</a>', photo_url)
        return "لا توجد صورة"

    view_photo_link.short_description = "الصورة الشخصية"

    def get_date_of_birth(self, obj):
        return obj.user.date_of_birth

    def get_is_active(self, obj):
        return obj.user.is_active if obj.user else False

    get_is_active.short_description = 'نشط '
    get_is_active.boolean = True

    def get_is_approved(self, obj):
        return obj.user.is_approved if obj.user else False

    get_is_approved.short_description = 'مُوافق عليه'
    get_is_approved.boolean = True

    get_date_of_birth.short_description = 'تاريخ الميلاد'


class UserActionMixin():
    def send_approval_email(self, user_email, subject, message):
        sender_email = settings.EMAIL_HOST_USER
        send_mail(subject, message, sender_email, [user_email])

    def make_approved(self, request, queryset):
        for obj in queryset:
            obj.user.is_approved = True
            obj.user.save()
            self.send_approval_email(obj.user.email, 'تمت الموافقة على حسابك', 'تمت الموافقة على حسابك. يمكنك الآن تسجيل الدخول.')

    make_approved.short_description = "تحديد كموافق عليه"

    def make_not_approved(self, request, queryset):
        for obj in queryset:
            obj.user.is_approved = False
            obj.user.save()

    make_not_approved.short_description = "تحديد كغير موافق عليه"

    def make_inactive(self, request, queryset):
        for obj in queryset:
            obj.user.is_active = False
            obj.user.save()
            self.send_approval_email(obj.user.email, 'تم إلغاء تنشيط حسابك', 'تم إلغاء تنشيط حسابك. لم يعد بإمكانك تسجيل الدخول.')

    make_inactive.short_description = "تحديد كغير نشط"

    def make_active(self, request, queryset):
        for obj in queryset:
            obj.user.is_active = True
            obj.user.save()
            self.send_approval_email(obj.user.email, 'تم تنشيط حسابك', 'تم تنشيط حسابك. يمكنك الآن تسجيل الدخول.')

    make_active.short_description = "تحديد كنشط"
    actions = ['make_approved', 'make_not_approved', 'make_inactive', 'make_active']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin, BaseUserAdminMixin, UserActionMixin):
    list_display = BaseUserAdminMixin.list_display + ('faculty', 'study_year', 'father_name', 'country_born','country_of_residence', 'phone_number', 'qualification', 'language', 'view_id_photo_link', 'view_certificate_link')
    list_filter = ('faculty', 'study_year', 'qualification', 'language', 'country_of_residence', 'user__is_active', 'user__is_approved')
    search_fields = ('phone_number', 'user__first_name', 'user__last_name', 'user__email', 'user__username')
    search_help_text = 'ابحث عن طالب عن طريق اسم المستخدم, الاسم, اللقب, البريد الالكتوني أو رقم الهاتف'
    actions = UserActionMixin.actions

    def view_id_photo_link(self, obj):
        if obj.user.photo:
            photo_url = obj.id_photo.url
            return format_html('<a href="{}" target="_blank">عرض الهوية</a>', photo_url)
        return "لا توجد هوية مثبتة"

    view_id_photo_link.short_description = "الهوية المثبتة"

    def view_certificate_link(self, obj):
        if obj.user.photo:
            photo_url = obj.certificate_photo.url
            return format_html('<a href="{}" target="_blank">عرض الشهادة</a>', photo_url)
        return "لا توجد شهادة"

    view_certificate_link.short_description = "المؤهل العلمي"


@admin.register(CustomUser)
class CustomUserAdmin(ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'username', 'date_of_birth', 'is_student', 'is_active', 'is_approved', 'view_photo_link')
    list_filter = ('is_active', 'is_approved', 'is_student')
    search_fields = ('first_name', 'last_name', 'email', 'username')
    search_help_text = 'ابحث عن طالب عن طريق اسم المستخدم, الاسم, اللقب أو البريد الالكتوني '

    def view_photo_link(self, obj):
        if obj.photo:
            photo_url = obj.photo.url
            return format_html('<a href="{}" target="_blank">عرض الصورة</a>', photo_url)
        return "لا توجد صورة"


@admin.register(Instructor)
class InstructorAdmin(ModelAdmin, BaseUserAdminMixin, UserActionMixin):
    list_display = BaseUserAdminMixin.list_display
    form = InstructorAdminForm
    actions = UserActionMixin.actions


#class ExtensionListFilter(admin.SimpleListFilter):
#    title = 'Extension'
#    parameter_name = 'extension'
#
#    def lookups(self, request, model_admin):
#        documents = Document.objects.exclude(document='').values_list('document', flat=True)
#        extensions = {doc.split('.')[-1] for doc in documents}
#        return [(ext, ext) for ext in extensions]
#
#    def queryset(self, request, queryset):
#        if self.value():
#            documents = Document.objects.exclude(document='').filter(document__endswith=f".{self.value()}")
#            document_ids = documents.values_list('id', flat=True)
#            return queryset.filter(id__in=document_ids)
#        return queryset


#@admin.register(Document)
#class DocumentAdmin(admin.ModelAdmin):
#    list_display = ('user', 'uploaded_at', 'view_document_link')
#    list_filter = (ExtensionListFilter, 'user')
#    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email', 'uploaded_at']
#    search_help_text = 'Search by first name, last name, email, username, uploaded date'
#
#    def view_document_link(self, obj):
#        if obj.document:
#            url = reverse('serve_document', kwargs={'username': obj.user.username, 'document_id': obj.id})
#            return format_html('<a href="{}">عرض المستند</a>', url)
#        return "لا يوجد مستند"
#
#    view_document_link.short_description = "رابط المستند"

