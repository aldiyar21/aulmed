import csv

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render

from apps.accounts.decorators import roles_required
from apps.accounts.services import user_is_manager_or_admin
from apps.core.forms import html5_date_input
from apps.core.i18n import lang_text, lang_text_lazy
from apps.facilities.models import Facility
from apps.reports.services import build_telemedicine_metrics

REPORT_ROLES = (
    settings.ROLE_ADMIN,
    settings.ROLE_MANAGER,
    settings.ROLE_CLINICIAN,
)


class TelemedicineReportFilterForm(forms.Form):
    date_from = forms.DateField(
        label=lang_text_lazy("Дата с", "Басталу күні"),
        required=False,
        widget=html5_date_input(),
    )
    date_to = forms.DateField(
        label=lang_text_lazy("Дата по", "Аяқталу күні"),
        required=False,
        widget=html5_date_input(),
    )
    facility = forms.ModelChoiceField(
        label=lang_text_lazy("Учреждение", "Ұйым"),
        queryset=Facility.objects.filter(is_active=True),
        required=False,
    )
    doctor = forms.ModelChoiceField(
        label=lang_text_lazy("Врач", "Дәрігер"),
        queryset=User.objects.filter(employee_profile__role_code="clinician"),
        required=False,
    )


def _telemedicine_csv_response(metrics: dict) -> HttpResponse:
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="telemedicine-report.csv"'
    writer = csv.writer(response)
    writer.writerow([lang_text("Метрика", "Көрсеткіш"), lang_text("Значение", "Мәні")])
    writer.writerow([lang_text("Дата с", "Басталу күні"), metrics["date_from"]])
    writer.writerow([lang_text("Дата по", "Аяқталу күні"), metrics["date_to"]])
    writer.writerow([lang_text("Всего онлайн-консультаций", "Барлық онлайн консультациялар"), metrics["total_online_consultations"]])
    writer.writerow([lang_text("Назначенных консультаций", "Жоспарланған консультациялар"), metrics["scheduled_consultations"]])
    writer.writerow([lang_text("Завершённых консультаций", "Аяқталған консультациялар"), metrics["completed_consultations"]])
    writer.writerow([lang_text("Отменённых консультаций", "Бас тартылған консультациялар"), metrics["cancelled_consultations"]])
    writer.writerow([lang_text("Среднее время ожидания", "Орташа күту уақыты"), metrics["average_wait_time"] or ""])
    writer.writerow([lang_text("Выданных документов", "Берілген құжаттар"), metrics["issued_medical_documents"]])
    writer.writerow([lang_text("Выданных рецептов", "Берілген рецепттер"), metrics["issued_prescriptions"]])
    writer.writerow([lang_text("Пациентов на дистанционном мониторинге", "Қашықтан мониторингтегі пациенттер"), metrics["active_remote_monitoring_patients"]])
    writer.writerow([lang_text("Всего телеконсилиумов", "Телеконсилиумдар саны"), metrics["teleconsiliums_count"]])
    writer.writerow([lang_text("Завершённых телеконсилиумов", "Аяқталған телеконсилиумдар"), metrics["teleconsiliums_completed_count"]])
    writer.writerow([])
    writer.writerow([lang_text("Раздел", "Бөлім"), lang_text("Показатель", "Көрсеткіш"), lang_text("Количество", "Саны")])
    for item in metrics["appointments_by_status"]:
        writer.writerow([lang_text("Записи по статусу", "Жазылулар күйі бойынша"), item["status"], item["total"]])
    for item in metrics["appointments_by_type"]:
        writer.writerow([lang_text("Записи по типу", "Жазылулар түрі бойынша"), item["appointment_type"], item["total"]])
    for item in metrics["consultations_by_facility"]:
        writer.writerow([lang_text("Консультации по учреждениям", "Консультациялар ұйым бойынша"), item["facility__name"], item["total"]])
    for item in metrics["consultations_by_settlement"]:
        writer.writerow([lang_text("Консультации по населённым пунктам", "Консультациялар елді мекен бойынша"), item["patient__settlement_name"], item["total"]])
    for item in metrics["doctor_workload"]:
        writer.writerow([lang_text("Нагрузка врачей", "Дәрігер жүктемесі"), item["doctor__username"], item["total"]])
    return response


@roles_required(*REPORT_ROLES)
def reports_view(request):
    return render(request, "reports/index.html")


@roles_required(*REPORT_ROLES)
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
