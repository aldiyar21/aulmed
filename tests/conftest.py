from __future__ import annotations

import pytest
from django.contrib.auth.models import Group, User
from django.test import Client
from django.utils import timezone

from apps.accounts.models import EmployeeProfile
from apps.accounts.services import ensure_role_groups
from apps.appointments.models import Appointment
from apps.facilities.models import Facility
from apps.patients.models import Patient
from apps.telemedicine.services import ensure_online_consultation_for_appointment


@pytest.fixture
def facility(db):
    return Facility.objects.create(
        name="ФАП Тест",
        facility_type="fap",
        region="Кызылординская область",
        district="Тестовый район",
        settlement_name="Аул Тест",
        address="ул. Тестовая, 1",
        phone="+77000000001",
    )


@pytest.fixture
def role_setup(db):
    ensure_role_groups()


@pytest.fixture
def create_user(db, role_setup, facility):
    def _create_user(username: str, group_name: str, role_code: str = "clinician"):
        user = User.objects.create_user(username=username, password="demo12345")
        user.groups.set([Group.objects.get(name=group_name)])
        if role_code != "patient":
            EmployeeProfile.objects.create(
                user=user,
                facility=facility,
                position="Тестовая роль",
                role_code=role_code,
                phone="+77000000002",
            )
        return user

    return _create_user


@pytest.fixture
def registrar_user(create_user):
    return create_user("registrar_test", "Регистратор", "registrar")


@pytest.fixture
def clinician_user(create_user):
    return create_user("clinician_test", "Медработник", "clinician")


@pytest.fixture
def manager_user(create_user):
    return create_user("manager_test", "Руководитель", "manager")


@pytest.fixture
def admin_user(create_user):
    return create_user("admin_test", "Администратор системы", "admin")


@pytest.fixture
def patient_user(create_user):
    return create_user("patient_test", "Пациент", "patient")


@pytest.fixture
def other_patient_user(create_user):
    return create_user("patient_other", "Пациент", "patient")


@pytest.fixture
def authed_client():
    return Client()


@pytest.fixture
def patient(db, facility):
    return Patient.objects.create(
        last_name="Иванов",
        first_name="Иван",
        middle_name="Иванович",
        iin="123456789012",
        birth_date=timezone.localdate().replace(year=1990),
        sex="male",
        phone="+77000000003",
        address="ул. Центральная, 5",
        settlement_name=facility.settlement_name,
        facility=facility,
        social_category="general",
        risk_level="low",
        attachment_date=timezone.localdate(),
    )


@pytest.fixture
def linked_patient(patient, patient_user):
    patient.patient_user = patient_user
    patient.save(update_fields=["patient_user"])
    return patient


@pytest.fixture
def other_patient(db, facility):
    return Patient.objects.create(
        last_name="Петров",
        first_name="Петр",
        middle_name="Петрович",
        iin="223456789012",
        birth_date=timezone.localdate().replace(year=1991),
        sex="male",
        phone="+77000000004",
        address="ул. Степная, 6",
        settlement_name=facility.settlement_name,
        facility=facility,
        social_category="general",
        risk_level="low",
        attachment_date=timezone.localdate(),
    )


@pytest.fixture
def linked_other_patient(other_patient, other_patient_user):
    other_patient.patient_user = other_patient_user
    other_patient.save(update_fields=["patient_user"])
    return other_patient


@pytest.fixture
def online_appointment(linked_patient, clinician_user):
    appointment = Appointment.objects.create(
        patient=linked_patient,
        facility=linked_patient.facility,
        doctor=clinician_user,
        created_by=clinician_user,
        appointment_type=Appointment.AppointmentType.ONLINE,
        status=Appointment.Status.SCHEDULED,
        requested_datetime=timezone.now() + timezone.timedelta(days=1),
        scheduled_datetime=timezone.now() + timezone.timedelta(days=1, hours=1),
        duration_minutes=30,
        reason="Онлайн консультация",
    )
    ensure_online_consultation_for_appointment(appointment=appointment, created_by=clinician_user)
    return appointment
