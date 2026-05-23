from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    path('', views.company_list, name='list'),
    path('my-company/', views.my_company, name='my_company'),
    path('create/', views.create_company, name='create'),
    path('<slug:slug>/', views.company_detail, name='detail'),
]
