from django.urls import path
from . import views

app_name = 'candidates'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('resume/', views.manage_resume, name='resume'),
    path('skills/add/', views.add_skill, name='add_skill'),
    path('skills/<int:skill_id>/delete/', views.delete_skill, name='delete_skill'),
    path('education/add/', views.add_education, name='add_education'),
    path('education/<int:edu_id>/edit/', views.edit_education, name='edit_education'),
    path('education/<int:edu_id>/delete/', views.delete_education, name='delete_education'),
    path('experience/add/', views.add_experience, name='add_experience'),
    path('experience/<int:exp_id>/edit/', views.edit_experience, name='edit_experience'),
    path('experience/<int:exp_id>/delete/', views.delete_experience, name='delete_experience'),
    path('saved-jobs/', views.saved_jobs, name='saved_jobs'),
]
