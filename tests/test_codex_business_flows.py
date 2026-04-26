from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client
from django.utils import timezone
import pytest

from apps.accounts.models import EmployeeProfile
from apps.accounts.services import ensure_role_groups
from apps.appointments.models import Appointment
from apps.audit.models import AuditLog
from apps.documents.models import MedicalDocument, PatientFile, Prescription
from apps.encounters.models import Encounter
from apps.facilities.models import Facility
from apps.monitoring.models import VitalReading
from apps.patients.models import Patient
from apps.prevention.models import PreventionEvent
from apps.referrals.models import Referral
from apps.telemedicine.models import OnlineConsultation, PatientConsent
from apps.visits.models import HomeVisit, HomeVisitPatient


pytestmark = pytest.mark.django_db


def _date_input(value):
    return value.isoformat()


def _datetime_input(value):
    if timezone.is_naive(value):
        value = timezone.make_aware(value, timezone.get_current_timezone())
    return timezone.localtime(value).strftime("%Y-%m-%dT%H:%M")


def _group_name(role_name: str) -> str:
    return role_name


def _make_client(user: User) -> Client:
    client = Client()
    assert client.login(username=user.username, password="demo12345")
    return client


def _create_staff_user(*, username: str, role_name: str, role_code: str, facility: Facility, is_superuser: bool = False) -> User:
    user = User.objects.create_user(
        username=username,
        password="demo12345",
        first_name="TEST-CODEX",
        last_name=role_code.upper(),
        is_staff=True,
        is_superuser=is_superuser,
    )
    user.groups.set([Group.objects.get(name=_group_name(role_name))])
    EmployeeProfile.objects.create(
        user=user,
        facility=facility,
        position=f"TEST-CODEX {role_code}",
        role_code=role_code,
        phone="+77000000000",
    )
    return user


def _create_patient_user(*, username: str) -> User:
    user = User.objects.create_user(
        username=username,
        password="demo12345",
        first_name="TEST-CODEX",
        last_name="PATIENT",
        is_staff=False,
    )
    user.groups.set([Group.objects.get(name=_group_name(settings.ROLE_PATIENT))])
    return user


def _create_patient(
    *,
    facility: Facility,
    iin: str,
    last_name: str,
    first_name: str,
    linked_user: User | None = None,
    settlement_name: str | None = None,
) -> Patient:
    return Patient.objects.create(
        last_name=last_name,
        first_name=first_name,
        middle_name="TEST-CODEX",
        iin=iin,
        birth_date=timezone.localdate().replace(year=1990),
        sex="male",
        phone="+77000000001",
        address="TEST-CODEX address",
        settlement_name=settlement_name or facility.settlement_name,
        facility=facility,
        social_category="general",
        risk_level="low",
        attachment_date=timezone.localdate(),
        notes="TEST-CODEX notes",
        patient_user=linked_user,
    )


@pytest.fixture
def codex_env():
    ensure_role_groups()
    facility_a = Facility.objects.create(
        name="TEST-CODEX Facility A",
        facility_type="clinic",
        region="TEST-CODEX Region",
        district="TEST-CODEX District A",
        settlement_name="TEST-CODEX Settlement A",
        address="TEST-CODEX address A",
        phone="+77000000010",
    )
    facility_b = Facility.objects.create(
        name="TEST-CODEX Facility B",
        facility_type="clinic",
        region="TEST-CODEX Region",
        district="TEST-CODEX District B",
        settlement_name="TEST-CODEX Settlement B",
        address="TEST-CODEX address B",
        phone="+77000000011",
    )

    admin = _create_staff_user(
        username="test_codex_admin",
        role_name=settings.ROLE_ADMIN,
        role_code="admin",
        facility=facility_a,
        is_superuser=True,
    )
    registrator = _create_staff_user(
        username="test_codex_registrator",
        role_name=settings.ROLE_REGISTRAR,
        role_code="registrar",
        facility=facility_a,
    )
    doctor = _create_staff_user(
        username="test_codex_doctor",
        role_name=settings.ROLE_CLINICIAN,
        role_code="clinician",
        facility=facility_a,
    )
    doctor_b = _create_staff_user(
        username="test_codex_doctor_b",
        role_name=settings.ROLE_CLINICIAN,
        role_code="clinician",
        facility=facility_b,
    )
    manager = _create_staff_user(
        username="test_codex_manager",
        role_name=settings.ROLE_MANAGER,
        role_code="manager",
        facility=facility_a,
    )
    patient_user_a = _create_patient_user(username="test_codex_patient_a")
    patient_user_b = _create_patient_user(username="test_codex_patient_b")
    patient_user_c = _create_patient_user(username="test_codex_patient_c")

    patient_a = _create_patient(
        facility=facility_a,
        iin="100000000001",
        last_name="TEST-CODEX-A",
        first_name="Patient",
        linked_user=patient_user_a,
    )
    patient_b = _create_patient(
        facility=facility_a,
        iin="100000000002",
        last_name="TEST-CODEX-B",
        first_name="Patient",
        linked_user=patient_user_b,
    )
    patient_c = _create_patient(
        facility=facility_b,
        iin="100000000003",
        last_name="TEST-CODEX-C",
        first_name="Patient",
        linked_user=patient_user_c,
        settlement_name=facility_b.settlement_name,
    )

    return SimpleNamespace(
        facility_a=facility_a,
        facility_b=facility_b,
        admin=admin,
        registrator=registrator,
        doctor=doctor,
        doctor_b=doctor_b,
        manager=manager,
        patient_user_a=patient_user_a,
        patient_user_b=patient_user_b,
        patient_user_c=patient_user_c,
        patient_a=patient_a,
        patient_b=patient_b,
        patient_c=patient_c,
    )


def test_demo_seeded_users_login_and_dashboard_smoke():
    call_command("create_demo_users")
    call_command("seed_demo_data")

    demo_users = ["admin", "doctor", "registrator", "manager", "patient"]
    for username in demo_users:
        client = Client()
        assert client.login(username=username, password="demo12345"), username
        response = client.get("/dashboard/")
        assert response.status_code == 200, (username, response.status_code)

    linked_patient = Patient.objects.filter(patient_user__username="patient").first()
    assert linked_patient is not None


def test_admin_access_and_anonymous_redirect_smoke(codex_env):
    anonymous = Client()
    dashboard_redirect = anonymous.get("/dashboard/")
    patients_redirect = anonymous.get("/patients/")
    assert dashboard_redirect.status_code == 302
    assert patients_redirect.status_code == 302

    admin_client = _make_client(codex_env.admin)
    admin_urls = [
        "/dashboard/",
        "/patients/",
        "/patients/create/",
        "/encounters/",
        "/encounters/create/",
        "/referrals/",
        "/referrals/create/",
        "/visits/",
        "/visits/create/",
        "/prevention/",
        "/prevention/create/",
        "/reports/",
        "/reports/telemedicine/",
        "/appointments/staff/",
        "/telemedicine/consultations/",
        "/documents/staff/",
        "/documents/staff/create/",
        "/documents/staff/prescriptions/",
        "/documents/staff/prescriptions/create/",
    ]
    for url in admin_urls:
        response = admin_client.get(url)
        assert response.status_code == 200, url


def test_registrator_patient_registry_flow_and_export(codex_env):
    client = _make_client(codex_env.registrator)

    list_response = client.get("/patients/")
    assert list_response.status_code == 200

    create_payload = {
        "last_name": "TEST-CODEX",
        "first_name": "Patient",
        "middle_name": "Auto",
        "iin": "100000000099",
        "birth_date": "1990-01-01",
        "sex": "female",
        "phone": "+77000000021",
        "address": "TEST-CODEX registry address",
        "settlement_name": codex_env.facility_a.settlement_name,
        "facility": str(codex_env.facility_a.pk),
        "social_category": "general",
        "risk_level": "medium",
        "attachment_date": timezone.localdate().isoformat(),
        "notes": "TEST-CODEX registry patient",
        "is_active": "on",
        "create_portal_account": "on",
        "portal_username": "test_codex_registry_patient",
        "portal_password": "demo12345",
    }
    create_response = client.post("/patients/create/", create_payload, follow=False)
    assert create_response.status_code == 302

    created_patient = Patient.objects.get(iin="100000000099")
    assert created_patient.patient_user.username == "test_codex_registry_patient"

    search_response = client.get("/patients/", {"q": "TEST-CODEX"})
    assert search_response.status_code == 200
    assert b"TEST-CODEX" in search_response.content

    detail_response = client.get(f"/patients/{created_patient.pk}/")
    assert detail_response.status_code == 200
    assert b"TEST-CODEX" in detail_response.content

    update_payload = create_payload | {
        "phone": "+77000000022",
        "notes": "TEST-CODEX updated notes",
        "portal_username": "test_codex_registry_patient",
        "portal_password": "demo12345",
    }
    update_response = client.post(f"/patients/{created_patient.pk}/edit/", update_payload, follow=False)
    assert update_response.status_code == 302
    created_patient.refresh_from_db()
    assert created_patient.phone == "+77000000022"
    assert created_patient.notes == "TEST-CODEX updated notes"

    duplicate_response = client.post("/patients/create/", create_payload)
    assert duplicate_response.status_code == 200
    assert Patient.objects.filter(iin="100000000099").count() == 1

    export_response = client.get("/patients/export/")
    assert export_response.status_code == 200
    assert export_response["Content-Type"].startswith("text/csv")
    assert "100000000099" in export_response.content.decode("utf-8")


def test_doctor_encounter_referral_prevention_and_exports(codex_env):
    client = _make_client(codex_env.doctor)

    encounter_response = client.post(
        "/encounters/create/",
        {
            "patient": str(codex_env.patient_a.pk),
            "facility": str(codex_env.facility_a.pk),
            "clinician": str(codex_env.doctor.employee_profile.pk),
            "encounter_type": Encounter.ENCOUNTER_TYPES[0][0],
            "encounter_date": timezone.localdate().isoformat(),
            "reason_for_visit": "TEST-CODEX encounter reason",
            "diagnosis_text": "TEST-CODEX diagnosis",
            "services_provided": "TEST-CODEX services",
            "result_type": Encounter.RESULT_TYPES[0][0],
            "next_visit_date": (timezone.localdate() + timezone.timedelta(days=7)).isoformat(),
            "notes": "TEST-CODEX encounter notes",
        },
        follow=False,
    )
    assert encounter_response.status_code == 302
    encounter = Encounter.objects.get(reason_for_visit="TEST-CODEX encounter reason")

    patient_card = client.get(f"/patients/{codex_env.patient_a.pk}/")
    assert patient_card.status_code == 200
    assert any(item.pk == encounter.pk for item in patient_card.context["encounters"])

    encounter_update = client.post(
        f"/encounters/{encounter.pk}/edit/",
        {
            "patient": str(codex_env.patient_a.pk),
            "facility": str(codex_env.facility_a.pk),
            "clinician": str(codex_env.doctor.employee_profile.pk),
            "encounter_type": encounter.encounter_type,
            "encounter_date": timezone.localdate().isoformat(),
            "reason_for_visit": encounter.reason_for_visit,
            "diagnosis_text": "TEST-CODEX diagnosis updated",
            "services_provided": encounter.services_provided,
            "result_type": Encounter.RESULT_TYPES[-1][0],
            "next_visit_date": (timezone.localdate() + timezone.timedelta(days=10)).isoformat(),
            "notes": encounter.notes,
        },
        follow=False,
    )
    assert encounter_update.status_code == 302
    encounter.refresh_from_db()
    assert encounter.diagnosis_text == "TEST-CODEX diagnosis updated"

    encounter_export = client.get("/encounters/export/")
    assert encounter_export.status_code == 200
    assert encounter_export["Content-Type"].startswith("text/csv")
    assert codex_env.patient_a.last_name in encounter_export.content.decode("utf-8")

    referral_response = client.post(
        "/referrals/create/",
        {
            "patient": str(codex_env.patient_a.pk),
            "source_encounter": str(encounter.pk),
            "created_by": str(codex_env.doctor.employee_profile.pk),
            "destination_org": "TEST-CODEX Referral Org",
            "destination_specialist": "TEST-CODEX Specialist",
            "reason": "TEST-CODEX referral reason",
            "priority": Referral.PRIORITY_CHOICES[0][0],
            "status": Referral.STATUS_CHOICES[0][0],
            "referral_date": timezone.localdate().isoformat(),
            "result_note": "TEST-CODEX referral note",
        },
        follow=False,
    )
    assert referral_response.status_code == 302
    referral = Referral.objects.get(reason="TEST-CODEX referral reason")

    referral_update = client.post(
        f"/referrals/{referral.pk}/edit/",
        {
            "patient": str(codex_env.patient_a.pk),
            "source_encounter": str(encounter.pk),
            "created_by": str(codex_env.doctor.employee_profile.pk),
            "destination_org": referral.destination_org,
            "destination_specialist": referral.destination_specialist,
            "reason": referral.reason,
            "priority": referral.priority,
            "status": "completed",
            "referral_date": referral.referral_date.isoformat(),
            "result_note": "TEST-CODEX referral result",
        },
        follow=False,
    )
    assert referral_update.status_code == 302
    referral.refresh_from_db()
    assert referral.status == "completed"
    assert referral.result_note == "TEST-CODEX referral result"

    patient_referral_list = _make_client(codex_env.patient_user_a).get("/patients/my/referrals/")
    assert patient_referral_list.status_code == 200
    assert any(item.pk == referral.pk for item in patient_referral_list.context["page_obj"].object_list)

    referral_export = client.get("/referrals/export/")
    assert referral_export.status_code == 200
    assert referral_export["Content-Type"].startswith("text/csv")

    foreign_encounter = Encounter.objects.create(
        patient=codex_env.patient_b,
        facility=codex_env.facility_a,
        clinician=codex_env.doctor.employee_profile,
        encounter_type=Encounter.ENCOUNTER_TYPES[0][0],
        encounter_date=timezone.localdate(),
        reason_for_visit="TEST-CODEX foreign encounter",
        diagnosis_text="TEST-CODEX foreign diagnosis",
        services_provided="TEST-CODEX foreign services",
        result_type=Encounter.RESULT_TYPES[0][0],
        notes="TEST-CODEX foreign notes",
    )
    mismatch_response = client.post(
        "/referrals/create/",
        {
            "patient": str(codex_env.patient_a.pk),
            "source_encounter": str(foreign_encounter.pk),
            "created_by": str(codex_env.doctor.employee_profile.pk),
            "destination_org": "TEST-CODEX Mismatch Org",
            "destination_specialist": "TEST-CODEX Mismatch Specialist",
            "reason": "TEST-CODEX mismatch referral",
            "priority": Referral.PRIORITY_CHOICES[0][0],
            "status": Referral.STATUS_CHOICES[0][0],
            "referral_date": timezone.localdate().isoformat(),
            "result_note": "",
        },
    )
    assert mismatch_response.status_code == 200
    assert not Referral.objects.filter(reason="TEST-CODEX mismatch referral").exists()

    planned_response = client.post(
        "/prevention/create/",
        {
            "patient": str(codex_env.patient_a.pk),
            "event_type": PreventionEvent.EVENT_TYPES[0][0],
            "planned_date": (timezone.localdate() + timezone.timedelta(days=1)).isoformat(),
            "completed_date": "",
            "status": "planned",
            "assigned_employee": str(codex_env.doctor.employee_profile.pk),
            "notes": "TEST-CODEX prevention planned",
        },
        follow=False,
    )
    assert planned_response.status_code == 302

    overdue = PreventionEvent.objects.create(
        patient=codex_env.patient_a,
        event_type=PreventionEvent.EVENT_TYPES[0][0],
        planned_date=timezone.localdate() - timezone.timedelta(days=1),
        status="planned",
        assigned_employee=codex_env.doctor.employee_profile,
        notes="TEST-CODEX prevention overdue",
    )

    overdue_response = client.get("/prevention/overdue/")
    assert overdue_response.status_code == 200
    overdue.refresh_from_db()
    assert overdue.status == "overdue"
    assert any(item.pk == overdue.pk for item in overdue_response.context["page_obj"])

    complete_response = client.post(
        f"/prevention/{overdue.pk}/edit/",
        {
            "patient": str(codex_env.patient_a.pk),
            "event_type": overdue.event_type,
            "planned_date": overdue.planned_date.isoformat(),
            "completed_date": timezone.localdate().isoformat(),
            "status": "completed",
            "assigned_employee": str(codex_env.doctor.employee_profile.pk),
            "notes": "TEST-CODEX prevention completed",
        },
        follow=False,
    )
    assert complete_response.status_code == 302
    overdue.refresh_from_db()
    assert overdue.status == "completed"

    prevention_export = client.get("/prevention/export/")
    assert prevention_export.status_code == 200
    assert prevention_export["Content-Type"].startswith("text/csv")


def test_visit_flow_supports_multiple_patients_and_preserves_links_on_edit(codex_env):
    client = _make_client(codex_env.registrator)

    create_response = client.post(
        "/visits/create/",
        {
            "planned_date": timezone.localdate().isoformat(),
            "facility": str(codex_env.facility_a.pk),
            "assigned_employee": str(codex_env.doctor.employee_profile.pk),
            "settlement_name": codex_env.facility_a.settlement_name,
            "status": "planned",
            "purpose": "TEST-CODEX home visit",
            "route_notes": "TEST-CODEX route notes",
            "result_summary": "",
            "patients": [str(codex_env.patient_a.pk), str(codex_env.patient_b.pk)],
        },
        follow=False,
    )
    assert create_response.status_code == 302
    visit = HomeVisit.objects.get(purpose="TEST-CODEX home visit")
    assert visit.visit_patients.count() == 2

    today_response = client.get("/visits/today/")
    assert today_response.status_code == 200
    assert any(item.pk == visit.pk for item in today_response.context["visits"])

    patient_detail = client.get(f"/patients/{codex_env.patient_a.pk}/")
    assert patient_detail.status_code == 200
    assert any(item.home_visit_id == visit.pk for item in patient_detail.context["visit_links"])

    link_a = HomeVisitPatient.objects.get(home_visit=visit, patient=codex_env.patient_a)
    link_b = HomeVisitPatient.objects.get(home_visit=visit, patient=codex_env.patient_b)
    link_a.notes = "TEST-CODEX patient A outcome"
    link_a.save(update_fields=["notes"])
    link_b.notes = "TEST-CODEX patient B outcome"
    link_b.save(update_fields=["notes"])

    update_response = client.post(
        f"/visits/{visit.pk}/edit/",
        {
            "planned_date": visit.planned_date.isoformat(),
            "facility": str(codex_env.facility_a.pk),
            "assigned_employee": str(codex_env.doctor.employee_profile.pk),
            "settlement_name": visit.settlement_name,
            "status": "completed",
            "purpose": visit.purpose,
            "route_notes": "TEST-CODEX route notes updated",
            "result_summary": "TEST-CODEX completed visit",
            "patients": [str(codex_env.patient_a.pk), str(codex_env.patient_b.pk)],
        },
        follow=False,
    )
    assert update_response.status_code == 302
    visit.refresh_from_db()
    assert visit.visit_patients.count() == 2
    assert visit.route_notes == "TEST-CODEX route notes updated"
    assert HomeVisitPatient.objects.get(home_visit=visit, patient=codex_env.patient_a).notes == "TEST-CODEX patient A outcome"
    assert HomeVisitPatient.objects.get(home_visit=visit, patient=codex_env.patient_b).notes == "TEST-CODEX patient B outcome"


def test_patient_dashboard_appointments_telemedicine_and_room_consent_flow(codex_env):
    patient_client = _make_client(codex_env.patient_user_a)

    dashboard_response = patient_client.get("/dashboard/")
    assert dashboard_response.status_code == 200
    assert patient_client.get("/patients/my/dashboard/").status_code == 200
    assert patient_client.get("/patients/my/profile/").status_code == 200
    assert patient_client.get("/patients/my/chart/").status_code == 200

    offline_response = patient_client.post(
        "/appointments/my/create/",
        {
            "facility": str(codex_env.facility_a.pk),
            "appointment_type": Appointment.AppointmentType.OFFLINE,
            "requested_datetime": _datetime_input(timezone.now() + timezone.timedelta(days=2)),
            "reason": "TEST-CODEX offline appointment",
        },
        follow=False,
    )
    assert offline_response.status_code == 302
    offline_appointment = Appointment.objects.get(reason="TEST-CODEX offline appointment")
    assert offline_appointment.patient_id == codex_env.patient_a.pk
    assert offline_appointment.status == Appointment.Status.REQUESTED

    online_response = patient_client.post(
        "/appointments/my/create/",
        {
            "facility": str(codex_env.facility_a.pk),
            "appointment_type": Appointment.AppointmentType.ONLINE,
            "requested_datetime": _datetime_input(timezone.now() + timezone.timedelta(days=3)),
            "reason": "TEST-CODEX online appointment",
        },
        follow=False,
    )
    assert online_response.status_code == 302
    online_appointment = Appointment.objects.get(reason="TEST-CODEX online appointment")
    consultation = OnlineConsultation.objects.get(appointment=online_appointment)

    appointment_list = patient_client.get("/appointments/my/")
    assert appointment_list.status_code == 200
    assert patient_client.get(f"/appointments/my/{online_appointment.pk}/").status_code == 200

    staff_client = _make_client(codex_env.registrator)
    schedule_response = staff_client.post(
        f"/appointments/staff/{online_appointment.pk}/edit/",
        {
            "status": Appointment.Status.SCHEDULED,
            "doctor": str(codex_env.doctor.pk),
            "scheduled_datetime": _datetime_input(timezone.now() + timezone.timedelta(days=4)),
            "duration_minutes": "30",
            "appointment_type": Appointment.AppointmentType.ONLINE,
            "reason": online_appointment.reason,
            "cancellation_reason": "",
        },
        follow=False,
    )
    assert schedule_response.status_code == 302
    online_appointment.refresh_from_db()
    consultation.refresh_from_db()
    assert online_appointment.status == Appointment.Status.SCHEDULED
    assert consultation.doctor_id == codex_env.doctor.pk

    doctor_client = _make_client(codex_env.doctor)
    doctor_list = doctor_client.get("/appointments/doctor/")
    assert doctor_list.status_code == 200
    assert codex_env.patient_a.last_name.encode() in doctor_list.content

    consultation_list = patient_client.get("/telemedicine/consultations/")
    assert consultation_list.status_code == 200
    assert doctor_client.get("/telemedicine/consultations/").status_code == 200

    consent_gate = patient_client.get(f"/telemedicine/consultations/{consultation.pk}/room/")
    assert consent_gate.status_code == 302
    assert consent_gate.headers["Location"].endswith(f"/telemedicine/consultations/{consultation.pk}/consent/")

    consent_response = patient_client.post(f"/telemedicine/consultations/{consultation.pk}/consent/", follow=False)
    assert consent_response.status_code == 302
    assert PatientConsent.objects.filter(consultation=consultation, patient=codex_env.patient_a).exists()

    room_response = patient_client.get(f"/telemedicine/consultations/{consultation.pk}/room/")
    assert room_response.status_code == 200
    assert consultation.jitsi_domain.encode() in room_response.content
    assert codex_env.patient_a.last_name.encode() not in room_response.content
    assert codex_env.patient_a.iin.encode() not in room_response.content
    assert codex_env.patient_a.phone.encode() not in room_response.content
    assert codex_env.patient_a.last_name not in consultation.jitsi_room_name
    assert codex_env.patient_a.iin not in consultation.jitsi_room_name
    assert codex_env.patient_a.phone not in consultation.jitsi_room_name

    start_response = doctor_client.get(f"/telemedicine/consultations/{consultation.pk}/start/", follow=False)
    assert start_response.status_code == 302
    consultation.refresh_from_db()
    assert consultation.status == OnlineConsultation.Status.IN_PROGRESS

    complete_response = doctor_client.post(
        f"/telemedicine/consultations/{consultation.pk}/complete/",
        {
            "anamnesis": "TEST-CODEX anamnesis",
            "diagnosis_text": "TEST-CODEX telemedicine diagnosis",
            "treatment_plan": "TEST-CODEX treatment plan",
            "doctor_recommendations": "TEST-CODEX recommendations",
            "follow_up_required": "on",
            "follow_up_date": (timezone.localdate() + timezone.timedelta(days=14)).isoformat(),
        },
        follow=False,
    )
    assert complete_response.status_code == 302
    consultation.refresh_from_db()
    assert consultation.status == OnlineConsultation.Status.COMPLETED
    assert consultation.diagnosis_text == "TEST-CODEX telemedicine diagnosis"


def test_documents_prescriptions_and_files_flow(codex_env):
    doctor_client = _make_client(codex_env.doctor)
    patient_client = _make_client(codex_env.patient_user_a)

    appointment = Appointment.objects.create(
        patient=codex_env.patient_a,
        facility=codex_env.facility_a,
        doctor=codex_env.doctor,
        created_by=codex_env.patient_user_a,
        appointment_type=Appointment.AppointmentType.ONLINE,
        status=Appointment.Status.SCHEDULED,
        requested_datetime=timezone.now() + timezone.timedelta(days=1),
        scheduled_datetime=timezone.now() + timezone.timedelta(days=1, hours=1),
        duration_minutes=30,
        reason="TEST-CODEX document consultation appointment",
    )
    consultation = OnlineConsultation.objects.create(
        patient=codex_env.patient_a,
        facility=codex_env.facility_a,
        doctor=codex_env.doctor,
        appointment=appointment,
        scheduled_start=appointment.scheduled_datetime,
        scheduled_end=appointment.scheduled_datetime + timezone.timedelta(minutes=30),
        status=OnlineConsultation.Status.SCHEDULED,
        jitsi_room_name=f"test-codex-room-{uuid4().hex}",
        created_by=codex_env.doctor,
    )

    document_response = doctor_client.post(
        "/documents/staff/create/",
        {
            "patient": str(codex_env.patient_a.pk),
            "consultation": str(consultation.pk),
            "encounter": "",
            "referral": "",
            "document_type": MedicalDocument.DocumentType.RECOMMENDATION,
            "title": "TEST-CODEX medical document",
            "content": "TEST-CODEX document content",
            "status": MedicalDocument.Status.ISSUED,
            "valid_until": "",
        },
        follow=False,
    )
    assert document_response.status_code == 302
    document = MedicalDocument.objects.get(title="TEST-CODEX medical document")
    assert doctor_client.get("/documents/staff/").status_code == 200
    assert patient_client.get("/documents/my/").status_code == 200
    assert patient_client.get(f"/documents/my/{document.pk}/").status_code == 200
    assert patient_client.get(f"/documents/print/document/{document.pk}/").status_code == 200

    prescription_response = doctor_client.post(
        "/documents/staff/prescriptions/create/",
        {
            "patient": str(codex_env.patient_a.pk),
            "consultation": str(consultation.pk),
            "status": Prescription.Status.ISSUED,
            "notes": "TEST-CODEX prescription reason",
            "items-TOTAL_FORMS": "2",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "0",
            "items-MAX_NUM_FORMS": "1000",
            "items-0-medication_name": "TEST-CODEX Paracetamol",
            "items-0-dosage": "500 mg",
            "items-0-frequency": "2 times daily",
            "items-0-duration": "3 days",
            "items-0-instructions": "TEST-CODEX instructions",
            "items-1-medication_name": "",
            "items-1-dosage": "",
            "items-1-frequency": "",
            "items-1-duration": "",
            "items-1-instructions": "",
        },
        follow=False,
    )
    assert prescription_response.status_code == 302
    prescription = Prescription.objects.get(notes="TEST-CODEX prescription reason")
    assert prescription.items.filter(medication_name="TEST-CODEX Paracetamol").exists()
    assert patient_client.get("/documents/my/prescriptions/").status_code == 200
    assert patient_client.get(f"/documents/my/prescriptions/{prescription.pk}/").status_code == 200
    assert patient_client.get(f"/documents/print/prescription/{prescription.pk}/").status_code == 200

    staff_file_response = doctor_client.post(
        "/documents/staff/files/upload/",
        {
            "patient": str(codex_env.patient_a.pk),
            "related_consultation": str(consultation.pk),
            "result_type": PatientFile.ResultType.DOCUMENT,
            "title": "TEST-CODEX staff file",
            "description": "TEST-CODEX staff file description",
            "result_date": timezone.localdate().isoformat(),
            "file": SimpleUploadedFile("test-codex-staff.pdf", b"TEST-CODEX staff file"),
        },
        follow=False,
    )
    assert staff_file_response.status_code == 302
    staff_file = PatientFile.objects.get(title="TEST-CODEX staff file")
    assert patient_client.get("/documents/my/files/").status_code == 200
    assert patient_client.get(f"/documents/files/{staff_file.pk}/").status_code == 200
    download_response = patient_client.get(f"/documents/files/{staff_file.pk}/download/")
    assert download_response.status_code == 200
    assert "attachment" in download_response.headers["Content-Disposition"]

    valid_patient_file_response = patient_client.post(
        "/documents/my/files/upload/",
        {
            "patient": str(codex_env.patient_a.pk),
            "related_consultation": "",
            "result_type": PatientFile.ResultType.DOCUMENT,
            "title": "TEST-CODEX patient file",
            "description": "TEST-CODEX patient file description",
            "result_date": timezone.localdate().isoformat(),
            "file": SimpleUploadedFile("test-codex-patient.pdf", b"TEST-CODEX patient file"),
        },
        follow=False,
    )
    assert valid_patient_file_response.status_code == 302
    patient_file = PatientFile.objects.get(title="TEST-CODEX patient file")
    assert patient_file.patient_id == codex_env.patient_a.pk

    tamper_response = patient_client.post(
        "/documents/my/files/upload/",
        {
            "patient": str(codex_env.patient_b.pk),
            "related_consultation": "",
            "result_type": PatientFile.ResultType.DOCUMENT,
            "title": "TEST-CODEX tamper file",
            "description": "TEST-CODEX tamper description",
            "result_date": timezone.localdate().isoformat(),
            "file": SimpleUploadedFile("test-codex-tamper.pdf", b"TEST-CODEX tamper file"),
        },
    )
    assert tamper_response.status_code == 200
    assert not PatientFile.objects.filter(title="TEST-CODEX tamper file", patient=codex_env.patient_b).exists()


def test_monitoring_flow_for_doctor_and_patient(codex_env):
    doctor_client = _make_client(codex_env.doctor)
    patient_client = _make_client(codex_env.patient_user_a)

    doctor_response = doctor_client.post(
        f"/monitoring/patient/{codex_env.patient_a.pk}/create/",
        {
            "recorded_at": _datetime_input(timezone.now()),
            "systolic_bp": "120",
            "diastolic_bp": "80",
            "pulse": "72",
            "temperature": "36.6",
            "spo2": "98",
            "glucose": "5.2",
            "weight": "70",
            "comment": "TEST-CODEX doctor reading",
        },
        follow=False,
    )
    assert doctor_response.status_code == 302
    doctor_reading = VitalReading.objects.get(comment="TEST-CODEX doctor reading")
    assert doctor_reading.source == VitalReading.Source.DOCTOR_MANUAL

    patient_response = patient_client.post(
        "/monitoring/my/create/",
        {
            "recorded_at": _datetime_input(timezone.now()),
            "systolic_bp": "118",
            "diastolic_bp": "78",
            "pulse": "70",
            "temperature": "36.5",
            "spo2": "99",
            "glucose": "5.1",
            "weight": "69",
            "comment": "TEST-CODEX patient reading",
        },
        follow=False,
    )
    assert patient_response.status_code == 302
    patient_reading = VitalReading.objects.get(comment="TEST-CODEX patient reading")
    assert patient_reading.source == VitalReading.Source.PATIENT_MANUAL

    assert patient_client.get("/monitoring/my/").status_code == 200
    assert doctor_client.get(f"/monitoring/patient/{codex_env.patient_a.pk}/").status_code == 200


def test_manager_reports_and_current_behavior_permissions(codex_env):
    patient_client = _make_client(codex_env.patient_user_a)
    manager_client = _make_client(codex_env.manager)
    appointment = Appointment.objects.create(
        patient=codex_env.patient_a,
        facility=codex_env.facility_a,
        doctor=codex_env.doctor,
        created_by=codex_env.patient_user_a,
        appointment_type=Appointment.AppointmentType.OFFLINE,
        status=Appointment.Status.REQUESTED,
        requested_datetime=timezone.now() + timezone.timedelta(days=2),
        reason="TEST-CODEX manager current behavior appointment",
    )

    assert manager_client.get("/dashboard/").status_code == 200
    assert manager_client.get("/reports/").status_code == 200
    assert manager_client.get("/reports/telemedicine/").status_code == 200
    csv_response = manager_client.get("/reports/telemedicine/", {"format": "csv"})
    assert csv_response.status_code == 200
    assert csv_response["Content-Type"].startswith("text/csv")

    assert manager_client.get("/patients/").status_code == 200
    assert manager_client.get("/encounters/").status_code == 200
    assert manager_client.get("/referrals/").status_code == 200
    assert manager_client.get("/visits/").status_code == 200
    assert manager_client.get("/prevention/").status_code == 200
    assert manager_client.get("/appointments/staff/").status_code == 200
    assert manager_client.get("/documents/staff/").status_code == 200

    assert manager_client.get("/appointments/staff/").status_code == 200
    assert manager_client.get(f"/appointments/staff/{appointment.pk}/edit/").status_code == 200
    assert manager_client.get("/documents/staff/create/").status_code == 200
    assert manager_client.get("/documents/staff/prescriptions/create/").status_code == 200

    forbidden_manager_creates = [
        "/patients/create/",
        "/encounters/create/",
        "/referrals/create/",
        "/visits/create/",
        "/prevention/create/",
    ]
    for url in forbidden_manager_creates:
        response = manager_client.get(url)
        assert response.status_code != 200, url

    forbidden_urls = [
        "/patients/",
        "/patients/create/",
        f"/patients/{codex_env.patient_b.pk}/",
        f"/patients/{codex_env.patient_b.pk}/edit/",
        "/encounters/",
        "/encounters/create/",
        "/referrals/",
        "/referrals/create/",
        "/visits/",
        "/prevention/",
        "/reports/",
        "/reports/telemedicine/",
    ]
    for url in forbidden_urls:
        response = patient_client.get(url)
        assert response.status_code != 200, url


def test_patient_privacy_and_object_level_access(codex_env):
    doctor_client = _make_client(codex_env.doctor)
    patient_client = _make_client(codex_env.patient_user_a)

    encounter_b = Encounter.objects.create(
        patient=codex_env.patient_b,
        facility=codex_env.facility_a,
        clinician=codex_env.doctor.employee_profile,
        encounter_type=Encounter.ENCOUNTER_TYPES[0][0],
        encounter_date=timezone.localdate(),
        reason_for_visit="TEST-CODEX foreign patient encounter",
        diagnosis_text="TEST-CODEX foreign diagnosis",
        services_provided="TEST-CODEX foreign service",
        result_type=Encounter.RESULT_TYPES[0][0],
        notes="TEST-CODEX foreign notes",
    )
    Referral.objects.create(
        patient=codex_env.patient_b,
        source_encounter=encounter_b,
        created_by=codex_env.doctor.employee_profile,
        destination_org="TEST-CODEX foreign org",
        destination_specialist="TEST-CODEX foreign specialist",
        reason="TEST-CODEX foreign referral",
        priority=Referral.PRIORITY_CHOICES[0][0],
        status=Referral.STATUS_CHOICES[0][0],
        referral_date=timezone.localdate(),
    )
    appointment_b = Appointment.objects.create(
        patient=codex_env.patient_b,
        facility=codex_env.facility_a,
        doctor=codex_env.doctor,
        created_by=codex_env.patient_user_b,
        appointment_type=Appointment.AppointmentType.ONLINE,
        status=Appointment.Status.SCHEDULED,
        requested_datetime=timezone.now() + timezone.timedelta(days=2),
        scheduled_datetime=timezone.now() + timezone.timedelta(days=2, hours=1),
        duration_minutes=30,
        reason="TEST-CODEX foreign appointment",
    )
    consultation_b = OnlineConsultation.objects.create(
        patient=codex_env.patient_b,
        facility=codex_env.facility_a,
        doctor=codex_env.doctor,
        appointment=appointment_b,
        scheduled_start=appointment_b.scheduled_datetime,
        scheduled_end=appointment_b.scheduled_datetime + timezone.timedelta(minutes=30),
        status=OnlineConsultation.Status.SCHEDULED,
        jitsi_room_name=f"test-codex-room-{uuid4().hex}",
        created_by=codex_env.doctor,
    )
    document_b = MedicalDocument.objects.create(
        patient=codex_env.patient_b,
        created_by=codex_env.doctor,
        document_type=MedicalDocument.DocumentType.RECOMMENDATION,
        title="TEST-CODEX foreign document",
        content="TEST-CODEX foreign document content",
        status=MedicalDocument.Status.ISSUED,
    )
    prescription_b = Prescription.objects.create(
        patient=codex_env.patient_b,
        doctor=codex_env.doctor,
        status=Prescription.Status.ISSUED,
        notes="TEST-CODEX foreign prescription",
    )
    file_b = PatientFile.objects.create(
        patient=codex_env.patient_b,
        uploaded_by=codex_env.doctor,
        result_type=PatientFile.ResultType.DOCUMENT,
        title="TEST-CODEX foreign file",
        result_date=timezone.localdate(),
    )
    file_b.file.save("test-codex-foreign.pdf", SimpleUploadedFile("test-codex-foreign.pdf", b"TEST-CODEX foreign pdf"), save=True)
    VitalReading.objects.create(
        patient=codex_env.patient_b,
        recorded_by=codex_env.doctor,
        source=VitalReading.Source.DOCTOR_MANUAL,
        recorded_at=timezone.now(),
        comment="TEST-CODEX foreign reading",
    )

    forbidden_direct_urls = [
        f"/patients/{codex_env.patient_b.pk}/",
        f"/patients/{codex_env.patient_b.pk}/edit/",
        f"/appointments/my/{appointment_b.pk}/",
        f"/telemedicine/consultations/{consultation_b.pk}/",
        f"/telemedicine/consultations/{consultation_b.pk}/room/",
        f"/documents/my/{document_b.pk}/",
        f"/documents/my/prescriptions/{prescription_b.pk}/",
        f"/documents/files/{file_b.pk}/",
        f"/documents/files/{file_b.pk}/download/",
        f"/monitoring/patient/{codex_env.patient_b.pk}/",
    ]
    for url in forbidden_direct_urls:
        response = patient_client.get(url)
        assert response.status_code != 200, url
        assert b"TEST-CODEX foreign" not in response.content

    my_encounters = patient_client.get("/patients/my/encounters/")
    my_referrals = patient_client.get("/patients/my/referrals/")
    assert my_encounters.status_code == 200
    assert my_referrals.status_code == 200
    assert b"TEST-CODEX foreign patient encounter" not in my_encounters.content
    assert b"TEST-CODEX foreign referral" not in my_referrals.content

    assert doctor_client.get(f"/patients/{codex_env.patient_b.pk}/").status_code == 200


def test_facility_isolation_for_clinician_exports_and_direct_access(codex_env):
    Encounter.objects.create(
        patient=codex_env.patient_c,
        facility=codex_env.facility_b,
        clinician=codex_env.doctor_b.employee_profile,
        encounter_type=Encounter.ENCOUNTER_TYPES[0][0],
        encounter_date=timezone.localdate(),
        reason_for_visit="TEST-CODEX facility-b encounter",
        diagnosis_text="TEST-CODEX facility-b diagnosis",
        services_provided="TEST-CODEX facility-b services",
        result_type=Encounter.RESULT_TYPES[0][0],
        notes="TEST-CODEX facility-b notes",
    )
    appointment_c = Appointment.objects.create(
        patient=codex_env.patient_c,
        facility=codex_env.facility_b,
        doctor=codex_env.doctor_b,
        created_by=codex_env.patient_user_c,
        appointment_type=Appointment.AppointmentType.OFFLINE,
        status=Appointment.Status.REQUESTED,
        requested_datetime=timezone.now() + timezone.timedelta(days=5),
        reason="TEST-CODEX facility-b appointment",
    )

    doctor_a_client = _make_client(codex_env.doctor)
    export_response = doctor_a_client.get("/encounters/export/")
    assert export_response.status_code == 200
    assert "TEST-CODEX facility-b encounter" not in export_response.content.decode("utf-8")
    assert doctor_a_client.get(f"/patients/{codex_env.patient_c.pk}/").status_code != 200
    assert doctor_a_client.get(f"/appointments/staff/{appointment_c.pk}/").status_code != 200

    manager_client = _make_client(codex_env.manager)
    manager_appointment_access = manager_client.get(f"/appointments/staff/{appointment_c.pk}/")
    assert manager_appointment_access.status_code == 200


def test_audit_logs_are_written_for_key_workflows(codex_env):
    registrator_client = _make_client(codex_env.registrator)
    doctor_client = _make_client(codex_env.doctor)
    patient_client = _make_client(codex_env.patient_user_a)

    create_patient_response = registrator_client.post(
        "/patients/create/",
        {
            "last_name": "TEST-CODEX-AUDIT",
            "first_name": "Patient",
            "middle_name": "Auto",
            "iin": "100000000199",
            "birth_date": "1990-01-01",
            "sex": "female",
            "phone": "+77000000031",
            "address": "TEST-CODEX audit address",
            "settlement_name": codex_env.facility_a.settlement_name,
            "facility": str(codex_env.facility_a.pk),
            "social_category": "general",
            "risk_level": "low",
            "attachment_date": timezone.localdate().isoformat(),
            "notes": "TEST-CODEX audit patient",
            "is_active": "on",
            "create_portal_account": "",
            "portal_username": "",
            "portal_password": "",
        },
        follow=False,
    )
    assert create_patient_response.status_code == 302
    created_patient = Patient.objects.get(iin="100000000199")

    encounter_response = doctor_client.post(
        "/encounters/create/",
        {
            "patient": str(created_patient.pk),
            "facility": str(codex_env.facility_a.pk),
            "clinician": str(codex_env.doctor.employee_profile.pk),
            "encounter_type": Encounter.ENCOUNTER_TYPES[0][0],
            "encounter_date": timezone.localdate().isoformat(),
            "reason_for_visit": "TEST-CODEX audit encounter",
            "diagnosis_text": "TEST-CODEX audit diagnosis",
            "services_provided": "TEST-CODEX audit services",
            "result_type": Encounter.RESULT_TYPES[0][0],
            "next_visit_date": "",
            "notes": "TEST-CODEX audit notes",
        },
        follow=False,
    )
    assert encounter_response.status_code == 302
    encounter = Encounter.objects.get(reason_for_visit="TEST-CODEX audit encounter")

    referral_response = doctor_client.post(
        "/referrals/create/",
        {
            "patient": str(created_patient.pk),
            "source_encounter": str(encounter.pk),
            "created_by": str(codex_env.doctor.employee_profile.pk),
            "destination_org": "TEST-CODEX audit org",
            "destination_specialist": "TEST-CODEX audit specialist",
            "reason": "TEST-CODEX audit referral",
            "priority": Referral.PRIORITY_CHOICES[0][0],
            "status": Referral.STATUS_CHOICES[0][0],
            "referral_date": timezone.localdate().isoformat(),
            "result_note": "",
        },
        follow=False,
    )
    assert referral_response.status_code == 302
    referral = Referral.objects.get(reason="TEST-CODEX audit referral")

    appointment = Appointment.objects.create(
        patient=codex_env.patient_a,
        facility=codex_env.facility_a,
        doctor=codex_env.doctor,
        created_by=codex_env.patient_user_a,
        appointment_type=Appointment.AppointmentType.ONLINE,
        status=Appointment.Status.SCHEDULED,
        requested_datetime=timezone.now() + timezone.timedelta(days=1),
        scheduled_datetime=timezone.now() + timezone.timedelta(days=1, hours=1),
        duration_minutes=30,
        reason="TEST-CODEX audit telemedicine",
    )
    consultation = OnlineConsultation.objects.create(
        patient=codex_env.patient_a,
        facility=codex_env.facility_a,
        doctor=codex_env.doctor,
        appointment=appointment,
        scheduled_start=appointment.scheduled_datetime,
        scheduled_end=appointment.scheduled_datetime + timezone.timedelta(minutes=30),
        status=OnlineConsultation.Status.SCHEDULED,
        jitsi_room_name=f"test-codex-room-{uuid4().hex}",
        created_by=codex_env.doctor,
    )
    consent_response = patient_client.post(f"/telemedicine/consultations/{consultation.pk}/consent/", follow=False)
    assert consent_response.status_code == 302

    actions = set(
        AuditLog.objects.filter(
            entity_id__in=[str(created_patient.pk), str(encounter.pk), str(referral.pk), str(consultation.pk)]
        ).values_list("action", flat=True)
    )
    assert "create" in actions
    assert "accept_consent" in actions
