from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import roles_required
from apps.accounts.models import EmployeeProfile
from apps.core.i18n import lang_text
from apps.core.utils import export_to_csv
from apps.patients.models import Patient
from apps.prevention.forms import PreventionEventForm, PreventionFilterForm
from apps.prevention.selectors import (
    filter_prevention,
    overdue_queryset,
    prevention_queryset_for_user,
)
from apps.prevention.services import (
    create_prevention_event,
    mark_overdue_events,
    update_prevention_event,
)

ALLOWED_ROLES = ("Р С’Р Т‘Р СР С‘Р Р…Р С‘РЎРѓРЎвЂљРЎР‚Р В°РЎвЂљР С•РЎР‚ РЎРѓР С‘РЎРѓРЎвЂљР ВµР СРЎвЂ№", "Р СљР ВµР Т‘РЎР‚Р В°Р В±Р С•РЎвЂљР Р…Р С‘Р С”", "Р В РЎС“Р С”Р С•Р Р†Р С•Р Т‘Р С‘РЎвЂљР ВµР В»РЎРЉ")


@roles_required(*ALLOWED_ROLES)
def prevention_list(request):
    mark_overdue_events()
    form = PreventionFilterForm(request.GET or None)
    queryset = prevention_queryset_for_user(request.user)
    if form.is_valid():
        queryset = filter_prevention(queryset, form.cleaned_data)
    page_obj = Paginator(queryset.order_by("planned_date"), 15).get_page(request.GET.get("page"))
    return render(request, "prevention/list.html", {"form": form, "page_obj": page_obj})


@roles_required(*ALLOWED_ROLES)
def prevention_overdue(request):
    mark_overdue_events()
    queryset = overdue_queryset(prevention_queryset_for_user(request.user))
    return render(request, "prevention/overdue.html", {"page_obj": queryset})


@roles_required("Р С’Р Т‘Р СР С‘Р Р…Р С‘РЎРѓРЎвЂљРЎР‚Р В°РЎвЂљР С•РЎР‚ РЎРѓР С‘РЎРѓРЎвЂљР ВµР СРЎвЂ№", "Р СљР ВµР Т‘РЎР‚Р В°Р В±Р С•РЎвЂљР Р…Р С‘Р С”")
def prevention_create(request):
    form = PreventionEventForm(request.POST or None)
    if not request.user.is_superuser and hasattr(request.user, "employee_profile") and request.user.employee_profile.facility_id:
        facility_id = request.user.employee_profile.facility_id
        form.fields["patient"].queryset = Patient.objects.active().filter(facility_id=facility_id)
        form.fields["assigned_employee"].queryset = EmployeeProfile.objects.filter(facility_id=facility_id, is_active=True)
    if request.method == "POST" and form.is_valid():
        create_prevention_event(user=request.user, cleaned_data=form.cleaned_data)
        messages.success(request, lang_text("Профилактическое мероприятие создано.", "Профилактикалық іс-шара құрылды."))
        return redirect("prevention-list")
    return render(request, "prevention/form.html", {"form": form, "title": lang_text("Создание мероприятия", "Іс-шара құру")})


@roles_required("Р С’Р Т‘Р СР С‘Р Р…Р С‘РЎРѓРЎвЂљРЎР‚Р В°РЎвЂљР С•РЎР‚ РЎРѓР С‘РЎРѓРЎвЂљР ВµР СРЎвЂ№", "Р СљР ВµР Т‘РЎР‚Р В°Р В±Р С•РЎвЂљР Р…Р С‘Р С”")
def prevention_update(request, pk: int):
    event = get_object_or_404(prevention_queryset_for_user(request.user), pk=pk)
    form = PreventionEventForm(request.POST or None, instance=event)
    if not request.user.is_superuser and hasattr(request.user, "employee_profile") and request.user.employee_profile.facility_id:
        facility_id = request.user.employee_profile.facility_id
        form.fields["patient"].queryset = Patient.objects.active().filter(facility_id=facility_id)
        form.fields["assigned_employee"].queryset = EmployeeProfile.objects.filter(facility_id=facility_id, is_active=True)
    if request.method == "POST" and form.is_valid():
        update_prevention_event(user=request.user, event=event, cleaned_data=form.cleaned_data)
        messages.success(request, lang_text("Профилактическое мероприятие обновлено.", "Профилактикалық іс-шара жаңартылды."))
        return redirect("prevention-list")
    return render(request, "prevention/form.html", {"form": form, "title": lang_text("Редактирование мероприятия", "Іс-шараны өңдеу")})


@roles_required(*ALLOWED_ROLES)
def prevention_export_csv(request):
    form = PreventionFilterForm(request.GET or None)
    queryset = prevention_queryset_for_user(request.user)
    if form.is_valid():
        queryset = filter_prevention(queryset, form.cleaned_data)
    rows = [
        [str(item.patient), item.get_event_type_display(), str(item.planned_date), item.get_status_display(), str(item.assigned_employee or "")]
        for item in queryset
    ]
    return export_to_csv(
        "prevention",
        [
            lang_text("Пациент", "Пациент"),
            lang_text("Тип", "Түрі"),
            lang_text("Плановая дата", "Жоспарланған күн"),
            lang_text("Статус", "Күйі"),
            lang_text("Ответственный", "Жауапты"),
        ],
        rows,
    )
