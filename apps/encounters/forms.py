from django import forms

from apps.accounts.models import EmployeeProfile
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
            "encounter_date": forms.DateInput(attrs={"type": "date"}),
            "next_visit_date": forms.DateInput(attrs={"type": "date"}),
            "reason_for_visit": forms.Textarea(attrs={"rows": 3}),
            "diagnosis_text": forms.Textarea(attrs={"rows": 3}),
            "services_provided": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class EncounterFilterForm(forms.Form):
    date_from = forms.DateField(
        required=False,
        label=lang_text_lazy("Дата с", "Басталу күні"),
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    date_to = forms.DateField(
        required=False,
        label=lang_text_lazy("Дата по", "Аяқталу күні"),
        widget=forms.DateInput(attrs={"type": "date"}),
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
