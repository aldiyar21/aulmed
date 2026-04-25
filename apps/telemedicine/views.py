from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.access import doctor_or_patient_consultation_access, require_access
from apps.accounts.decorators import patient_required, roles_required
from apps.audit.services import log_action
from apps.telemedicine.forms import (
    ConsultationCompletionForm,
    ConsultationFilterForm,
    TeleconsiliumCompleteForm,
    TeleconsiliumForm,
)
from apps.telemedicine.selectors import (
    consultation_queryset_for_user,
    filter_consultations,
    teleconsilium_queryset_for_user,
)
from apps.telemedicine.services import (
    CONSENT_TEXT,
    accept_patient_consent,
    cancel_consultation,
    complete_consultation,
    create_teleconsilium,
    start_consultation,
    update_teleconsilium,
)


@login_required
def consultation_list(request):
    form = ConsultationFilterForm(request.GET or None)
    qs = consultation_queryset_for_user(request.user)
    if form.is_valid():
        qs = filter_consultations(qs, form.cleaned_data)
    page_obj = Paginator(qs, 20).get_page(request.GET.get("page"))
    template = "telemedicine/patient_consultation_list.html" if hasattr(request.user, "patient_profile") else "telemedicine/doctor_consultation_list.html"
    return render(request, template, {"form": form, "page_obj": page_obj})


@login_required
def consultation_detail(request, pk: int):
    consultation = get_object_or_404(consultation_queryset_for_user(request.user), pk=pk)
    require_access(doctor_or_patient_consultation_access(request.user, consultation))
    log_action(
        user=request.user,
        action="view_consultation_detail",
        entity_type="OnlineConsultation",
        entity_id=consultation.pk,
        description=f"Viewed consultation detail {consultation.pk}",
        changes={"status": consultation.status},
    )
    template = (
        "telemedicine/patient_consultation_detail.html"
        if hasattr(request.user, "patient_profile")
        else "telemedicine/doctor_consultation_detail.html"
    )
    can_manage_consultation = bool(
        request.user.is_superuser or consultation.doctor_id == request.user.pk
    )
    return render(
        request,
        template,
        {
            "consultation": consultation,
            "can_manage_consultation": can_manage_consultation,
        },
    )


@patient_required
def consultation_consent(request, pk: int):
    consultation = get_object_or_404(consultation_queryset_for_user(request.user), pk=pk)
    if request.method == "POST":
        accept_patient_consent(
            user=request.user,
            patient=request.user.patient_profile,
            consultation=consultation,
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return redirect("consultation-room", pk=consultation.pk)
    return render(request, "telemedicine/consultation_consent.html", {"consultation": consultation, "consent_text": CONSENT_TEXT})


@login_required
def consultation_room(request, pk: int):
    consultation = get_object_or_404(consultation_queryset_for_user(request.user), pk=pk)
    require_access(doctor_or_patient_consultation_access(request.user, consultation))
    if hasattr(request.user, "patient_profile") and not consultation.consents.filter(
        accepted_by=request.user,
        patient=request.user.patient_profile,
        consent_type="telemedicine",
    ).exists():
        return redirect("consultation-consent", pk=consultation.pk)
    log_action(
        user=request.user,
        action="enter_consultation_room",
        entity_type="OnlineConsultation",
        entity_id=consultation.pk,
        description=f"Entered consultation room {consultation.pk}",
        changes={"room": consultation.jitsi_room_name},
    )
    template = "telemedicine/patient_consultation_room.html" if hasattr(request.user, "patient_profile") else "telemedicine/doctor_consultation_room.html"
    return render(request, template, {"consultation": consultation})


@roles_required("Администратор системы", "Медработник", "Руководитель")
def consultation_start(request, pk: int):
    consultation = get_object_or_404(consultation_queryset_for_user(request.user), pk=pk)
    if not (request.user.is_superuser or consultation.doctor_id == request.user.pk):
        raise PermissionDenied
    start_consultation(user=request.user, consultation=consultation)
    messages.success(request, "Консультация начата.")
    return redirect("consultation-room", pk=consultation.pk)


@roles_required("Администратор системы", "Медработник", "Руководитель")
def consultation_complete(request, pk: int):
    consultation = get_object_or_404(consultation_queryset_for_user(request.user), pk=pk)
    if not (request.user.is_superuser or consultation.doctor_id == request.user.pk):
        raise PermissionDenied
    form = ConsultationCompletionForm(request.POST or None, instance=consultation)
    if request.method == "POST" and form.is_valid():
        complete_consultation(user=request.user, consultation=consultation, cleaned_data=form.cleaned_data)
        messages.success(request, "Консультация завершена.")
        return redirect("consultation-detail", pk=consultation.pk)
    return render(request, "telemedicine/consultation_complete_form.html", {"form": form, "consultation": consultation})


@roles_required("Администратор системы", "Медработник", "Руководитель")
def consultation_cancel(request, pk: int):
    consultation = get_object_or_404(consultation_queryset_for_user(request.user), pk=pk)
    cancel_consultation(user=request.user, consultation=consultation)
    messages.success(request, "Консультация отменена.")
    return redirect("consultation-detail", pk=consultation.pk)


@login_required
def printable_consultation_summary(request, pk: int):
    consultation = get_object_or_404(consultation_queryset_for_user(request.user), pk=pk)
    require_access(doctor_or_patient_consultation_access(request.user, consultation))
    return render(request, "telemedicine/printable_consultation_summary.html", {"consultation": consultation})


@roles_required("Администратор системы", "Медработник", "Руководитель")
def teleconsilium_list(request):
    page_obj = Paginator(teleconsilium_queryset_for_user(request.user), 20).get_page(request.GET.get("page"))
    return render(request, "telemedicine/teleconsilium_list.html", {"page_obj": page_obj})


@roles_required("Администратор системы", "Медработник", "Руководитель")
def teleconsilium_detail(request, pk: int):
    teleconsilium = get_object_or_404(teleconsilium_queryset_for_user(request.user), pk=pk)
    return render(request, "telemedicine/teleconsilium_detail.html", {"teleconsilium": teleconsilium})


@roles_required("Администратор системы", "Медработник", "Руководитель")
def teleconsilium_create_view(request):
    form = TeleconsiliumForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        teleconsilium = create_teleconsilium(user=request.user, cleaned_data=form.cleaned_data)
        messages.success(request, "Телеконсилиум создан.")
        return redirect("teleconsilium-detail", pk=teleconsilium.pk)
    return render(request, "telemedicine/teleconsilium_form.html", {"form": form, "title": "Создание телеконсилиума"})


@roles_required("Администратор системы", "Медработник", "Руководитель")
def teleconsilium_update_view(request, pk: int):
    teleconsilium = get_object_or_404(teleconsilium_queryset_for_user(request.user), pk=pk)
    form = TeleconsiliumForm(request.POST or None, instance=teleconsilium)
    if request.method == "POST" and form.is_valid():
        update_teleconsilium(user=request.user, teleconsilium=teleconsilium, cleaned_data=form.cleaned_data)
        messages.success(request, "Телеконсилиум обновлен.")
        return redirect("teleconsilium-detail", pk=teleconsilium.pk)
    return render(request, "telemedicine/teleconsilium_form.html", {"form": form, "title": "Редактирование телеконсилиума"})


@roles_required("Администратор системы", "Медработник", "Руководитель")
def teleconsilium_room(request, pk: int):
    teleconsilium = get_object_or_404(teleconsilium_queryset_for_user(request.user), pk=pk)
    log_action(
        user=request.user,
        action="enter_teleconsilium_room",
        entity_type="Teleconsilium",
        entity_id=teleconsilium.pk,
        description=f"Entered teleconsilium room {teleconsilium.pk}",
        changes={"room": teleconsilium.jitsi_room_name},
    )
    return render(request, "telemedicine/teleconsilium_room.html", {"teleconsilium": teleconsilium})


@roles_required("Администратор системы", "Медработник", "Руководитель")
def teleconsilium_complete_view(request, pk: int):
    teleconsilium = get_object_or_404(teleconsilium_queryset_for_user(request.user), pk=pk)
    form = TeleconsiliumCompleteForm(request.POST or None, instance=teleconsilium)
    if request.method == "POST" and form.is_valid():
        update_teleconsilium(user=request.user, teleconsilium=teleconsilium, cleaned_data=form.cleaned_data)
        messages.success(request, "Телеконсилиум завершен.")
        return redirect("teleconsilium-detail", pk=teleconsilium.pk)
    return render(request, "telemedicine/teleconsilium_complete_form.html", {"form": form, "teleconsilium": teleconsilium})
