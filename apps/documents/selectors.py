from __future__ import annotations

from django.db.models import QuerySet

from apps.accounts.services import get_linked_patient, user_is_manager_or_admin, user_is_patient
from apps.documents.models import MedicalDocument, PatientFile, Prescription


def medical_document_queryset_for_user(user) -> QuerySet[MedicalDocument]:
    qs = MedicalDocument.objects.select_related("patient", "created_by", "consultation", "encounter", "referral").order_by(
        "-issued_at", "-created_at", "-pk"
    )
    if user.is_superuser or user_is_manager_or_admin(user):
        return qs
    if user_is_patient(user):
        linked_patient = get_linked_patient(user)
        return qs.filter(patient=linked_patient) if linked_patient else qs.none()
    if hasattr(user, "employee_profile") and user.employee_profile.facility_id:
        return qs.filter(patient__facility_id=user.employee_profile.facility_id)
    return qs.none()


def prescription_queryset_for_user(user) -> QuerySet[Prescription]:
    qs = Prescription.objects.select_related("patient", "doctor", "consultation").prefetch_related("items").order_by(
        "-issued_at", "-created_at", "-pk"
    )
    if user.is_superuser or user_is_manager_or_admin(user):
        return qs
    if user_is_patient(user):
        linked_patient = get_linked_patient(user)
        return qs.filter(patient=linked_patient) if linked_patient else qs.none()
    if hasattr(user, "employee_profile") and user.employee_profile.facility_id:
        return qs.filter(patient__facility_id=user.employee_profile.facility_id)
    return qs.none()


def patient_file_queryset_for_user(user) -> QuerySet[PatientFile]:
    qs = PatientFile.objects.select_related("patient", "uploaded_by", "related_consultation").order_by(
        "-result_date", "-created_at", "-pk"
    )
    if user.is_superuser or user_is_manager_or_admin(user):
        return qs
    if user_is_patient(user):
        linked_patient = get_linked_patient(user)
        return qs.filter(patient=linked_patient) if linked_patient else qs.none()
    if hasattr(user, "employee_profile") and user.employee_profile.facility_id:
        return qs.filter(patient__facility_id=user.employee_profile.facility_id)
    return qs.none()
