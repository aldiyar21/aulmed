import pytest
from django.urls import reverse

from apps.encounters.models import Encounter


@pytest.mark.django_db
def test_create_encounter(authed_client, clinician_user, patient):
    authed_client.login(username=clinician_user.username, password="demo12345")
    response = authed_client.post(
        reverse("encounter-create"),
        {
            "patient": patient.pk,
            "facility": patient.facility.pk,
            "clinician": clinician_user.employee_profile.pk,
            "encounter_type": "clinic",
            "encounter_date": "2026-04-01",
            "reason_for_visit": "Боль в горле",
            "diagnosis_text": "ОРВИ",
            "services_provided": "Осмотр",
            "result_type": "treatment",
            "next_visit_date": "2026-04-10",
            "notes": "Тест",
        },
    )
    assert response.status_code == 302
    assert Encounter.objects.count() == 1
