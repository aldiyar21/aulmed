from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import roles_required
from apps.accounts.models import EmployeeProfile
from apps.core.i18n import lang_text
from apps.core.utils import export_to_csv
from apps.encounters.forms import EncounterFilterForm, EncounterForm
from apps.encounters.selectors import encounter_queryset_for_user, filter_encounters
from apps.encounters.services import create_encounter, update_encounter
from apps.facilities.models import Facility
from apps.patients.models import Patient

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
def encounter_list(request):
    form = EncounterFilterForm(request.GET or None)
    queryset = encounter_queryset_for_user(request.user)
    if form.is_valid():
        queryset = filter_encounters(queryset, form.cleaned_data)
    page_obj = Paginator(queryset.order_by("-encounter_date"), 15).get_page(request.GET.get("page"))
    return render(request, "encounters/list.html", {"form": form, "page_obj": page_obj})


@roles_required(*CREATE_UPDATE_ROLES)
def encounter_create(request):
    initial = {}
    if patient_id := request.GET.get("patient"):
        initial["patient"] = patient_id
    form = EncounterForm(request.POST or None, initial=initial)
    if not request.user.is_superuser and hasattr(request.user, "employee_profile") and request.user.employee_profile.facility_id:
        facility_id = request.user.employee_profile.facility_id
        form.fields["patient"].queryset = Patient.objects.active().filter(facility_id=facility_id)
        form.fields["facility"].queryset = Facility.objects.filter(pk=facility_id)
        form.fields["facility"].initial = facility_id
        form.fields["clinician"].queryset = EmployeeProfile.objects.filter(facility_id=facility_id, is_active=True)
    if request.method == "POST" and form.is_valid():
        encounter = create_encounter(user=request.user, cleaned_data=form.cleaned_data)
        messages.success(request, lang_text("Обращение создано.", "Қабылдау құрылды."))
        return redirect("patient-detail", pk=encounter.patient_id)
    return render(request, "encounters/form.html", {"form": form, "title": lang_text("Создание обращения", "Қабылдау құру")})


@roles_required(*CREATE_UPDATE_ROLES)
def encounter_update(request, pk: int):
    encounter = get_object_or_404(encounter_queryset_for_user(request.user), pk=pk)
    form = EncounterForm(request.POST or None, instance=encounter)
    if not request.user.is_superuser and hasattr(request.user, "employee_profile") and request.user.employee_profile.facility_id:
        facility_id = request.user.employee_profile.facility_id
        form.fields["patient"].queryset = Patient.objects.active().filter(facility_id=facility_id)
        form.fields["facility"].queryset = Facility.objects.filter(pk=facility_id)
        form.fields["clinician"].queryset = EmployeeProfile.objects.filter(facility_id=facility_id, is_active=True)
    if request.method == "POST" and form.is_valid():
        update_encounter(user=request.user, encounter=encounter, cleaned_data=form.cleaned_data)
        messages.success(request, lang_text("Обращение обновлено.", "Қабылдау жаңартылды."))
        return redirect("patient-detail", pk=encounter.patient_id)
    return render(request, "encounters/form.html", {"form": form, "title": lang_text("Редактирование обращения", "Қабылдауды өңдеу")})


@roles_required(*ALLOWED_ROLES)
def encounter_export_csv(request):
    form = EncounterFilterForm(request.GET or None)
    queryset = encounter_queryset_for_user(request.user)
    if form.is_valid():
        queryset = filter_encounters(queryset, form.cleaned_data)
    rows = [
        [
            str(item.encounter_date),
            str(item.patient),
            item.facility.name,
            str(item.clinician),
            item.get_encounter_type_display(),
            item.get_result_type_display(),
        ]
        for item in queryset
    ]
    return export_to_csv(
        "encounters",
        [
            lang_text("Дата", "Күні"),
            lang_text("Пациент", "Пациент"),
            lang_text("Учреждение", "Ұйым"),
            lang_text("Сотрудник", "Қызметкер"),
            lang_text("Тип", "Түрі"),
            lang_text("Результат", "Нәтиже"),
        ],
        rows,
    )
