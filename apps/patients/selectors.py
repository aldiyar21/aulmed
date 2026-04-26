from __future__ import annotations

from django.db.models import Q, QuerySet
from django.utils import timezone

from apps.accounts.services import get_linked_patient, user_is_patient
from apps.patients.models import Patient


def patient_queryset_for_user(user) -> QuerySet[Patient]:
    qs = Patient.all_objects.select_related("facility", "patient_user").prefetch_related(
        "conditions",
        "encounters",
        "prevention_events",
        "referrals",
    )
    if user.is_superuser:
        return qs
    if user_is_patient(user):
        linked_patient = get_linked_patient(user)
        return qs.filter(pk=linked_patient.pk) if linked_patient else qs.none()
    if hasattr(user, "employee_profile") and user.employee_profile.facility_id:
        return qs.filter(facility_id=user.employee_profile.facility_id)
    return qs


def filter_patients(qs: QuerySet[Patient], data: dict) -> QuerySet[Patient]:
    query = data.get("q")
    if query:
        qs = qs.filter(
            Q(last_name__icontains=query)
            | Q(first_name__icontains=query)
            | Q(middle_name__icontains=query)
            | Q(iin__icontains=query)
            | Q(phone__icontains=query)
        )
    if data.get("settlement_name"):
        qs = qs.filter(settlement_name__icontains=data["settlement_name"])
    if data.get("facility"):
        facility = data["facility"]
        facility_id = facility.pk if hasattr(facility, "pk") else facility
        qs = qs.filter(facility_id=facility_id)
    if data.get("sex"):
        qs = qs.filter(sex=data["sex"])
    if data.get("risk_level"):
        qs = qs.filter(risk_level=data["risk_level"])
    if data.get("is_active") in [True, False]:
        qs = qs.filter(is_active=data["is_active"])
    age_group = data.get("age_group")
    today = timezone.localdate()
    if age_group == "child":
        qs = qs.filter(birth_date__gt=today.replace(year=today.year - 18))
    elif age_group == "adult":
        qs = qs.filter(
            birth_date__lte=today.replace(year=today.year - 18),
            birth_date__gt=today.replace(year=today.year - 60),
        )
    elif age_group == "elderly":
        qs = qs.filter(birth_date__lte=today.replace(year=today.year - 60))
    return qs
