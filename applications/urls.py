from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('apply/<int:pk>/', views.apply_opportunity, name='apply'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('my-applications/<int:pk>/', views.application_detail, name='application_detail'),
    path('my-applications/<int:pk>/withdraw/', views.withdraw_application, name='withdraw'),
]
