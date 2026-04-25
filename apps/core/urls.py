from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard_redirect, name="home"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("notifications/<int:pk>/read/", views.mark_notification_read, name="notification-read"),
]
