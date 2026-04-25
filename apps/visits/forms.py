from django import forms

from apps.accounts.models import EmployeeProfile
from apps.facilities.models import Facility
from apps.patients.models import Patient
from apps.visits.models import HomeVisit


class HomeVisitForm(forms.ModelForm):
    patients = forms.ModelMultipleChoiceField(
        queryset=Patient.objects.active(),
        label="Пациенты",
        widget=forms.SelectMultiple(attrs={"size": 8}),
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
            "planned_date": forms.DateInput(attrs={"type": "date"}),
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
            self.fields["patients"].initial = self.instance.visit_patients.values_list("patient_id", flat=True)


class HomeVisitFilterForm(forms.Form):
    planned_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    status = forms.ChoiceField(required=False, choices=[("", "Все")] + HomeVisit.STATUS_CHOICES)
    assigned_employee = forms.ModelChoiceField(queryset=EmployeeProfile.objects.filter(is_active=True), required=False)
    settlement_name = forms.CharField(required=False)
    facility = forms.ModelChoiceField(queryset=Facility.objects.filter(is_active=True), required=False)
