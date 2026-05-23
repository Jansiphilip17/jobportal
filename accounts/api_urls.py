from django.urls import path
from .api_views import CandidateRegisterAPIView, RecruiterRegisterAPIView, CurrentUserAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/candidate/', CandidateRegisterAPIView.as_view()),
    path('register/recruiter/', RecruiterRegisterAPIView.as_view()),
    path('me/', CurrentUserAPIView.as_view()),
    path('token/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
]
