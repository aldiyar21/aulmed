from django import forms
from django.utils import timezone

from apps.accounts.models import EmployeeProfile
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
            "planned_date": forms.DateInput(attrs={"type": "date"}),
            "completed_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class PreventionFilterForm(forms.Form):
    event_type = forms.ChoiceField(required=False, choices=[("", "Все")] + PreventionEvent.EVENT_TYPES)
    status = forms.ChoiceField(required=False, choices=[("", "Все")] + PreventionEvent.STATUS_CHOICES)
    planned_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    assigned_employee = forms.ModelChoiceField(queryset=EmployeeProfile.objects.filter(is_active=True), required=False)
