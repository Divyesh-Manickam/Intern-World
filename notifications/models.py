from django.db import models
from django.conf import settings


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        APPLICATION = 'APPLICATION', 'Application Update'
        INTERVIEW = 'INTERVIEW', 'Interview Update'
        OPPORTUNITY = 'OPPORTUNITY', 'Opportunity Alert'
        SYSTEM = 'SYSTEM', 'System Notification'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )
    link_url = models.CharField(max_length=255, blank=True, default='')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"Notification for {self.user.email}: {self.title}"

    @property
    def icon_class(self):
        mapping = {
            self.NotificationType.APPLICATION: 'bi-briefcase',
            self.NotificationType.INTERVIEW: 'bi-calendar-event',
            self.NotificationType.OPPORTUNITY: 'bi-stars',
            self.NotificationType.SYSTEM: 'bi-info-circle',
        }
        return mapping.get(self.notification_type, 'bi-bell')
