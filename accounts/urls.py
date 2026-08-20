from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/student/', views.StudentRegisterView.as_view(), name='register_student'),
    path('register/recruiter/', views.RecruiterRegisterView.as_view(), name='register_recruiter'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
]
