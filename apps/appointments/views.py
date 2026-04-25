from __future__ import annotations
from apps.core.i18n import lang_text
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import patient_required, roles_required
from apps.appointments.forms import (
    AppointmentFilterForm,
    AppointmentPatientForm,
    AppointmentStaffUpdateForm,
)
from apps.appointments.selectors import (
    appointment_queryset_for_user,
    doctor_appointments,
    filter_appointments,
)
from apps.appointments.services import create_appointment, update_appointment
from apps.facilities.models import Facility


@patient_required
def patient_appointment_create(request):
    patient = request.user.patient_profile
    form = AppointmentPatientForm(request.POST or None, initial={"facility": patient.facility})
    form.fields["facility"].queryset = Facility.objects.filter(pk=patient.facility_id)
    if request.method == "POST" and form.is_valid():
        appointment = create_appointment(user=request.user, patient=patient, cleaned_data=form.cleaned_data)
        messages.success(request, lang_text("Заявка создана.", "Өтінім жасалды."))
        return redirect("patient-appointment-detail", pk=appointment.pk)
    return render(request, "appointments/patient_appointment_form.html", {"form": form})


@patient_required
def patient_appointment_list(request):
    form = AppointmentFilterForm(request.GET or None)
    qs = appointment_queryset_for_user(request.user)
    if form.is_valid():
        qs = filter_appointments(qs, form.cleaned_data)
    page_obj = Paginator(qs, 15).get_page(request.GET.get("page"))
    return render(request, "appointments/patient_appointment_list.html", {"form": form, "page_obj": page_obj})


@patient_required
def patient_appointment_detail(request, pk: int):
    appointment = get_object_or_404(appointment_queryset_for_user(request.user), pk=pk)
    return render(request, "appointments/patient_appointment_detail.html", {"appointment": appointment})


@roles_required("Администратор системы", "Регистратор", "Медработник", "Руководитель")
def staff_appointment_list(request):
    form = AppointmentFilterForm(request.GET or None)
    qs = appointment_queryset_for_user(request.user)
    if form.is_valid():
        qs = filter_appointments(qs, form.cleaned_data)
    page_obj = Paginator(qs, 20).get_page(request.GET.get("page"))
    return render(request, "appointments/staff_appointment_list.html", {"form": form, "page_obj": page_obj})


@roles_required("Администратор системы", "Регистратор", "Медработник", "Руководитель")
def staff_appointment_detail(request, pk: int):
    appointment = get_object_or_404(appointment_queryset_for_user(request.user), pk=pk)
    return render(request, "appointments/staff_appointment_detail.html", {"appointment": appointment})


@roles_required("Администратор системы", "Регистратор", "Медработник", "Руководитель")
def staff_appointment_update(request, pk: int):
    appointment = get_object_or_404(appointment_queryset_for_user(request.user), pk=pk)
    form = AppointmentStaffUpdateForm(request.POST or None, instance=appointment)
    if request.method == "POST" and form.is_valid():
        appointment = update_appointment(user=request.user, appointment=appointment, cleaned_data=form.cleaned_data)
        messages.success(request, lang_text("Запись обновлена.", "Жазба жаңартылды."))
        return redirect("staff-appointment-detail", pk=appointment.pk)
    return render(
        request,
        "appointments/staff_appointment_form.html",
        {"form": form, "appointment": appointment},
    )


@roles_required("Администратор системы", "Медработник", "Руководитель")
def doctor_appointment_list(request):
    form = AppointmentFilterForm(request.GET or None)
    qs = doctor_appointments(request.user)
    if form.is_valid():
        qs = filter_appointments(qs, form.cleaned_data)
    page_obj = Paginator(qs, 20).get_page(request.GET.get("page"))
    return render(request, "appointments/doctor_appointment_list.html", {"form": form, "page_obj": page_obj})
