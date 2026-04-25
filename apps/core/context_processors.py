from django.conf import settings

from apps.accounts.services import get_user_role_names
from apps.core.models import Notification


def app_context(request):
    if not request.user.is_authenticated:
        return {"APP_NAME": settings.APP_NAME}
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
    return {
        "APP_NAME": settings.APP_NAME,
        "user_role_names": get_user_role_names(request.user),
        "unread_notifications": unread_notifications,
    }
