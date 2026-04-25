from django.urls import path

from . import views

urlpatterns = [
    path("my/", views.patient_vital_reading_list, name="patient-vital-reading-list"),
    path("my/create/", views.patient_vital_reading_create, name="patient-vital-reading-create"),
    path("patient/<int:patient_pk>/", views.staff_patient_vital_list, name="staff-patient-vital-list"),
    path("patient/<int:patient_pk>/create/", views.staff_patient_vital_create, name="staff-patient-vital-create"),
]
