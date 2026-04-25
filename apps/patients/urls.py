from django.urls import path

from . import views

urlpatterns = [
    path("", views.patient_list, name="patient-list"),
    path("create/", views.patient_create, name="patient-create"),
    path("export/", views.patient_export_csv, name="patient-export"),
    path("my/dashboard/", views.patient_dashboard, name="patient-dashboard"),
    path("my/profile/", views.patient_profile, name="patient-profile"),
    path("my/chart/", views.patient_chart, name="patient-chart"),
    path("my/encounters/", views.patient_encounter_history, name="patient-encounters"),
    path("my/referrals/", views.patient_referral_history, name="patient-referrals"),
    path("<int:pk>/", views.patient_detail, name="patient-detail"),
    path("<int:pk>/edit/", views.patient_update, name="patient-update"),
]
