from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/users/', views.admin_manage_users, name='admin_users'),
    path('admin-dashboard/users/<int:pk>/toggle-status/', views.admin_toggle_user_status, name='toggle_user_status'),
    path('admin-dashboard/companies/', views.admin_manage_companies, name='admin_companies'),
    path('admin-dashboard/companies/<int:pk>/verify/', views.admin_verify_company, name='verify_company'),
    path('admin-dashboard/companies/<int:pk>/reject/', views.admin_reject_company, name='reject_company'),
    path('admin-dashboard/opportunities/', views.admin_manage_opportunities, name='admin_opportunities'),
    path('admin-dashboard/opportunities/<int:pk>/approve/', views.admin_approve_opportunity, name='approve_opportunity'),
    path('admin-dashboard/opportunities/<int:pk>/reject/', views.admin_reject_opportunity, name='reject_opportunity'),
    path('admin-dashboard/applications/', views.admin_manage_applications, name='admin_applications'),
    path('admin-dashboard/analytics/', views.admin_analytics, name='analytics_view'),
]
