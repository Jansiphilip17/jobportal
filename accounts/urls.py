from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/candidate/', views.register_candidate, name='register_candidate'),
    path('register/recruiter/', views.register_recruiter, name='register_recruiter'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    path('settings/', views.profile_settings, name='profile_settings'),
    path('change-password/', views.change_password, name='change_password'),
]
