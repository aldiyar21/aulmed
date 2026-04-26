from __future__ import annotations

from django.db.models import QuerySet

from apps.accounts.services import get_linked_patient, user_is_manager_or_admin, user_is_patient
from apps.monitoring.models import VitalReading


def vital_reading_queryset_for_user(user) -> QuerySet[VitalReading]:
    qs = VitalReading.objects.select_related("patient", "recorded_by")
    if user.is_superuser or user_is_manager_or_admin(user):
        return qs
    if user_is_patient(user):
        linked_patient = get_linked_patient(user)
        return qs.filter(patient=linked_patient) if linked_patient else qs.none()
    if hasattr(user, "employee_profile") and user.employee_profile.facility_id:
        return qs.filter(patient__facility_id=user.employee_profile.facility_id)
    return qs.none()
