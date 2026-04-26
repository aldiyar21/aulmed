from django import forms

from apps.accounts.models import EmployeeProfile
from apps.core.forms import html5_date_input
from apps.core.i18n import lang_text_lazy
from apps.facilities.models import Facility
from apps.patients.models import Patient
from apps.visits.models import HomeVisit


class HomeVisitForm(forms.ModelForm):
    patients = forms.ModelMultipleChoiceField(
        queryset=Patient.objects.active(),
        label=lang_text_lazy("Пациенты", "Пациенттер"),
        widget=forms.CheckboxSelectMultiple(),
    )

    class Meta:
        model = HomeVisit
        fields = [
            "planned_date",
            "facility",
            "assigned_employee",
            "settlement_name",
            "status",
            "purpose",
            "route_notes",
            "result_summary",
        ]
        widgets = {
            "planned_date": html5_date_input(),
            "purpose": forms.Textarea(attrs={"rows": 3}),
            "route_notes": forms.Textarea(attrs={"rows": 2}),
            "result_summary": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        patients_qs = kwargs.pop("patients_qs", None)
        super().__init__(*args, **kwargs)
        if patients_qs is not None:
            self.fields["patients"].queryset = patients_qs
        if self.instance.pk:
            self.fields["patients"].initial = self.instance.visit_patients.values_list(
                "patient_id",
                flat=True,
            )


class HomeVisitFilterForm(forms.Form):
    planned_date = forms.DateField(
        required=False,
        label=lang_text_lazy("Дата выезда", "Шығу күні"),
        widget=html5_date_input(),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[("", lang_text_lazy("Все", "Барлығы"))] + HomeVisit.STATUS_CHOICES,
        label=lang_text_lazy("Статус", "Күйі"),
    )
    assigned_employee = forms.ModelChoiceField(
        queryset=EmployeeProfile.objects.filter(is_active=True),
        required=False,
        label=lang_text_lazy("Сотрудник", "Қызметкер"),
    )
    settlement_name = forms.CharField(
        required=False,
        label=lang_text_lazy("Населённый пункт", "Елді мекен"),
    )
    facility = forms.ModelChoiceField(
        queryset=Facility.objects.filter(is_active=True),
        required=False,
        label=lang_text_lazy("Учреждение", "Ұйым"),
    )
