from django import forms

from apps.accounts.models import EmployeeProfile
from apps.core.forms import html5_date_input
from apps.core.i18n import lang_text_lazy
from apps.encounters.models import Encounter
from apps.facilities.models import Facility
from apps.patients.models import Patient


class EncounterForm(forms.ModelForm):
    class Meta:
        model = Encounter
        fields = [
            "patient",
            "facility",
            "clinician",
            "encounter_type",
            "encounter_date",
            "reason_for_visit",
            "diagnosis_text",
            "services_provided",
            "result_type",
            "next_visit_date",
            "notes",
        ]
        widgets = {
            "encounter_date": html5_date_input(),
            "next_visit_date": html5_date_input(),
            "reason_for_visit": forms.Textarea(attrs={"rows": 3}),
            "diagnosis_text": forms.Textarea(attrs={"rows": 3}),
            "services_provided": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class EncounterFilterForm(forms.Form):
    date_from = forms.DateField(
        required=False,
        label=lang_text_lazy("Дата с", "Басталу күні"),
        widget=html5_date_input(),
    )
    date_to = forms.DateField(
        required=False,
        label=lang_text_lazy("Дата по", "Аяқталу күні"),
        widget=html5_date_input(),
    )
    facility = forms.ModelChoiceField(
        queryset=Facility.objects.filter(is_active=True),
        required=False,
        label=lang_text_lazy("Учреждение", "Ұйым"),
    )
    clinician = forms.ModelChoiceField(
        queryset=EmployeeProfile.objects.filter(is_active=True),
        required=False,
        label=lang_text_lazy("Сотрудник", "Қызметкер"),
    )
    encounter_type = forms.ChoiceField(
        required=False,
        choices=[("", lang_text_lazy("Все", "Барлығы"))] + Encounter.ENCOUNTER_TYPES,
        label=lang_text_lazy("Тип обращения", "Қабылдау түрі"),
    )
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.active(),
        required=False,
        label=lang_text_lazy("Пациент", "Пациент"),
    )
