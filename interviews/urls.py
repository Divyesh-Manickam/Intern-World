from django.urls import path
from . import views

app_name = 'interviews'

urlpatterns = [
    path('', views.interview_list, name='interview_list'),
    path('schedule/<int:application_id>/', views.schedule_interview, name='schedule'),
    path('<int:pk>/cancel/', views.cancel_interview, name='cancel'),
]
