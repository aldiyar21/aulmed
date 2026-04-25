import pytest
from django.urls import reverse

from apps.audit.models import AuditLog
from apps.patients.models import Patient


@pytest.mark.django_db
def test_create_patient(authed_client, registrar_user, facility):
    authed_client.login(username=registrar_user.username, password="demo12345")
    response = authed_client.post(
        reverse("patient-create"),
        {
            "last_name": "Петров",
            "first_name": "Петр",
            "middle_name": "Петрович",
            "iin": "987654321098",
            "birth_date": "1985-05-01",
            "sex": "male",
            "phone": "+77001234567",
            "address": "ул. Ауыл, 2",
            "settlement_name": "Аул Тест",
            "facility": facility.pk,
            "social_category": "general",
            "risk_level": "medium",
            "attachment_date": "2026-01-01",
            "notes": "Тест",
            "is_active": "on",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert Patient.objects.filter(iin="987654321098").exists()


@pytest.mark.django_db
def test_search_patient(authed_client, registrar_user, patient):
    authed_client.login(username=registrar_user.username, password="demo12345")
    response = authed_client.get(reverse("patient-list"), {"q": "123456789012"})
    assert response.status_code == 200
    assert patient.last_name in response.content.decode("utf-8")


@pytest.mark.django_db
def test_audit_log_created_for_patient_creation(authed_client, registrar_user, facility):
    authed_client.login(username=registrar_user.username, password="demo12345")
    authed_client.post(
        reverse("patient-create"),
        {
            "last_name": "Сидоров",
            "first_name": "Сидор",
            "middle_name": "",
            "iin": "111111111111",
            "birth_date": "1988-02-10",
            "sex": "male",
            "phone": "+77000001234",
            "address": "ул. Степная, 3",
            "settlement_name": "Аул Тест",
            "facility": facility.pk,
            "social_category": "general",
            "risk_level": "low",
            "attachment_date": "2026-01-02",
            "notes": "",
            "is_active": "on",
        },
    )
    assert AuditLog.objects.filter(entity_type="Patient", action="create").exists()


@pytest.mark.django_db
def test_update_patient_serializes_dates_in_audit_log(authed_client, registrar_user, patient, facility):
    authed_client.login(username=registrar_user.username, password="demo12345")

    response = authed_client.post(
        reverse("patient-update", args=[patient.pk]),
        {
            "last_name": patient.last_name,
            "first_name": patient.first_name,
            "middle_name": patient.middle_name,
            "iin": patient.iin,
            "birth_date": "1990-05-25",
            "sex": patient.sex,
            "phone": patient.phone,
            "address": patient.address,
            "settlement_name": patient.settlement_name,
            "facility": facility.pk,
            "social_category": patient.social_category,
            "risk_level": patient.risk_level,
            "attachment_date": "2024-12-24",
            "notes": "Обновлено в тесте",
            "is_active": "on",
        },
        follow=True,
    )

    assert response.status_code == 200
    audit_log = AuditLog.objects.filter(entity_type="Patient", action="update").latest("created_at")
    assert audit_log.changes_json["birth_date"] == "1990-05-25"
    assert audit_log.changes_json["attachment_date"] == "2024-12-24"
