from django.db.models import QuerySet

from apps.prevention.models import PreventionEvent


def prevention_queryset_for_user(user) -> QuerySet[PreventionEvent]:
    qs = PreventionEvent.objects.select_related(
        "patient",
        "patient__facility",
        "assigned_employee",
        "assigned_employee__user",
    )
    if user.is_superuser:
        return qs
    if hasattr(user, "employee_profile") and user.employee_profile.facility_id:
        qs = qs.filter(patient__facility_id=user.employee_profile.facility_id)
    return qs


def filter_prevention(qs: QuerySet[PreventionEvent], data: dict) -> QuerySet[PreventionEvent]:
    if data.get("event_type"):
        qs = qs.filter(event_type=data["event_type"])
    if data.get("status"):
        qs = qs.filter(status=data["status"])
    if data.get("planned_date"):
        qs = qs.filter(planned_date=data["planned_date"])
    if data.get("assigned_employee"):
        qs = qs.filter(assigned_employee=data["assigned_employee"])
    return qs


def overdue_queryset(qs: QuerySet[PreventionEvent]) -> QuerySet[PreventionEvent]:
    return qs.filter(status="overdue").order_by("planned_date")
