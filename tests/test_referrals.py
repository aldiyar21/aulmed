import pytest
from django.urls import reverse

from apps.referrals.models import Referral


@pytest.mark.django_db
def test_create_referral(authed_client, clinician_user, patient):
    authed_client.login(username=clinician_user.username, password="demo12345")
    response = authed_client.post(
        reverse("referral-create"),
        {
            "patient": patient.pk,
            "source_encounter": "",
            "created_by": clinician_user.employee_profile.pk,
            "destination_org": "Областная больница",
            "destination_specialist": "Кардиолог",
            "reason": "Боли в сердце",
            "priority": "high",
            "status": "created",
            "referral_date": "2026-04-01",
            "result_note": "",
        },
    )
    assert response.status_code == 302
    assert Referral.objects.count() == 1
