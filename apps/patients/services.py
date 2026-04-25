from __future__ import annotations

from django.contrib.auth.models import User

from apps.audit.services import log_action
from apps.patients.models import Patient


def create_patient(*, user: User, cleaned_data: dict) -> Patient:
    """Создает пациента и пишет запись в аудит."""
    patient = Patient.objects.create(**cleaned_data)
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
