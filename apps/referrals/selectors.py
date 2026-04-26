from django.db.models import QuerySet

from apps.accounts.services import get_linked_patient, user_is_patient
from apps.referrals.models import Referral


def referral_queryset_for_user(user) -> QuerySet[Referral]:
    qs = Referral.objects.select_related(
        "patient",
        "patient__facility",
        "source_encounter",
        "created_by",
        "created_by__user",
    )
    if user.is_superuser:
        return qs
    if user_is_patient(user):
        linked_patient = get_linked_patient(user)
        return qs.filter(patient=linked_patient) if linked_patient else qs.none()
    if hasattr(user, "employee_profile") and user.employee_profile.facility_id:
        qs = qs.filter(patient__facility_id=user.employee_profile.facility_id)
    return qs


def filter_referrals(qs: QuerySet[Referral], data: dict) -> QuerySet[Referral]:
    if data.get("status"):
        qs = qs.filter(status=data["status"])
    if data.get("priority"):
        qs = qs.filter(priority=data["priority"])
    if data.get("date_from"):
        qs = qs.filter(referral_date__gte=data["date_from"])
    if data.get("date_to"):
        qs = qs.filter(referral_date__lte=data["date_to"])
    return qs
