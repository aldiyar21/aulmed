from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_visit_list, name="visit-list"),
    path("create/", views.home_visit_create, name="visit-create"),
    path("today/", views.home_visit_today, name="visit-today"),
    path("<int:pk>/edit/", views.home_visit_update, name="visit-update"),
]
