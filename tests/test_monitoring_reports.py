import pytest
from django.urls import reverse

from apps.monitoring.models import VitalReading


@pytest.mark.django_db
def test_patient_can_create_own_vital_reading(authed_client, patient_user, linked_patient):
    authed_client.login(username=patient_user.username, password="demo12345")
    response = authed_client.post(
        reverse("patient-vital-reading-create"),
        {
            "recorded_at": "2026-04-20T10:00",
            "systolic_bp": 120,
            "diastolic_bp": 80,
            "pulse": 72,
            "temperature": 36.6,
            "spo2": 98,
            "glucose": 5.5,
            "weight": 70,
            "comment": "Домашнее измерение",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert VitalReading.objects.filter(patient=linked_patient).exists()


@pytest.mark.django_db
def test_doctor_can_view_patient_vital_readings(authed_client, clinician_user, linked_patient):
    VitalReading.objects.create(
        patient=linked_patient,
        recorded_by=clinician_user,
        source="doctor_manual",
        recorded_at="2026-04-20T10:00:00Z",
        systolic_bp=120,
    )
    authed_client.login(username=clinician_user.username, password="demo12345")
    response = authed_client.get(reverse("staff-patient-vital-list", args=[linked_patient.pk]))
    assert response.status_code == 200


@pytest.mark.django_db
def test_telemedicine_report_returns_200_for_manager_and_admin(
    authed_client, manager_user, admin_user
):
    authed_client.login(username=manager_user.username, password="demo12345")
    response = authed_client.get(reverse("telemedicine-reports"))
    assert response.status_code == 200
    authed_client.logout()
    authed_client.login(username=admin_user.username, password="demo12345")
    response = authed_client.get(reverse("telemedicine-reports"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_patient_cannot_access_telemedicine_report(authed_client, patient_user, linked_patient):
    authed_client.login(username=patient_user.username, password="demo12345")
    response = authed_client.get(reverse("telemedicine-reports"))
    assert response.status_code == 403
