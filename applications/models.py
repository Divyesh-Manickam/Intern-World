from django.db import models
from django.conf import settings
from opportunities.models import Opportunity


class Application(models.Model):
    class Status(models.TextChoices):
        APPLIED = 'APPLIED', 'Applied'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        SHORTLISTED = 'SHORTLISTED', 'Shortlisted'
        INTERVIEW_SCHEDULED = 'INTERVIEW_SCHEDULED', 'Interview Scheduled'
        SELECTED = 'SELECTED', 'Selected'
        REJECTED = 'REJECTED', 'Rejected'
        WITHDRAWN = 'WITHDRAWN', 'Withdrawn'

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    resume = models.FileField(
        upload_to='application_resumes/',
        blank=True,
        null=True
    )
    cover_letter = models.TextField(blank=True, default='')
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.APPLIED
    )
    recruiter_notes = models.TextField(
        blank=True,
        default='',
        help_text='Internal recruiter feedback/evaluation notes'
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_at']
        unique_together = ('student', 'opportunity')
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['applied_at']),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.opportunity.title} ({self.get_status_display()})"

    @property
    def badge_color(self):
        mapping = {
            self.Status.APPLIED: 'primary',
            self.Status.UNDER_REVIEW: 'info',
            self.Status.SHORTLISTED: 'warning',
            self.Status.INTERVIEW_SCHEDULED: 'purple',
            self.Status.SELECTED: 'success',
            self.Status.REJECTED: 'danger',
            self.Status.WITHDRAWN: 'secondary',
        }
        return mapping.get(self.status, 'secondary')
