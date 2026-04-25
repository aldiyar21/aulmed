import pytest
from django.urls import reverse

from apps.patients.models import Patient
from apps.visits.models import HomeVisit


@pytest.mark.django_db
def test_create_home_visit_with_multiple_patients(authed_client, clinician_user, patient, facility):
    second_patient = Patient.objects.create(
        last_name="Сериков",
        first_name="Асан",
        middle_name="",
        iin="222222222222",
        birth_date="1980-01-01",
        sex="male",
        phone="+77000000004",
        address="ул. Абая, 2",
        settlement_name=facility.settlement_name,
        facility=facility,
        social_category="general",
        risk_level="low",
        attachment_date="2026-01-01",
    )
    authed_client.login(username=clinician_user.username, password="demo12345")
    response = authed_client.post(
        reverse("visit-create"),
        {
            "planned_date": "2026-04-22",
            "facility": facility.pk,
            "assigned_employee": clinician_user.employee_profile.pk,
            "settlement_name": facility.settlement_name,
            "status": "planned",
            "purpose": "Осмотр на дому",
            "route_notes": "Маршрут",
            "result_summary": "",
            "patients": [patient.pk, second_patient.pk],
        },
    )
    assert response.status_code == 302
    visit = HomeVisit.objects.get()
    assert visit.visit_patients.count() == 2
