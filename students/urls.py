from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('profile/', views.student_profile, name='profile'),
    path('profile/edit/', views.StudentProfileEditView.as_view(), name='edit_profile'),
    path('profile/upload-resume/', views.upload_resume, name='upload_resume'),
    path('projects/add/', views.add_project, name='add_project'),
    path('projects/<int:pk>/delete/', views.delete_project, name='delete_project'),
    path('certifications/add/', views.add_certification, name='add_certification'),
    path('certifications/<int:pk>/delete/', views.delete_certification, name='delete_certification'),
    path('experiences/add/', views.add_experience, name='add_experience'),
    path('experiences/<int:pk>/delete/', views.delete_experience, name='delete_experience'),
    path('saved/', views.saved_opportunities, name='saved_opportunities'),
    path('saved/<int:pk>/toggle/', views.toggle_save_opportunity, name='toggle_save'),
]
