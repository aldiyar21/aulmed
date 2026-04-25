from django.urls import path

from . import views

urlpatterns = [
    path("", views.prevention_list, name="prevention-list"),
    path("create/", views.prevention_create, name="prevention-create"),
    path("overdue/", views.prevention_overdue, name="prevention-overdue"),
    path("export/", views.prevention_export_csv, name="prevention-export"),
    path("<int:pk>/edit/", views.prevention_update, name="prevention-update"),
]
