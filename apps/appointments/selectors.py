from __future__ import annotations

from django.db.models import QuerySet

from apps.accounts.services import get_linked_patient, user_is_manager_or_admin, user_is_patient
from apps.appointments.models import Appointment


def appointment_queryset_for_user(user) -> QuerySet[Appointment]:
    qs = Appointment.all_objects.select_related("patient", "facility", "doctor", "created_by")
    if user.is_superuser or user_is_manager_or_admin(user):
        return qs
    if user_is_patient(user):
        linked_patient = get_linked_patient(user)
        return qs.filter(patient=linked_patient) if linked_patient else qs.none()
    if hasattr(user, "employee_profile") and user.employee_profile.facility_id:
        return qs.filter(facility_id=user.employee_profile.facility_id)
    return qs.none()


def doctor_appointments(user) -> QuerySet[Appointment]:
    return appointment_queryset_for_user(user).filter(doctor=user)


def filter_appointments(qs: QuerySet[Appointment], data: dict) -> QuerySet[Appointment]:
    if data.get("status"):
        qs = qs.filter(status=data["status"])
    if data.get("appointment_type"):
        qs = qs.filter(appointment_type=data["appointment_type"])
    if data.get("date_from"):
        qs = qs.filter(requested_datetime__date__gte=data["date_from"])
    if data.get("date_to"):
        qs = qs.filter(requested_datetime__date__lte=data["date_to"])
    if data.get("facility"):
        qs = qs.filter(facility=data["facility"])
    return qs
