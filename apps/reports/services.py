from __future__ import annotations

from datetime import date, timedelta

from django.db.models import Count
from django.utils.dateparse import parse_date
from django.utils.timezone import localdate

from apps.accounts.services import user_is_manager_or_admin
from apps.encounters.models import Encounter
from apps.patients.models import Patient
from apps.prevention.models import PreventionEvent
from apps.referrals.models import Referral
from apps.visits.models import HomeVisit


def _resolve_period(date_from: str | None, date_to: str | None) -> tuple[date, date]:
    today = localdate()
    start = parse_date(date_from) if date_from else today - timedelta(days=30)
    end = parse_date(date_to) if date_to else today
    return start or today - timedelta(days=30), end or today


def build_dashboard_metrics(*, user, date_from: str | None, date_to: str | None) -> dict:
    start, end = _resolve_period(date_from, date_to)
    patient_qs = Patient.objects.select_related("facility").active()
    encounter_qs = Encounter.objects.select_related("facility", "clinician", "patient")
    visit_qs = HomeVisit.objects.select_related("facility", "assigned_employee")
    prevention_qs = PreventionEvent.objects.select_related("patient", "assigned_employee")
    referral_qs = Referral.objects.select_related("patient", "created_by")

    if not user_is_manager_or_admin(user) and hasattr(user, "employee_profile") and user.employee_profile.facility_id:
        facility_id = user.employee_profile.facility_id
        patient_qs = patient_qs.filter(facility_id=facility_id)
        encounter_qs = encounter_qs.filter(facility_id=facility_id)
        visit_qs = visit_qs.filter(facility_id=facility_id)
        prevention_qs = prevention_qs.filter(patient__facility_id=facility_id)
        referral_qs = referral_qs.filter(patient__facility_id=facility_id)

    period_encounters = encounter_qs.filter(encounter_date__range=(start, end))
    period_visits = visit_qs.filter(planned_date__range=(start, end))

    return {
        "date_from": start,
        "date_to": end,
        "active_patients": patient_qs.count(),
        "encounters_count": period_encounters.count(),
        "visits_count": period_visits.count(),
        "overdue_prevention": prevention_qs.filter(status="overdue").count(),
        "active_referrals": referral_qs.exclude(status__in=["completed", "cancelled"]).count(),
        "encounter_distribution": list(
            period_encounters.values("encounter_type").annotate(total=Count("id")).order_by("-total")
        ),
        "patients_by_settlement": list(
            patient_qs.values("settlement_name").annotate(total=Count("id")).order_by("-total")[:10]
        ),
        "employee_load": list(
            period_encounters.values("clinician__user__first_name", "clinician__user__last_name")
            .annotate(total=Count("id"))
            .order_by("-total")[:10]
        ),
    }
