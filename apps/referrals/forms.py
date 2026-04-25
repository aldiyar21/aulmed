from django import forms

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
    status = forms.ChoiceField(required=False, choices=[("", "Все")] + Referral.STATUS_CHOICES)
    priority = forms.ChoiceField(required=False, choices=[("", "Все")] + Referral.PRIORITY_CHOICES)
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
