from .views import StudentRegistrationView, RegistrationDoneView, CustomLoginView
from django.urls import path
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('register/', StudentRegistrationView.as_view(), name='register'),
    path('registration/done/', RegistrationDoneView.as_view(), name='registration_done'),
    #path('dashboard/', StudentCourseListView.as_view(), name='dashboard'),
]
