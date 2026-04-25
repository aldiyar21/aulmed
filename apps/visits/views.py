from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import roles_required
from apps.accounts.models import EmployeeProfile
from apps.core.i18n import lang_text
from apps.facilities.models import Facility
from apps.patients.selectors import patient_queryset_for_user
from apps.visits.forms import HomeVisitFilterForm, HomeVisitForm
from apps.visits.selectors import filter_visits, visit_queryset_for_user, visits_for_today
from apps.visits.services import create_home_visit, update_home_visit

ALLOWED_ROLES = ("РђРґРјРёРЅРёСЃС‚СЂР°С‚РѕСЂ СЃРёСЃС‚РµРјС‹", "Р РµРіРёСЃС‚СЂР°С‚РѕСЂ", "РњРµРґСЂР°Р±РѕС‚РЅРёРє", "Р СѓРєРѕРІРѕРґРёС‚РµР»СЊ")


@roles_required(*ALLOWED_ROLES)
def home_visit_list(request):
    form = HomeVisitFilterForm(request.GET or None)
    queryset = visit_queryset_for_user(request.user)
    if form.is_valid():
        queryset = filter_visits(queryset, form.cleaned_data)
    page_obj = Paginator(queryset.order_by("planned_date"), 15).get_page(request.GET.get("page"))
    return render(request, "visits/list.html", {"form": form, "page_obj": page_obj, "title": lang_text("Выезды", "Үйге барулар")})


@roles_required(*ALLOWED_ROLES)
def home_visit_today(request):
    queryset = visits_for_today(visit_queryset_for_user(request.user))
    return render(
        request,
        "visits/today.html",
        {"visits": queryset, "title": lang_text("Выезды на сегодня", "Бүгінгі шығулар")},
    )


@roles_required("РђРґРјРёРЅРёСЃС‚СЂР°С‚РѕСЂ СЃРёСЃС‚РµРјС‹", "Р РµРіРёСЃС‚СЂР°С‚РѕСЂ", "РњРµРґСЂР°Р±РѕС‚РЅРёРє")
def home_visit_create(request):
    patients_qs = patient_queryset_for_user(request.user).filter(is_active=True)
    form = HomeVisitForm(request.POST or None, patients_qs=patients_qs)
    if not request.user.is_superuser and hasattr(request.user, "employee_profile") and request.user.employee_profile.facility_id:
        facility_id = request.user.employee_profile.facility_id
        form.fields["facility"].queryset = Facility.objects.filter(pk=facility_id)
        form.fields["facility"].initial = facility_id
        form.fields["assigned_employee"].queryset = EmployeeProfile.objects.filter(facility_id=facility_id, is_active=True)
    if request.method == "POST" and form.is_valid():
        patients = form.cleaned_data.pop("patients")
        create_home_visit(user=request.user, cleaned_data=form.cleaned_data, patients=patients)
        messages.success(request, lang_text("Выезд создан.", "Үйге бару құрылды."))
        return redirect("visit-list")
    return render(request, "visits/form.html", {"form": form, "title": lang_text("Создание выезда", "Үйге баруды құру")})


@roles_required("РђРґРјРёРЅРёСЃС‚СЂР°С‚РѕСЂ СЃРёСЃС‚РµРјС‹", "Р РµРіРёСЃС‚СЂР°С‚РѕСЂ", "РњРµРґСЂР°Р±РѕС‚РЅРёРє")
def home_visit_update(request, pk: int):
    visit = get_object_or_404(visit_queryset_for_user(request.user), pk=pk)
    patients_qs = patient_queryset_for_user(request.user).filter(is_active=True)
    form = HomeVisitForm(request.POST or None, instance=visit, patients_qs=patients_qs)
    if not request.user.is_superuser and hasattr(request.user, "employee_profile") and request.user.employee_profile.facility_id:
        facility_id = request.user.employee_profile.facility_id
        form.fields["facility"].queryset = Facility.objects.filter(pk=facility_id)
        form.fields["assigned_employee"].queryset = EmployeeProfile.objects.filter(facility_id=facility_id, is_active=True)
    if request.method == "POST" and form.is_valid():
        patients = form.cleaned_data.pop("patients")
        update_home_visit(user=request.user, visit=visit, cleaned_data=form.cleaned_data, patients=patients)
        messages.success(request, lang_text("Выезд обновлён.", "Үйге бару жаңартылды."))
        return redirect("visit-list")
    return render(request, "visits/form.html", {"form": form, "title": lang_text("Редактирование выезда", "Үйге баруды өңдеу")})
