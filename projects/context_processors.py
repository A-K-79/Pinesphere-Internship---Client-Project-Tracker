from .models import Notification

def user_notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:20]
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {
            'notifications': notifications,
            'unread_notifications_count': unread_count,
        }
    return {
        'notifications': [],
        'unread_notifications_count': 0,
    }
