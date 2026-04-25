from django.urls import path

from . import views

urlpatterns = [
    path("", views.patient_list, name="patient-list"),
    path("create/", views.patient_create, name="patient-create"),
    path("export/", views.patient_export_csv, name="patient-export"),
    path("<int:pk>/", views.patient_detail, name="patient-detail"),
    path("<int:pk>/edit/", views.patient_update, name="patient-update"),
]
