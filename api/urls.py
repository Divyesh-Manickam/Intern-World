from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'opportunities', views.OpportunityViewSet, basename='api_opportunity')
router.register(r'applications', views.ApplicationViewSet, basename='api_application')
router.register(r'interviews', views.InterviewViewSet, basename='api_interview')
router.register(r'notifications', views.NotificationViewSet, basename='api_notification')

urlpatterns = [
    path('auth/user/', views.CurrentUserAPIView.as_view(), name='api_current_user'),
    path('students/profile/', views.StudentProfileAPIView.as_view(), name='api_student_profile'),
    path('recommendations/', views.RecommendationsAPIView.as_view(), name='api_recommendations'),
    path('admin/stats/', views.AdminStatsAPIView.as_view(), name='api_admin_stats'),
    path('', include(router.urls)),
]
