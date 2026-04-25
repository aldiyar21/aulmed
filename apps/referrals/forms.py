from django import forms

from apps.core.i18n import lang_text_lazy
from apps.referrals.models import Referral


class ReferralForm(forms.ModelForm):
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
            "referral_date": forms.DateInput(attrs={"type": "date"}),
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
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    date_to = forms.DateField(
        required=False,
        label=lang_text_lazy("Дата по", "Аяқталу күні"),
        widget=forms.DateInput(attrs={"type": "date"}),
    )
