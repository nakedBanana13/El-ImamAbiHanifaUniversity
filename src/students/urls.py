from django.urls import path
from .views import StudentUpdateView, StudentCourseListView, StudentCourseDetailView

urlpatterns = [
    path('edit/', StudentUpdateView.as_view(), name='student_edit'),
    path('dashboard/', StudentCourseListView.as_view(), name='dashboard'),
    path('course/<int:pk>', StudentCourseDetailView.as_view(), name='student_course_details'),
    path('course/<int:pk>/<int:module_id>/', StudentCourseDetailView.as_view(),
         name='student_course_details_module'),
]
