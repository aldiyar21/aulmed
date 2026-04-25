from django.urls import path

from . import views

urlpatterns = [
    path("", views.encounter_list, name="encounter-list"),
    path("create/", views.encounter_create, name="encounter-create"),
    path("export/", views.encounter_export_csv, name="encounter-export"),
    path("<int:pk>/edit/", views.encounter_update, name="encounter-update"),
]
