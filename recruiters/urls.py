from django.urls import path
from . import views

app_name = 'recruiters'

urlpatterns = [
    path('jobs/', views.my_jobs, name='my_jobs'),
    path('jobs/<int:job_id>/applicants/', views.job_applicants, name='job_applicants'),
    path('applicants/', views.all_applicants, name='all_applicants'),
    path('applications/<int:app_id>/', views.application_detail, name='application_detail'),
    path('applications/<int:app_id>/update-status/', views.update_application_status, name='update_application_status'),
]
