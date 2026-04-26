import pytest
from django.urls import reverse
from django.utils import timezone

from apps.appointments.models import Appointment
from apps.documents.forms import MedicalDocumentForm
from apps.documents.models import MedicalDocument
from apps.encounters.models import Encounter
from apps.monitoring.models import VitalReading
from apps.patients.models import Patient
from apps.referrals.models import Referral


@pytest.mark.django_db
def test_registrar_can_create_patient_with_portal_account(authed_client, registrar_user, facility):
    authed_client.login(username=registrar_user.username, password="demo12345")
    response = authed_client.post(
        reverse("patient-create"),
        {
            "last_name": "Тестов",
            "first_name": "Пациент",
            "middle_name": "",
            "iin": "987654321012",
            "birth_date": "1995-04-12",
            "sex": "male",
            "phone": "+77010000000",
            "address": "ул. Абая, 10",
            "settlement_name": facility.settlement_name,
            "facility": facility.pk,
            "social_category": "general",
            "risk_level": "low",
            "attachment_date": "2026-04-01",
            "notes": "",
            "is_active": "on",
            "create_portal_account": "on",
            "portal_username": "new_patient_login",
            "portal_password": "TempPass123!",
        },
    )
    assert response.status_code == 302
    patient = Patient.objects.get(iin="987654321012")
    assert patient.patient_user is not None
    assert patient.patient_user.username == "new_patient_login"
    assert patient.patient_user.check_password("TempPass123!")


@pytest.mark.django_db
def test_referral_cannot_be_created_from_another_patients_encounter(authed_client, clinician_user, patient, other_patient, facility):
    foreign_encounter = Encounter.objects.create(
        patient=other_patient,
        facility=facility,
        clinician=clinician_user.employee_profile,
        encounter_type="clinic",
        encounter_date=timezone.localdate(),
        reason_for_visit="Foreign encounter",
        diagnosis_text="",
        services_provided="",
        result_type="completed",
        notes="",
    )
    authed_client.login(username=clinician_user.username, password="demo12345")
    response = authed_client.post(
        reverse("referral-create"),
        {
            "patient": patient.pk,
            "source_encounter": foreign_encounter.pk,
            "created_by": clinician_user.employee_profile.pk,
            "destination_org": "Областная больница",
            "destination_specialist": "Кардиолог",
            "reason": "Проверка безопасности",
            "priority": "high",
            "status": "created",
            "referral_date": "2026-04-01",
            "result_note": "",
        },
    )
    assert response.status_code == 200
    assert Referral.objects.count() == 0
    assert "source_encounter" in response.context["form"].errors


@pytest.mark.django_db
def test_medical_document_form_filters_related_objects_by_patient(patient, other_patient, clinician_user, facility):
    own_encounter = Encounter.objects.create(
        patient=patient,
        facility=facility,
        clinician=clinician_user.employee_profile,
        encounter_type="clinic",
        encounter_date=timezone.localdate(),
        reason_for_visit="Own encounter",
        diagnosis_text="",
        services_provided="",
        result_type="completed",
        notes="",
    )
    foreign_encounter = Encounter.objects.create(
        patient=other_patient,
        facility=facility,
        clinician=clinician_user.employee_profile,
        encounter_type="clinic",
        encounter_date=timezone.localdate(),
        reason_for_visit="Foreign encounter",
        diagnosis_text="",
        services_provided="",
        result_type="completed",
        notes="",
    )
    form = MedicalDocumentForm(initial={"patient": patient.pk})
    queryset = form.fields["encounter"].queryset
    assert own_encounter in queryset
    assert foreign_encounter not in queryset


@pytest.mark.django_db
def test_monitoring_root_opens_for_clinician(authed_client, clinician_user):
    authed_client.login(username=clinician_user.username, password="demo12345")
    response = authed_client.get(reverse("monitoring-root"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_patient_chart_shows_own_appointments(authed_client, patient_user, linked_patient, online_appointment):
    authed_client.login(username=patient_user.username, password="demo12345")
    response = authed_client.get(reverse("patient-chart"))
    assert response.status_code == 200
    assert str(online_appointment.get_appointment_type_display()) in response.content.decode("utf-8")


@pytest.mark.django_db
def test_patient_does_not_see_foreign_online_appointments_in_booking_list(
    authed_client, patient_user, linked_patient, linked_other_patient, clinician_user
):
    own_appointment = Appointment.objects.create(
        patient=linked_patient,
        facility=linked_patient.facility,
        created_by=patient_user,
        doctor=clinician_user,
        appointment_type="online",
        status="scheduled",
        requested_datetime=timezone.now() + timezone.timedelta(days=1),
        scheduled_datetime=timezone.now() + timezone.timedelta(days=1, hours=1),
        reason="Own appointment",
    )
    Appointment.objects.create(
        patient=linked_other_patient,
        facility=linked_other_patient.facility,
        created_by=clinician_user,
        doctor=clinician_user,
        appointment_type="online",
        status="scheduled",
        requested_datetime=timezone.now() + timezone.timedelta(days=2),
        scheduled_datetime=timezone.now() + timezone.timedelta(days=2, hours=1),
        reason="Foreign appointment",
    )

    authed_client.login(username=patient_user.username, password="demo12345")
    response = authed_client.get(reverse("patient-appointment-list"))
    assert response.status_code == 200
    visible_ids = {item.pk for item in response.context["page_obj"].object_list}
    assert own_appointment.pk in visible_ids
    assert len(visible_ids) == 1
    detail_response = authed_client.get(reverse("patient-appointment-detail", args=[own_appointment.pk]))
    assert detail_response.status_code == 200


@pytest.mark.django_db
def test_staff_patient_card_shows_patient_appointments(authed_client, clinician_user, linked_patient):
    appointment = Appointment.objects.create(
        patient=linked_patient,
        facility=linked_patient.facility,
        created_by=clinician_user,
        doctor=clinician_user,
        appointment_type="offline",
        status="requested",
        requested_datetime=timezone.now() + timezone.timedelta(days=1),
        reason="Staff card visibility",
    )

    authed_client.login(username=clinician_user.username, password="demo12345")
    response = authed_client.get(reverse("patient-detail", args=[linked_patient.pk]))
    body = response.content.decode("utf-8")
    assert response.status_code == 200
    assert appointment.get_appointment_type_display() in body


@pytest.mark.django_db
def test_registrar_sees_facility_patient_appointments_in_staff_list(
    authed_client, registrar_user, clinician_user, linked_patient
):
    appointment = Appointment.objects.create(
        patient=linked_patient,
        facility=linked_patient.facility,
        created_by=clinician_user,
        doctor=clinician_user,
        appointment_type="offline",
        status="requested",
        requested_datetime=timezone.now() + timezone.timedelta(days=1),
        reason="Registrar visibility",
    )
    authed_client.login(username=registrar_user.username, password="demo12345")
    response = authed_client.get(reverse("staff-appointment-list"))
    assert response.status_code == 200
    visible_ids = {item.pk for item in response.context["page_obj"].object_list}
    assert appointment.pk in visible_ids


@pytest.mark.django_db
def test_staff_document_create_redirects_to_existing_detail(
    authed_client, clinician_user, linked_patient
):
    authed_client.login(username=clinician_user.username, password="demo12345")
    response = authed_client.post(
        reverse("staff-document-create"),
        {
            "patient": linked_patient.pk,
            "consultation": "",
            "encounter": "",
            "referral": "",
            "document_type": "recommendation",
            "title": "Документ без 404",
            "content": "Проверка редиректа",
            "status": "draft",
            "valid_until": "",
        },
        follow=True,
    )
    assert response.status_code == 200
    document = MedicalDocument.objects.get(title="Документ без 404")
    assert response.request["PATH_INFO"] == reverse("staff-document-detail", args=[document.pk])


@pytest.mark.django_db
def test_staff_monitoring_page_uses_staff_create_link(authed_client, clinician_user, linked_patient):
    VitalReading.objects.create(
        patient=linked_patient,
        source="doctor_manual",
        recorded_by=clinician_user,
        recorded_at=timezone.now(),
        systolic_bp=120,
        diastolic_bp=80,
    )
    authed_client.login(username=clinician_user.username, password="demo12345")
    response = authed_client.get(reverse("staff-patient-vital-list", args=[linked_patient.pk]))
    body = response.content.decode("utf-8")
    assert response.status_code == 200
    assert reverse("staff-patient-vital-create", args=[linked_patient.pk]) in body


@pytest.mark.django_db
def test_staff_cannot_open_foreign_facility_monitoring_page(
    authed_client, clinician_user, facility
):
    other_facility = Patient.objects.create(
        last_name="Чужой",
        first_name="Пациент",
        middle_name="",
        iin="555555555555",
        birth_date="1990-01-01",
        sex="male",
        phone="+77010000001",
        address="ул. Другая, 1",
        settlement_name="Другой аул",
        facility=facility.__class__.objects.create(
            name="Чужой ФАП",
            facility_type="fap",
            region="Другой регион",
            district="Другой район",
            settlement_name="Другой аул",
            address="ул. Другая, 2",
            phone="+77010000002",
        ),
        social_category="general",
        risk_level="low",
        attachment_date="2026-04-01",
    )
    authed_client.login(username=clinician_user.username, password="demo12345")
    response = authed_client.get(reverse("staff-patient-vital-list", args=[other_facility.pk]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_patient_file_form_filters_related_consultation_by_patient(
    linked_patient, linked_other_patient, online_appointment
):
    from apps.documents.forms import PatientFileForm

    foreign_consultation = linked_other_patient.online_consultations.create(
        doctor=online_appointment.online_consultation.doctor,
        facility=linked_other_patient.facility,
        status="scheduled",
        scheduled_start=timezone.now() + timezone.timedelta(days=3),
        scheduled_end=timezone.now() + timezone.timedelta(days=3, minutes=30),
        created_by=online_appointment.online_consultation.created_by,
    )
    form = PatientFileForm(initial={"patient": linked_patient.pk})
    queryset = form.fields["related_consultation"].queryset
    assert online_appointment.online_consultation in queryset
    assert foreign_consultation not in queryset
