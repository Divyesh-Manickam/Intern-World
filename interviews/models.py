from django.db import models
from django.conf import settings
from applications.models import Application


class Interview(models.Model):
    class InterviewType(models.TextChoices):
        ONLINE = 'ONLINE', 'Online Video Call'
        OFFLINE = 'OFFLINE', 'In-Person / On-Site'
        PHONE = 'PHONE', 'Telephonic'

    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='interviews'
    )
    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='scheduled_interviews'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interviews'
    )
    interview_date = models.DateField()
    interview_time = models.TimeField()
    interview_type = models.CharField(
        max_length=20,
        choices=InterviewType.choices,
        default=InterviewType.ONLINE
    )
    meeting_link = models.URLField(blank=True, default='', help_text='e.g., Google Meet, Zoom, MS Teams')
    location = models.CharField(max_length=255, blank=True, default='', help_text='Physical office or room location')
    instructions = models.TextField(blank=True, default='', help_text='Preparation instructions, requirements, agenda')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['interview_date', 'interview_time']
        verbose_name = 'Interview'
        verbose_name_plural = 'Interviews'

    def __str__(self):
        return f"Interview for {self.student.get_full_name()} - {self.application.opportunity.title} on {self.interview_date}"
