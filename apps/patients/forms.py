from __future__ import annotations

from django import forms

from apps.facilities.models import Facility
from apps.patients.models import Patient


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            "last_name",
            "first_name",
            "middle_name",
            "iin",
            "birth_date",
            "sex",
            "phone",
            "address",
            "settlement_name",
            "facility",
            "social_category",
            "risk_level",
            "attachment_date",
            "notes",
            "is_active",
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "attachment_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class PatientFilterForm(forms.Form):
    q = forms.CharField(required=False, label="Поиск")
    settlement_name = forms.CharField(required=False, label="Населенный пункт")
    facility = forms.ModelChoiceField(
        queryset=Facility.objects.filter(is_active=True),
        required=False,
        label="Учреждение",
    )
    sex = forms.ChoiceField(required=False, choices=[("", "Все")] + Patient.SEX_CHOICES, label="Пол")
    risk_level = forms.ChoiceField(
        required=False,
        choices=[("", "Все")] + Patient.RISK_LEVEL_CHOICES,
        label="Риск",
    )
    is_active = forms.TypedChoiceField(
        required=False,
        coerce=lambda value: True if value == "True" else False if value == "False" else None,
        choices=(("", "Все"), ("True", "Активные"), ("False", "Неактивные")),
        label="Активность",
    )
    age_group = forms.ChoiceField(
        required=False,
        choices=(
            ("", "Все"),
            ("child", "Дети"),
            ("adult", "Взрослые"),
            ("elderly", "Пожилые"),
        ),
        label="Возрастная группа",
    )
