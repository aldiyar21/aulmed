from __future__ import annotations

import pytest
from django.contrib.auth.models import Group, User
from django.test import Client
from django.utils import timezone

from apps.accounts.models import EmployeeProfile
from apps.accounts.services import ensure_role_groups
from apps.facilities.models import Facility
from apps.patients.models import Patient


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
