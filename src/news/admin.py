from django.contrib import admin
from .models import NewsItem, Announcement

admin.site.register(NewsItem)


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('course', 'instructor', 'content', 'created_at')
    list_filter = ('course', 'created_at')
    date_hierarchy = 'created_at'

admin.site.register(Announcement, AnnouncementAdmin)
