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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from news.views import contact_us

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('accounts.urls')),
    path('course/', include('courses.urls')),
    path('student/', include('students.urls')),
    path('exam/', include('exams.urls')),
    path('chat/', include('chat.urls', namespace='chat')),
    path('news/', include('news.urls')),
    #path('documents/<str:username>/<int:document_id>/', ServeDocumentView.as_view(), name='serve_document'),
    #path('<str:username>/profile_pic/', ServePhotoView.as_view(), name='serve_photo'),
    #path('', CourseListView.as_view(), name='course_list'),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('university_management/', TemplateView.as_view(template_name='management/university_management.html'), name='university_management'),
    path('university_management/dr_osama_abrash', TemplateView.as_view(template_name='management/dr_osama_abrash.html'), name='dr_osama_abrash'),
    path('university_management/dr_shafeek_aldeen_alsalah', TemplateView.as_view(template_name='management/dr_shafeek.html'), name='dr_shafeek_aldeen_alsalah'),
    path('university_management/dr_daher_alhamood', TemplateView.as_view(template_name='management/dr_daher_alhamood.html'), name='dr_daher_alhamood'),
    path('university_management/dr_ammar_bazerbashi', TemplateView.as_view(template_name='management/dr_ammar_bazerbashi.html'), name='dr_ammar_bazerbashi'),
    path('university_management/dr_mouaffak_almohemeed', TemplateView.as_view(template_name='management/dr_mouaffak_almohemeed.html'), name='dr_mouaffak_almohemeed'),
    path('manahej/', TemplateView.as_view(template_name='eulum/manahej.html'), name='manahej'),
    path('eulum/shareia/seera', TemplateView.as_view(template_name='eulum/shareia/seera.html'), name='seera'),
    path('eulum/shareia/quran', TemplateView.as_view(template_name='eulum/shareia/quran.html'), name='quran'),
    path('eulum/shareia/qera2at', TemplateView.as_view(template_name='eulum/shareia/qera2at.html'), name='qera2at'),
    path('eulum/shareia/fekh_mok', TemplateView.as_view(template_name='eulum/shareia/fekh_mok.html'), name='fekh_mok'),
    path('eulum/shareia/fekh_osoul', TemplateView.as_view(template_name='eulum/shareia/fekh_&_osoul.html'), name='fekh_&_osoul'),
    path('eulum/shareia/da3wa', TemplateView.as_view(template_name='eulum/shareia/da3wa.html'), name='da3wa'),
    path('eulum/shareia/8ada2', TemplateView.as_view(template_name='eulum/shareia/8ada2.html'), name='8ada2'),
    path('eulum/shareia/7adeeth', TemplateView.as_view(template_name='eulum/shareia/7adeeth.html'), name='7adeeth'),
    path('eulum/shareia/3akaed', TemplateView.as_view(template_name='eulum/shareia/3akaed.html'), name='3akaed'),
    path('eulum/shareia/derasat', TemplateView.as_view(template_name='eulum/shareia/derasat.html'), name='derasat'),
    path('eulum/arabia/na7o', TemplateView.as_view(template_name='eulum/arabia/na7o.html'), name='na7o'),
    path('eulum/arabia/balagha', TemplateView.as_view(template_name='eulum/arabia/bala3\'a.html'), name='balagha'),
    path('contact/', contact_us, name='contact_us'),
    path('under_construction/', TemplateView.as_view(template_name='under_construction.html'), name='under_construction'),
    path('who_are_we/', TemplateView.as_view(template_name='who_are_we.html'), name='who_are_we'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)