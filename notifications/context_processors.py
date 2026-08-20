from .models import Notification


def unread_notifications_count(request):
    """
    Context processor to inject unread notification count and latest 5 unread notifications.
    """
    if request.user.is_authenticated:
        unread_qs = Notification.objects.filter(user=request.user, is_read=False)
        return {
            'unread_notifications_count': unread_qs.count(),
            'recent_unread_notifications': unread_qs[:5]
        }
    return {
        'unread_notifications_count': 0,
        'recent_unread_notifications': []
    }
