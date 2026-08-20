import logging
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification

logger = logging.getLogger(__name__)


def create_notification(user, title, message, notification_type=Notification.NotificationType.SYSTEM, link_url='', send_email_alert=True):
    """
    Creates an in-app notification record and optionally dispatches an email notification.
    """
    try:
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            link_url=link_url
        )
    except Exception as e:
        logger.error(f"Failed to create database notification for user {user.id}: {e}")
        notification = None

    if send_email_alert and user.email:
        try:
            subject = f"[InternWorld] {title}"
            email_body = f"Hello {user.get_full_name() or user.username},\n\n{message}\n\n"
            if link_url:
                email_body += f"View details on InternWorld: {link_url}\n\n"
            email_body += "Best regards,\nThe InternWorld Placement Team"

            send_mail(
                subject=subject,
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True
            )
        except Exception as e:
            logger.warning(f"Failed to send email notification to {user.email}: {e}")

    return notification
