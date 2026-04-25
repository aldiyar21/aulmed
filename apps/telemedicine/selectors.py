from __future__ import annotations

from django.db.models import Q, QuerySet

from apps.accounts.services import get_linked_patient, user_is_manager_or_admin, user_is_patient
from apps.telemedicine.models import OnlineConsultation, Teleconsilium


def consultation_queryset_for_user(user) -> QuerySet[OnlineConsultation]:
    qs = OnlineConsultation.objects.select_related("patient", "doctor", "facility", "appointment")
    if user.is_superuser or user_is_manager_or_admin(user):
        return qs
    if user_is_patient(user):
        linked_patient = get_linked_patient(user)
        return qs.filter(patient=linked_patient) if linked_patient else qs.none()
    if hasattr(user, "employee_profile") and user.employee_profile.facility_id:
        return qs.filter(Q(doctor=user) | Q(facility_id=user.employee_profile.facility_id))
    return qs.none()


def filter_consultations(qs: QuerySet[OnlineConsultation], data: dict) -> QuerySet[OnlineConsultation]:
    if data.get("status"):
        qs = qs.filter(status=data["status"])
    if data.get("date_from"):
        qs = qs.filter(scheduled_start__date__gte=data["date_from"])
    if data.get("date_to"):
        qs = qs.filter(scheduled_start__date__lte=data["date_to"])
    return qs


def teleconsilium_queryset_for_user(user) -> QuerySet[Teleconsilium]:
    qs = Teleconsilium.objects.select_related("patient", "facility", "primary_doctor").prefetch_related("invited_doctors")
    if user.is_superuser or user_is_manager_or_admin(user):
        return qs
    if hasattr(user, "employee_profile") and user.employee_profile.facility_id:
        return qs.filter(Q(primary_doctor=user) | Q(invited_doctors=user) | Q(facility_id=user.employee_profile.facility_id)).distinct()
    return qs.none()
