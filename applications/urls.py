from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('apply/<slug:slug>/', views.apply_job, name='apply'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('withdraw/<int:app_id>/', views.withdraw_application, name='withdraw'),
    path('save-job/<int:job_id>/', views.save_job, name='save_job'),
]
