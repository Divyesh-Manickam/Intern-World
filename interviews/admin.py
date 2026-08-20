from django.contrib import admin
from .models import Interview


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('student', 'recruiter', 'interview_date', 'interview_time', 'interview_type', 'status', 'created_at')
    list_filter = ('interview_type', 'status', 'interview_date')
    search_fields = ('student__email', 'recruiter__email', 'application__opportunity__title')
