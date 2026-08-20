from django.urls import path
from . import views

app_name = 'opportunities'

urlpatterns = [
    path('', views.landing_page, name='home'),
    path('about/', views.about_page, name='about'),
    path('opportunities/', views.opportunity_list, name='list'),
    path('opportunities/create/', views.create_opportunity, name='create'),
    path('opportunities/my/', views.my_opportunities, name='my_opportunities'),
    path('opportunities/<int:pk>/', views.opportunity_detail, name='detail'),
    path('opportunities/<int:pk>/edit/', views.edit_opportunity, name='edit'),
    path('opportunities/<int:pk>/close/', views.close_opportunity, name='close'),
    path('opportunities/<int:pk>/delete/', views.delete_opportunity, name='delete'),
]
