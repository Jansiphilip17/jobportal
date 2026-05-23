from .models import Notification


def notifications_processor(request):
    if request.user.is_authenticated:
        unread = Notification.objects.filter(recipient=request.user, is_read=False).count()
        recent = Notification.objects.filter(recipient=request.user)[:5]
        return {
            'unread_notifications_count': unread,
            'recent_notifications': recent,
        }
    return {}
