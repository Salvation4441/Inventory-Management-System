from .models import Activity

def notification_context(request):
    """Add notification count to all templates"""
    unread_count = 0
    if request.user.is_authenticated:
        unread_count = Activity.objects.filter(is_read=False).count()
    
    return {
        'notification_count': unread_count
    }