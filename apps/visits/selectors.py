from django.db.models import QuerySet
from django.utils import timezone

from apps.visits.models import HomeVisit


def visit_queryset_for_user(user) -> QuerySet[HomeVisit]:
    qs = HomeVisit.objects.select_related("facility", "assigned_employee", "assigned_employee__user").prefetch_related(
        "visit_patients__patient"
    )
    if user.is_superuser:
        return qs
    if hasattr(user, "employee_profile") and user.employee_profile.facility_id:
        qs = qs.filter(facility_id=user.employee_profile.facility_id)
    return qs


def filter_visits(qs: QuerySet[HomeVisit], data: dict) -> QuerySet[HomeVisit]:
    if data.get("planned_date"):
        qs = qs.filter(planned_date=data["planned_date"])
    if data.get("status"):
        qs = qs.filter(status=data["status"])
    if data.get("assigned_employee"):
        qs = qs.filter(assigned_employee=data["assigned_employee"])
    if data.get("settlement_name"):
        qs = qs.filter(settlement_name__icontains=data["settlement_name"])
    if data.get("facility"):
        qs = qs.filter(facility=data["facility"])
    return qs


def visits_for_today(qs: QuerySet[HomeVisit]) -> QuerySet[HomeVisit]:
    return qs.filter(planned_date=timezone.localdate())
