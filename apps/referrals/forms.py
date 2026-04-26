from django import forms

from apps.encounters.models import Encounter
from apps.patients.models import Patient
from apps.core.forms import html5_date_input
from apps.core.i18n import lang_text_lazy
from apps.referrals.models import Referral


class ReferralForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        patient = None
        patient_value = self.data.get("patient") or self.initial.get("patient")
        if patient_value:
            patient = Patient.objects.filter(pk=patient_value).first()
        elif self.instance.pk:
            patient = self.instance.patient

        if patient:
            self.fields["source_encounter"].queryset = Encounter.objects.filter(patient=patient)
        else:
            self.fields["source_encounter"].queryset = Encounter.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        patient = cleaned_data.get("patient")
        source_encounter = cleaned_data.get("source_encounter")
        if source_encounter and patient and source_encounter.patient_id != patient.pk:
            self.add_error(
                "source_encounter",
                lang_text_lazy(
                    "Можно выбрать только обращение выбранного пациента.",
                    "Тек таңдалған пациенттің қабылдауын ғана таңдауға болады.",
                ),
            )
        return cleaned_data

    class Meta:
        model = Referral
        fields = [
            "patient",
            "source_encounter",
            "created_by",
            "destination_org",
            "destination_specialist",
            "reason",
            "priority",
            "status",
            "referral_date",
            "result_note",
        ]
        widgets = {
            "referral_date": html5_date_input(),
            "reason": forms.Textarea(attrs={"rows": 3}),
            "result_note": forms.Textarea(attrs={"rows": 3}),
        }


class ReferralFilterForm(forms.Form):
    status = forms.ChoiceField(
        required=False,
        choices=[("", lang_text_lazy("Все", "Барлығы"))] + Referral.STATUS_CHOICES,
        label=lang_text_lazy("Статус", "Күйі"),
    )
    priority = forms.ChoiceField(
        required=False,
        choices=[("", lang_text_lazy("Все", "Барлығы"))] + Referral.PRIORITY_CHOICES,
        label=lang_text_lazy("Приоритет", "Басымдық"),
    )
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
