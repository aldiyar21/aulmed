from __future__ import annotations

from datetime import date, timedelta

from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, Q
from django.utils.dateparse import parse_date
from django.utils.timezone import localdate

from apps.accounts.services import user_is_manager_or_admin
from apps.appointments.models import Appointment
from apps.documents.models import MedicalDocument, Prescription
from apps.encounters.models import Encounter
from apps.monitoring.models import VitalReading
from apps.patients.models import Patient
from apps.prevention.models import PreventionEvent
from apps.referrals.models import Referral
from apps.telemedicine.models import OnlineConsultation, Teleconsilium
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


def build_telemedicine_metrics(*, user, date_from: str | None, date_to: str | None, facility=None, doctor=None) -> dict:
    start, end = _resolve_period(date_from, date_to)
    appointment_qs = Appointment.objects.select_related("facility", "patient", "doctor")
    consultation_qs = OnlineConsultation.objects.select_related("facility", "patient", "doctor")
    teleconsilium_qs = Teleconsilium.objects.select_related("facility", "patient", "primary_doctor")
    document_qs = MedicalDocument.objects.select_related("patient")
    prescription_qs = Prescription.objects.select_related("patient", "doctor")
    vital_qs = VitalReading.objects.select_related("patient")

    if hasattr(user, "employee_profile") and not user_is_manager_or_admin(user):
        consultation_qs = consultation_qs.filter(doctor=user)
        appointment_qs = appointment_qs.filter(doctor=user)
        prescription_qs = prescription_qs.filter(doctor=user)
        teleconsilium_qs = teleconsilium_qs.filter(Q(primary_doctor=user) | Q(invited_doctors=user)).distinct()
    if facility:
        appointment_qs = appointment_qs.filter(facility=facility)
        consultation_qs = consultation_qs.filter(facility=facility)
        teleconsilium_qs = teleconsilium_qs.filter(facility=facility)
        document_qs = document_qs.filter(patient__facility=facility)
        prescription_qs = prescription_qs.filter(patient__facility=facility)
        vital_qs = vital_qs.filter(patient__facility=facility)
    if doctor:
        appointment_qs = appointment_qs.filter(doctor=doctor)
        consultation_qs = consultation_qs.filter(doctor=doctor)
        prescription_qs = prescription_qs.filter(doctor=doctor)
        teleconsilium_qs = teleconsilium_qs.filter(Q(primary_doctor=doctor) | Q(invited_doctors=doctor)).distinct()

    appointment_period = appointment_qs.filter(created_at__date__range=(start, end))
    consultation_period = consultation_qs.filter(created_at__date__range=(start, end))
    teleconsilium_period = teleconsilium_qs.filter(created_at__date__range=(start, end))
    avg_wait = appointment_period.filter(scheduled_datetime__isnull=False).annotate(
        wait_time=ExpressionWrapper(F("scheduled_datetime") - F("requested_datetime"), output_field=DurationField())
    ).aggregate(avg=Avg("wait_time"))["avg"]

    return {
        "date_from": start,
        "date_to": end,
        "total_online_consultations": consultation_period.count(),
        "scheduled_consultations": consultation_period.filter(status="scheduled").count(),
        "completed_consultations": consultation_period.filter(status="completed").count(),
        "cancelled_consultations": consultation_period.filter(status="cancelled").count(),
        "average_wait_time": avg_wait,
        "consultations_by_facility": list(consultation_period.values("facility__name").annotate(total=Count("id")).order_by("-total")),
        "consultations_by_settlement": list(consultation_period.values("patient__settlement_name").annotate(total=Count("id")).order_by("-total")),
        "doctor_workload": list(consultation_period.values("doctor__username").annotate(total=Count("id")).order_by("-total")),
        "issued_medical_documents": document_qs.filter(status="issued", created_at__date__range=(start, end)).count(),
        "issued_prescriptions": prescription_qs.filter(status="issued", created_at__date__range=(start, end)).count(),
        "active_remote_monitoring_patients": vital_qs.filter(created_at__date__range=(start, end)).values("patient_id").distinct().count(),
        "appointments_by_status": list(appointment_period.values("status").annotate(total=Count("id")).order_by("-total")),
        "appointments_by_type": list(appointment_period.values("appointment_type").annotate(total=Count("id")).order_by("-total")),
        "teleconsiliums_count": teleconsilium_period.count(),
        "teleconsiliums_completed_count": teleconsilium_period.filter(status="completed").count(),
    }
