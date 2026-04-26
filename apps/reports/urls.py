from django.urls import path

from . import views

urlpatterns = [
    path("", views.reports_view, name="reports"),
    path("telemedicine/", views.telemedicine_reports_view, name="telemedicine-reports"),
]
