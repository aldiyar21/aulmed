from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import roles_required
from apps.accounts.models import EmployeeProfile
from apps.core.i18n import lang_text
from apps.core.utils import export_to_csv
from apps.encounters.models import Encounter
from apps.patients.models import Patient
from apps.referrals.forms import ReferralFilterForm, ReferralForm
from apps.referrals.selectors import filter_referrals, referral_queryset_for_user
from apps.referrals.services import create_referral, update_referral

ALLOWED_ROLES = (
    settings.ROLE_ADMIN,
    settings.ROLE_REGISTRAR,
    settings.ROLE_CLINICIAN,
    settings.ROLE_MANAGER,
)
CREATE_UPDATE_ROLES = (
    settings.ROLE_ADMIN,
    settings.ROLE_REGISTRAR,
    settings.ROLE_CLINICIAN,
)


@roles_required(*ALLOWED_ROLES)
def referral_list(request):
    form = ReferralFilterForm(request.GET or None)
    queryset = referral_queryset_for_user(request.user)
    if form.is_valid():
        queryset = filter_referrals(queryset, form.cleaned_data)
    page_obj = Paginator(queryset.order_by("-referral_date"), 15).get_page(request.GET.get("page"))
    return render(request, "referrals/list.html", {"form": form, "page_obj": page_obj})


@roles_required(*CREATE_UPDATE_ROLES)
def referral_create(request):
    form = ReferralForm(request.POST or None)
    if not request.user.is_superuser and hasattr(request.user, "employee_profile") and request.user.employee_profile.facility_id:
        facility_id = request.user.employee_profile.facility_id
        form.fields["patient"].queryset = Patient.objects.active().filter(facility_id=facility_id)
        form.fields["source_encounter"].queryset = Encounter.objects.filter(facility_id=facility_id)
        form.fields["created_by"].queryset = EmployeeProfile.objects.filter(facility_id=facility_id, is_active=True)
    if request.method == "POST" and form.is_valid():
        create_referral(user=request.user, cleaned_data=form.cleaned_data)
        messages.success(request, lang_text("Направление создано.", "Жолдама құрылды."))
        return redirect("referral-list")
    return render(request, "referrals/form.html", {"form": form, "title": lang_text("Создание направления", "Жолдама құру")})


@roles_required(*CREATE_UPDATE_ROLES)
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
        messages.success(request, lang_text("Направление обновлено.", "Жолдама жаңартылды."))
        return redirect("referral-list")
    return render(request, "referrals/form.html", {"form": form, "title": lang_text("Редактирование направления", "Жолдаманы өңдеу")})


@roles_required(*ALLOWED_ROLES)
def referral_export_csv(request):
    form = ReferralFilterForm(request.GET or None)
    queryset = referral_queryset_for_user(request.user)
    if form.is_valid():
        queryset = filter_referrals(queryset, form.cleaned_data)
    rows = [
        [
            str(item.referral_date),
            str(item.patient),
            item.destination_org,
            item.destination_specialist,
            item.get_priority_display(),
            item.get_status_display(),
        ]
        for item in queryset
    ]
    return export_to_csv(
        "referrals",
        [
            lang_text("Дата", "Күні"),
            lang_text("Пациент", "Пациент"),
            lang_text("Организация", "Ұйым"),
            lang_text("Специалист", "Маман"),
            lang_text("Приоритет", "Басымдық"),
            lang_text("Статус", "Күйі"),
        ],
        rows,
    )
