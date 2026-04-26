from __future__ import annotations

from django.contrib.auth.models import Group, User

from apps.accounts.services import ensure_role_groups
from apps.audit.services import log_action
from apps.patients.models import Patient


def _create_patient_portal_user(*, username: str, password: str) -> User:
    ensure_role_groups()
    user = User.objects.create_user(username=username, password=password)
    user.groups.set([Group.objects.get(name="Пациент")])
    return user


def create_patient(*, user: User, cleaned_data: dict) -> Patient:
    """Создает пациента и пишет запись в аудит."""
    create_portal_account = cleaned_data.pop("create_portal_account", False)
    portal_username = cleaned_data.pop("portal_username", "")
    portal_password = cleaned_data.pop("portal_password", "")
    patient_user = None
    if create_portal_account:
        patient_user = _create_patient_portal_user(username=portal_username, password=portal_password)
        cleaned_data["patient_user"] = patient_user
    patient = Patient.objects.create(**cleaned_data)
    patient._portal_account_created = bool(patient_user)
    patient._portal_credentials = {"username": portal_username, "password": portal_password} if patient_user else None
    log_action(
        user=user,
        action="create",
        entity_type="Patient",
        entity_id=patient.pk,
        description=f"Создан пациент {patient}",
        changes=cleaned_data,
    )
    return patient


def update_patient(*, user: User, patient: Patient, cleaned_data: dict) -> Patient:
    create_portal_account = cleaned_data.pop("create_portal_account", False)
    portal_username = cleaned_data.pop("portal_username", "")
    portal_password = cleaned_data.pop("portal_password", "")
    if create_portal_account and not patient.patient_user_id:
        patient.patient_user = _create_patient_portal_user(username=portal_username, password=portal_password)
        patient._portal_account_created = True
        patient._portal_credentials = {"username": portal_username, "password": portal_password}
    for field, value in cleaned_data.items():
        setattr(patient, field, value)
    patient.save()
    log_action(
        user=user,
        action="update",
        entity_type="Patient",
        entity_id=patient.pk,
        description=f"Обновлен пациент {patient}",
        changes=cleaned_data,
    )
    return patient
