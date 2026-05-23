from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.home, name='home'),
    path('jobs/', views.job_list, name='list'),
    path('jobs/post/', views.post_job, name='post'),
    path('jobs/<slug:slug>/', views.job_detail, name='detail'),
    path('jobs/<int:job_id>/edit/', views.edit_job, name='edit'),
    path('jobs/<int:job_id>/delete/', views.delete_job, name='delete'),
]
