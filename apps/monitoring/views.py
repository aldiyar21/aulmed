from __future__ import annotations

from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import patient_required, roles_required
from apps.monitoring.forms import VitalReadingForm
from apps.monitoring.models import VitalReading
from apps.monitoring.selectors import vital_reading_queryset_for_user
from apps.monitoring.services import create_vital_reading
from apps.patients.models import Patient


@patient_required
def patient_vital_reading_list(request):
    page_obj = Paginator(vital_reading_queryset_for_user(request.user), 20).get_page(request.GET.get("page"))
    latest_readings = page_obj.object_list[:3]
    return render(
        request,
        "monitoring/patient_vital_list.html",
        {"page_obj": page_obj, "latest_readings": latest_readings},
    )


@patient_required
def patient_vital_reading_create(request):
    form = VitalReadingForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        create_vital_reading(
            user=request.user,
            patient=request.user.patient_profile,
            source=VitalReading.Source.PATIENT_MANUAL,
            cleaned_data=form.cleaned_data,
        )
        messages.success(request, "Показатели сохранены.")
        return redirect("patient-vital-reading-list")
    return render(request, "monitoring/vital_form.html", {"form": form, "title": "Новые показатели"})


@roles_required("Администратор системы", "Медработник", "Руководитель")
def staff_patient_vital_list(request, patient_pk: int):
    patient = get_object_or_404(Patient, pk=patient_pk)
    page_obj = Paginator(vital_reading_queryset_for_user(request.user).filter(patient=patient), 20).get_page(request.GET.get("page"))
    return render(request, "monitoring/staff_vital_list.html", {"page_obj": page_obj, "patient": patient})


@roles_required("Администратор системы", "Медработник", "Руководитель")
def staff_patient_vital_create(request, patient_pk: int):
    patient = get_object_or_404(Patient, pk=patient_pk)
    form = VitalReadingForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        create_vital_reading(
            user=request.user,
            patient=patient,
            source=VitalReading.Source.DOCTOR_MANUAL,
            cleaned_data=form.cleaned_data,
        )
        messages.success(request, "Показатели пациента сохранены.")
        return redirect("staff-patient-vital-list", patient_pk=patient.pk)
    return render(request, "monitoring/vital_form.html", {"form": form, "title": f"Новые показатели: {patient}"})
