from __future__ import annotations

from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import roles_required
from apps.facilities.models import Facility
from apps.core.utils import export_to_csv
from apps.patients.forms import PatientFilterForm, PatientForm
from apps.patients.selectors import filter_patients, patient_queryset_for_user
from apps.patients.services import create_patient, update_patient


PATIENT_ALLOWED_ROLES = ("Администратор системы", "Регистратор", "Медработник", "Руководитель")


@roles_required(*PATIENT_ALLOWED_ROLES)
def patient_list(request):
    form = PatientFilterForm(request.GET or None)
    queryset = patient_queryset_for_user(request.user)
    if form.is_valid():
        queryset = filter_patients(queryset, form.cleaned_data)
    queryset = queryset.order_by("last_name", "first_name")
    paginator = Paginator(queryset, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    template_name = "patients/_patient_table.html" if request.htmx else "patients/list.html"
    return render(request, template_name, {"form": form, "page_obj": page_obj})


@roles_required(*PATIENT_ALLOWED_ROLES)
def patient_detail(request, pk: int):
    patient = get_object_or_404(
        patient_queryset_for_user(request.user),
        pk=pk,
    )
    context = {
        "patient": patient,
        "encounters": patient.encounters.select_related("clinician", "facility")[:10],
        "conditions": patient.conditions.all(),
        "prevention_events": patient.prevention_events.select_related("assigned_employee")[:10],
        "referrals": patient.referrals.select_related("created_by")[:10],
        "visit_links": patient.home_visit_links.select_related("home_visit")[:10],
    }
    return render(request, "patients/detail.html", context)


@roles_required("Администратор системы", "Регистратор", "Медработник")
def patient_create(request):
    form = PatientForm(request.POST or None)
    if not request.user.is_superuser and hasattr(request.user, "employee_profile") and request.user.employee_profile.facility_id:
        form.fields["facility"].queryset = Facility.objects.filter(pk=request.user.employee_profile.facility_id)
        form.fields["facility"].initial = request.user.employee_profile.facility_id
    if request.method == "POST" and form.is_valid():
        patient = create_patient(user=request.user, cleaned_data=form.cleaned_data)
        messages.success(request, "Пациент успешно создан.")
        return redirect("patient-detail", pk=patient.pk)
    return render(request, "patients/form.html", {"form": form, "title": "Создание пациента"})


@roles_required("Администратор системы", "Регистратор", "Медработник")
def patient_update(request, pk: int):
    patient = get_object_or_404(patient_queryset_for_user(request.user), pk=pk)
    form = PatientForm(request.POST or None, instance=patient)
    if not request.user.is_superuser and hasattr(request.user, "employee_profile") and request.user.employee_profile.facility_id:
        form.fields["facility"].queryset = Facility.objects.filter(pk=request.user.employee_profile.facility_id)
    if request.method == "POST" and form.is_valid():
        update_patient(user=request.user, patient=patient, cleaned_data=form.cleaned_data)
        messages.success(request, "Данные пациента обновлены.")
        return redirect("patient-detail", pk=patient.pk)
    return render(request, "patients/form.html", {"form": form, "title": "Редактирование пациента"})


@roles_required(*PATIENT_ALLOWED_ROLES)
def patient_export_csv(request):
    form = PatientFilterForm(request.GET or None)
    queryset = patient_queryset_for_user(request.user)
    if form.is_valid():
        queryset = filter_patients(queryset, form.cleaned_data)
    rows = [
        [
            patient.last_name,
            patient.first_name,
            patient.middle_name,
            patient.iin or "",
            str(patient.birth_date),
            patient.phone,
            patient.settlement_name,
            patient.facility.name,
            "Да" if patient.is_active else "Нет",
        ]
        for patient in queryset.select_related("facility")
    ]
    return export_to_csv(
        "patients",
        ["Фамилия", "Имя", "Отчество", "ИИН", "Дата рождения", "Телефон", "НП", "Учреждение", "Активен"],
        rows,
    )
