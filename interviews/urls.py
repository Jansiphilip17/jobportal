from django.urls import path
from . import views

app_name = 'interviews'

urlpatterns = [
    path('schedule/<int:app_id>/', views.schedule_interview, name='schedule'),
]
