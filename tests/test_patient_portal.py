import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.documents.models import MedicalDocument, PatientFile, Prescription
from apps.monitoring.models import VitalReading


@pytest.mark.django_db
def test_patient_can_login_and_see_own_dashboard(authed_client, patient_user, linked_patient):
    authed_client.login(username=patient_user.username, password="demo12345")
    response = authed_client.get(reverse("dashboard"))
    assert response.status_code == 200
    assert linked_patient.last_name in response.content.decode("utf-8")


@pytest.mark.django_db
def test_patient_sees_only_own_data(authed_client, patient_user, linked_patient, linked_other_patient):
    authed_client.login(username=patient_user.username, password="demo12345")
    response = authed_client.get(reverse("patient-chart"))
    body = response.content.decode("utf-8")
    assert linked_patient.last_name in body
    assert linked_other_patient.last_name not in body


@pytest.mark.django_db
def test_patient_cannot_access_another_patient_document(
    authed_client, patient_user, linked_patient, linked_other_patient, clinician_user
):
    document = MedicalDocument.objects.create(
        patient=linked_other_patient,
        created_by=clinician_user,
        document_type="certificate",
        title="Чужой документ",
        content="Недоступно",
        status="issued",
        number="AULMED-DOC-2026-000999",
    )
    authed_client.login(username=patient_user.username, password="demo12345")
    response = authed_client.get(reverse("patient-document-detail", args=[document.pk]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_patient_cannot_access_another_patient_prescription(
    authed_client, patient_user, linked_patient, linked_other_patient, clinician_user
):
    prescription = Prescription.objects.create(
        patient=linked_other_patient,
        doctor=clinician_user,
        status="issued",
        number="AULMED-RX-2026-000999",
    )
    authed_client.login(username=patient_user.username, password="demo12345")
    response = authed_client.get(reverse("patient-prescription-detail", args=[prescription.pk]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_patient_can_view_own_document_and_prescription(
    authed_client, patient_user, linked_patient, clinician_user
):
    document = MedicalDocument.objects.create(
        patient=linked_patient,
        created_by=clinician_user,
        document_type="recommendation",
        title="Мой документ",
        content="Доступно пациенту",
        status="issued",
        number="AULMED-DOC-2026-000111",
    )
    prescription = Prescription.objects.create(
        patient=linked_patient,
        doctor=clinician_user,
        status="issued",
        number="AULMED-RX-2026-000111",
    )

    authed_client.login(username=patient_user.username, password="demo12345")
    document_response = authed_client.get(reverse("patient-document-detail", args=[document.pk]))
    prescription_response = authed_client.get(reverse("patient-prescription-detail", args=[prescription.pk]))

    assert document_response.status_code == 200
    assert prescription_response.status_code == 200


@pytest.mark.django_db
def test_patient_cannot_access_another_patient_file(
    authed_client, patient_user, linked_other_patient, clinician_user
):
    patient_file = PatientFile.objects.create(
        patient=linked_other_patient,
        uploaded_by=clinician_user,
        result_type="document",
        title="Чужой файл",
        description="Недоступно",
        file=SimpleUploadedFile("secret.pdf", b"demo file", content_type="application/pdf"),
        result_date="2026-04-20",
    )

    authed_client.login(username=patient_user.username, password="demo12345")
    response = authed_client.get(reverse("patient-file-detail", args=[patient_file.pk]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_patient_cannot_access_another_patient_vital_reading(
    authed_client, patient_user, linked_patient, linked_other_patient
):
    VitalReading.objects.create(
        patient=linked_other_patient,
        source="patient_manual",
        recorded_at="2026-04-20T10:00:00Z",
        systolic_bp=120,
    )
    authed_client.login(username=patient_user.username, password="demo12345")
    response = authed_client.get(reverse("staff-patient-vital-list", args=[linked_other_patient.pk]))
    assert response.status_code in {403, 404}
