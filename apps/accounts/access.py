from __future__ import annotations

from django.core.exceptions import PermissionDenied

from apps.accounts.services import get_linked_patient, user_is_manager_or_admin, user_is_patient


def user_can_access_patient(user, patient) -> bool:
    if not user.is_authenticated:
        return False
    if user.is_superuser or user_is_manager_or_admin(user):
        return True
    if user_is_patient(user):
        linked_patient = get_linked_patient(user)
        return bool(linked_patient and linked_patient.pk == patient.pk)
    if hasattr(user, "employee_profile") and user.employee_profile.facility_id:
        return user.employee_profile.facility_id == patient.facility_id
    return False


def patient_owns_resource(user, resource) -> bool:
    patient = getattr(resource, "patient", None)
    linked_patient = get_linked_patient(user)
    return bool(user_is_patient(user) and linked_patient and patient and linked_patient.pk == patient.pk)


def staff_or_patient_resource_access(user, resource) -> bool:
    patient = getattr(resource, "patient", None)
    return bool(patient and user_can_access_patient(user, patient))


def doctor_or_patient_consultation_access(user, consultation) -> bool:
    if not user.is_authenticated:
        return False
    if user.is_superuser or user_is_manager_or_admin(user):
        return True
    if user_is_patient(user):
        return patient_owns_resource(user, consultation)
    if consultation.doctor_id == user.pk:
        return True
    if hasattr(user, "employee_profile") and user.employee_profile.facility_id:
        return user.employee_profile.facility_id == consultation.facility_id
    return False


def require_access(condition: bool) -> None:
    if not condition:
        raise PermissionDenied
