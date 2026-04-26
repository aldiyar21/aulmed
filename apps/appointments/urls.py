from django.urls import path

from . import views

urlpatterns = [
    path("my/create/", views.patient_appointment_create, name="patient-appointment-create"),
    path("my/", views.patient_appointment_list, name="patient-appointment-list"),
    path("my/<int:pk>/", views.patient_appointment_detail, name="patient-appointment-detail"),
    path("staff/", views.staff_appointment_list, name="staff-appointment-list"),
    path("staff/<int:pk>/", views.staff_appointment_detail, name="staff-appointment-detail"),
    path("staff/<int:pk>/edit/", views.staff_appointment_update, name="staff-appointment-update"),
    path("doctor/", views.doctor_appointment_list, name="doctor-appointment-list"),
]
