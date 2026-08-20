from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages

from .models import Notification


@login_required
def notification_list(request):
    """
    Shows all notifications for the user with pagination and filter for unread.
    """
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    unread_only = request.GET.get('unread')
    if unread_only == 'true':
        notifications = notifications.filter(is_read=False)

    return render(request, 'notifications/notifications_list.html', {
        'notifications': notifications,
        'unread_only': unread_only == 'true',
    })


@login_required
def mark_notification_as_read(request, pk):
    """
    Marks a single notification as read.
    """
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'is_read': True})

    if notification.link_url:
        return redirect(notification.link_url)
    return redirect('notifications:list')


@login_required
def mark_all_notifications_as_read(request):
    """
    Marks all notifications for current user as read.
    """
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect('notifications:list')


@login_required
def unread_count_api(request):
    """
    Quick API for AJAX notification count polling.
    """
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})
