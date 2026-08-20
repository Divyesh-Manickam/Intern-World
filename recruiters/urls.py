from django.urls import path
from . import views

app_name = 'recruiters'

urlpatterns = [
    path('dashboard/', views.recruiter_dashboard, name='dashboard'),
    path('company/', views.company_profile, name='company_profile'),
    path('company/edit/', views.CompanyEditView.as_view(), name='edit_company'),
    path('applicants/', views.applicant_management, name='applicants'),
    path('applicants/<int:pk>/', views.applicant_detail, name='applicant_detail'),
    path('applicants/<int:pk>/update-status/', views.update_applicant_status, name='update_status'),
]
