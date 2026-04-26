from django import forms

from apps.accounts.models import EmployeeProfile
from apps.core.forms import html5_date_input
from apps.core.i18n import lang_text_lazy
from apps.prevention.models import PreventionEvent


class PreventionEventForm(forms.ModelForm):
    class Meta:
        model = PreventionEvent
        fields = [
            "patient",
            "event_type",
            "planned_date",
            "completed_date",
            "status",
            "assigned_employee",
            "notes",
        ]
        widgets = {
            "planned_date": html5_date_input(),
            "completed_date": html5_date_input(),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class PreventionFilterForm(forms.Form):
    event_type = forms.ChoiceField(
        required=False,
        choices=[("", lang_text_lazy("Все", "Барлығы"))] + PreventionEvent.EVENT_TYPES,
        label=lang_text_lazy("Тип мероприятия", "Іс-шара түрі"),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[("", lang_text_lazy("Все", "Барлығы"))] + PreventionEvent.STATUS_CHOICES,
        label=lang_text_lazy("Статус", "Күйі"),
    )
    planned_date = forms.DateField(
        required=False,
        label=lang_text_lazy("Плановая дата", "Жоспарланған күн"),
        widget=html5_date_input(),
    )
    assigned_employee = forms.ModelChoiceField(
        queryset=EmployeeProfile.objects.filter(is_active=True),
        required=False,
        label=lang_text_lazy("Ответственный сотрудник", "Жауапты қызметкер"),
    )
