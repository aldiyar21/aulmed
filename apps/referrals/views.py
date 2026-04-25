from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import roles_required
from apps.accounts.models import EmployeeProfile
from apps.core.utils import export_to_csv
from apps.encounters.models import Encounter
from apps.patients.models import Patient
from apps.referrals.forms import ReferralFilterForm, ReferralForm
from apps.referrals.selectors import filter_referrals, referral_queryset_for_user
from apps.referrals.services import create_referral, update_referral


ALLOWED_ROLES = ("Администратор системы", "Регистратор", "Медработник", "Руководитель")


@roles_required(*ALLOWED_ROLES)
def referral_list(request):
    form = ReferralFilterForm(request.GET or None)
    queryset = referral_queryset_for_user(request.user)
    if form.is_valid():
        queryset = filter_referrals(queryset, form.cleaned_data)
    page_obj = Paginator(queryset.order_by("-referral_date"), 15).get_page(request.GET.get("page"))
    return render(request, "referrals/list.html", {"form": form, "page_obj": page_obj})


@roles_required("Администратор системы", "Регистратор", "Медработник")
def referral_create(request):
    form = ReferralForm(request.POST or None)
    if not request.user.is_superuser and hasattr(request.user, "employee_profile") and request.user.employee_profile.facility_id:
        facility_id = request.user.employee_profile.facility_id
        form.fields["patient"].queryset = Patient.objects.active().filter(facility_id=facility_id)
        form.fields["source_encounter"].queryset = Encounter.objects.filter(facility_id=facility_id)
        form.fields["created_by"].queryset = EmployeeProfile.objects.filter(facility_id=facility_id, is_active=True)
    if request.method == "POST" and form.is_valid():
        create_referral(user=request.user, cleaned_data=form.cleaned_data)
        messages.success(request, "Направление создано.")
        return redirect("referral-list")
    return render(request, "referrals/form.html", {"form": form, "title": "Создание направления"})


@roles_required("Администратор системы", "Регистратор", "Медработник")
def referral_update(request, pk: int):
    referral = get_object_or_404(referral_queryset_for_user(request.user), pk=pk)
    form = ReferralForm(request.POST or None, instance=referral)
    if not request.user.is_superuser and hasattr(request.user, "employee_profile") and request.user.employee_profile.facility_id:
        facility_id = request.user.employee_profile.facility_id
        form.fields["patient"].queryset = Patient.objects.active().filter(facility_id=facility_id)
        form.fields["source_encounter"].queryset = Encounter.objects.filter(facility_id=facility_id)
        form.fields["created_by"].queryset = EmployeeProfile.objects.filter(facility_id=facility_id, is_active=True)
    if request.method == "POST" and form.is_valid():
        update_referral(user=request.user, referral=referral, cleaned_data=form.cleaned_data)
        messages.success(request, "Направление обновлено.")
        return redirect("referral-list")
    return render(request, "referrals/form.html", {"form": form, "title": "Редактирование направления"})


@roles_required(*ALLOWED_ROLES)
def referral_export_csv(request):
    form = ReferralFilterForm(request.GET or None)
    queryset = referral_queryset_for_user(request.user)
    if form.is_valid():
        queryset = filter_referrals(queryset, form.cleaned_data)
    rows = [
        [str(item.referral_date), str(item.patient), item.destination_org, item.destination_specialist, item.priority, item.status]
        for item in queryset
    ]
    return export_to_csv(
        "referrals",
        ["Дата", "Пациент", "Организация", "Специалист", "Приоритет", "Статус"],
        rows,
    )
