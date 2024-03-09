"""
URL configuration for ElImamAbiHanifaUniversity project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from accounts.views import ServeDocumentView, ServePhotoView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from courses.views import CourseListView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('accounts.urls')),
    path('course/', include('courses.urls')),
    path('student/', include('students.urls')),
    path('exam/', include('exams.urls')),
    path('documents/<str:username>/<int:document_id>/', ServeDocumentView.as_view(), name='serve_document'),
    path('<str:username>/profile_pic/', ServePhotoView.as_view(), name='serve_photo'),
    path('', CourseListView.as_view(), name='course_list'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)