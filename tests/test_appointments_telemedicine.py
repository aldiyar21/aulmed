import pytest
from django.urls import reverse

from apps.appointments.models import Appointment
from apps.documents.models import MedicalDocument, Prescription
from apps.telemedicine.models import Teleconsilium


@pytest.mark.django_db
def test_patient_can_create_online_appointment_request(authed_client, patient_user, linked_patient):
    authed_client.login(username=patient_user.username, password="demo12345")
    response = authed_client.post(
        reverse("patient-appointment-create"),
        {
            "facility": linked_patient.facility.pk,
            "appointment_type": "online",
            "requested_datetime": "2026-05-01T10:00",
            "reason": "Нужна видеоконсультация",
        },
        follow=True,
    )
    assert response.status_code == 200
    appointment = Appointment.objects.get(patient=linked_patient)
    assert appointment.appointment_type == "online"


@pytest.mark.django_db
def test_staff_can_schedule_online_appointment_and_create_consultation(
    authed_client, registrar_user, patient_user, linked_patient, clinician_user
):
    appointment = Appointment.objects.create(
        patient=linked_patient,
        facility=linked_patient.facility,
        created_by=patient_user,
        appointment_type="online",
        status="requested",
        requested_datetime="2026-05-01T10:00:00Z",
        reason="Онлайн прием",
    )
    authed_client.login(username=registrar_user.username, password="demo12345")
    response = authed_client.post(
        reverse("staff-appointment-update", args=[appointment.pk]),
        {
            "status": "scheduled",
            "doctor": clinician_user.pk,
            "scheduled_datetime": "2026-05-01T11:00",
            "duration_minutes": 30,
            "appointment_type": "online",
            "reason": appointment.reason,
            "cancellation_reason": "",
        },
        follow=True,
    )
    assert response.status_code == 200
    appointment.refresh_from_db()
    assert appointment.online_consultation is not None


@pytest.mark.django_db
def test_repeated_save_does_not_duplicate_online_consultation(
    authed_client, registrar_user, patient_user, linked_patient, clinician_user
):
    appointment = Appointment.objects.create(
        patient=linked_patient,
        facility=linked_patient.facility,
        created_by=patient_user,
        appointment_type="online",
        status="requested",
        requested_datetime="2026-05-01T10:00:00Z",
        reason="Онлайн прием",
    )
    authed_client.login(username=registrar_user.username, password="demo12345")
    payload = {
        "status": "scheduled",
        "doctor": clinician_user.pk,
        "scheduled_datetime": "2026-05-01T11:00",
        "duration_minutes": 30,
        "appointment_type": "online",
        "reason": appointment.reason,
        "cancellation_reason": "",
    }
    authed_client.post(reverse("staff-appointment-update", args=[appointment.pk]), payload)
    authed_client.post(reverse("staff-appointment-update", args=[appointment.pk]), payload)
    assert Appointment.objects.get(pk=appointment.pk).online_consultation is not None
    assert Appointment.objects.get(pk=appointment.pk).patient.online_consultations.count() == 1


@pytest.mark.django_db
def test_doctor_can_access_assigned_consultation(authed_client, clinician_user, online_appointment):
    authed_client.login(username=clinician_user.username, password="demo12345")
    response = authed_client.get(reverse("consultation-detail", args=[online_appointment.online_consultation.pk]))
    assert response.status_code == 200


@pytest.mark.django_db
def test_unrelated_patient_cannot_access_consultation(
    authed_client, other_patient_user, linked_other_patient, online_appointment
):
    authed_client.login(username=other_patient_user.username, password="demo12345")
    response = authed_client.get(reverse("consultation-detail", args=[online_appointment.online_consultation.pk]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_consultation_room_generates_non_pii_jitsi_room_name(online_appointment, linked_patient):
    room_name = online_appointment.online_consultation.jitsi_room_name
    assert room_name.startswith("aulmed-")
    assert linked_patient.last_name.lower() not in room_name.lower()
    assert (linked_patient.iin or "") not in room_name


@pytest.mark.django_db
def test_jitsi_room_url_uses_meet_jitsi_by_default(online_appointment):
    assert online_appointment.online_consultation.jitsi_room_url.startswith("https://meet.jit.si/")


@pytest.mark.django_db
def test_doctor_can_start_and_complete_consultation(authed_client, clinician_user, online_appointment):
    consultation = online_appointment.online_consultation
    authed_client.login(username=clinician_user.username, password="demo12345")
    start_response = authed_client.get(reverse("consultation-start", args=[consultation.pk]), follow=True)
    assert start_response.status_code == 200
    complete_response = authed_client.post(
        reverse("consultation-complete", args=[consultation.pk]),
        {
            "anamnesis": "Тест",
            "diagnosis_text": "ОРВИ",
            "treatment_plan": "",
            "doctor_recommendations": "",
            "follow_up_required": "",
            "follow_up_date": "",
        },
        follow=True,
    )
    assert complete_response.status_code == 200
    consultation.refresh_from_db()
    assert consultation.status == "completed"


@pytest.mark.django_db
def test_completion_requires_at_least_one_conclusion_field(authed_client, clinician_user, online_appointment):
    consultation = online_appointment.online_consultation
    authed_client.login(username=clinician_user.username, password="demo12345")
    response = authed_client.post(
        reverse("consultation-complete", args=[consultation.pk]),
        {
            "anamnesis": "",
            "diagnosis_text": "",
            "treatment_plan": "",
            "doctor_recommendations": "",
            "follow_up_required": "",
            "follow_up_date": "",
        },
    )
    assert response.status_code == 200
    consultation.refresh_from_db()
    assert consultation.status != "completed"


@pytest.mark.django_db
def test_patient_consent_required_before_patient_enters_consultation_room(
    authed_client, patient_user, online_appointment
):
    authed_client.login(username=patient_user.username, password="demo12345")
    response = authed_client.get(reverse("consultation-room", args=[online_appointment.online_consultation.pk]))
    assert response.status_code == 302
    assert reverse("consultation-consent", args=[online_appointment.online_consultation.pk]) in response.url


@pytest.mark.django_db
def test_accepted_consent_allows_patient_to_enter_consultation_room(
    authed_client, patient_user, online_appointment
):
    authed_client.login(username=patient_user.username, password="demo12345")
    authed_client.post(reverse("consultation-consent", args=[online_appointment.online_consultation.pk]), follow=True)
    response = authed_client.get(reverse("consultation-room", args=[online_appointment.online_consultation.pk]))
    assert response.status_code == 200


@pytest.mark.django_db
def test_teleconsilium_participant_can_open_room(
    authed_client, clinician_user, create_user, linked_patient
):
    invited_doctor = create_user("invited_doctor", "Медработник", "clinician")
    teleconsilium = Teleconsilium.objects.create(
        patient=linked_patient,
        primary_doctor=clinician_user,
        facility=linked_patient.facility,
        topic="Совместный разбор",
        description="Нужен второй взгляд",
        status="scheduled",
        scheduled_at="2026-05-01T12:00:00Z",
    )
    teleconsilium.invited_doctors.add(invited_doctor)

    authed_client.login(username=invited_doctor.username, password="demo12345")
    response = authed_client.get(reverse("teleconsilium-room", args=[teleconsilium.pk]))
    assert response.status_code == 200


@pytest.mark.django_db
def test_doctor_can_create_document_and_prescription(
    authed_client, clinician_user, linked_patient, online_appointment
):
    authed_client.login(username=clinician_user.username, password="demo12345")
    document_response = authed_client.post(
        reverse("staff-document-create"),
        {
            "patient": linked_patient.pk,
            "consultation": online_appointment.online_consultation.pk,
            "encounter": "",
            "referral": "",
            "document_type": "recommendation",
            "title": "Рекомендация",
            "content": "Тестовый контент",
            "status": "issued",
            "valid_until": "",
        },
        follow=True,
    )
    assert document_response.status_code == 200
    assert MedicalDocument.objects.filter(patient=linked_patient).exists()

    rx_response = authed_client.post(
        reverse("staff-prescription-create"),
        {
            "patient": linked_patient.pk,
            "consultation": online_appointment.online_consultation.pk,
            "status": "issued",
            "notes": "Тест",
            "items-TOTAL_FORMS": "2",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "0",
            "items-MAX_NUM_FORMS": "1000",
            "items-0-medication_name": "Парацетамол",
            "items-0-dosage": "500 мг",
            "items-0-frequency": "2 раза",
            "items-0-duration": "3 дня",
            "items-0-instructions": "После еды",
            "items-1-medication_name": "",
            "items-1-dosage": "",
            "items-1-frequency": "",
            "items-1-duration": "",
            "items-1-instructions": "",
        },
        follow=True,
    )
    assert rx_response.status_code == 200
    assert Prescription.objects.filter(patient=linked_patient).exists()
