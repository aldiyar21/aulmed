import csv

from django import forms
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from apps.accounts.decorators import roles_required
from apps.accounts.services import user_is_manager_or_admin
from apps.facilities.models import Facility
from apps.reports.services import build_telemedicine_metrics


class TelemedicineReportFilterForm(forms.Form):
    date_from = forms.DateField(
        label=_("Date from"),
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    date_to = forms.DateField(
        label=_("Date to"),
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    facility = forms.ModelChoiceField(
        label=_("Facility"),
        queryset=Facility.objects.filter(is_active=True),
        required=False,
    )
    doctor = forms.ModelChoiceField(
        label=_("Doctor"),
        queryset=User.objects.filter(employee_profile__role_code="clinician"),
        required=False,
    )


def _telemedicine_csv_response(metrics: dict) -> HttpResponse:
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="telemedicine-report.csv"'
    writer = csv.writer(response)
    writer.writerow(["metric", "value"])
    writer.writerow(["date_from", metrics["date_from"]])
    writer.writerow(["date_to", metrics["date_to"]])
    writer.writerow(["total_online_consultations", metrics["total_online_consultations"]])
    writer.writerow(["scheduled_consultations", metrics["scheduled_consultations"]])
    writer.writerow(["completed_consultations", metrics["completed_consultations"]])
    writer.writerow(["cancelled_consultations", metrics["cancelled_consultations"]])
    writer.writerow(["average_wait_time", metrics["average_wait_time"] or ""])
    writer.writerow(["issued_medical_documents", metrics["issued_medical_documents"]])
    writer.writerow(["issued_prescriptions", metrics["issued_prescriptions"]])
    writer.writerow(["active_remote_monitoring_patients", metrics["active_remote_monitoring_patients"]])
    writer.writerow(["teleconsiliums_count", metrics["teleconsiliums_count"]])
    writer.writerow(["teleconsiliums_completed_count", metrics["teleconsiliums_completed_count"]])
    writer.writerow([])
    writer.writerow(["section", "label", "total"])
    for item in metrics["appointments_by_status"]:
        writer.writerow(["appointments_by_status", item["status"], item["total"]])
    for item in metrics["appointments_by_type"]:
        writer.writerow(["appointments_by_type", item["appointment_type"], item["total"]])
    for item in metrics["consultations_by_facility"]:
        writer.writerow(["consultations_by_facility", item["facility__name"], item["total"]])
    for item in metrics["consultations_by_settlement"]:
        writer.writerow(["consultations_by_settlement", item["patient__settlement_name"], item["total"]])
    for item in metrics["doctor_workload"]:
        writer.writerow(["doctor_workload", item["doctor__username"], item["total"]])
    return response


@roles_required("Администратор системы", "Руководитель", "Медработник")
def reports_view(request):
    return render(request, "reports/index.html")


@roles_required("Администратор системы", "Руководитель", "Медработник")
def telemedicine_reports_view(request):
    if not user_is_manager_or_admin(request.user) and not hasattr(request.user, "employee_profile"):
        return render(request, "errors/403.html", status=403)
    form = TelemedicineReportFilterForm(request.GET or None)
    metrics = build_telemedicine_metrics(
        user=request.user,
        date_from=request.GET.get("date_from"),
        date_to=request.GET.get("date_to"),
        facility=form.cleaned_data["facility"] if form.is_valid() else None,
        doctor=form.cleaned_data["doctor"] if form.is_valid() else None,
    )
    if request.GET.get("format") == "csv":
        return _telemedicine_csv_response(metrics)
    return render(request, "reports/telemedicine.html", {"form": form, "metrics": metrics})
