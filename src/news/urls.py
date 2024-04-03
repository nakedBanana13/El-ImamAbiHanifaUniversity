from django.urls import path
from .views import NewsListView, AnnouncementListView, AnnouncementCreateView, AnnouncementUpdateView, \
    AnnouncementDeleteView

urlpatterns = [
    path('', NewsListView.as_view(), name='news_list'),
    path('announcements/', AnnouncementListView.as_view(), name='announcement_list'),
    path('announcements/create/', AnnouncementCreateView.as_view(), name='announcement_create'),
    path('announcements/<int:pk>/update/', AnnouncementUpdateView.as_view(), name='announcement_update'),
    path('announcements/<int:pk>/delete/', AnnouncementDeleteView.as_view(), name='announcement_delete'),
]