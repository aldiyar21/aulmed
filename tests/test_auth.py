import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_login_and_protected_access(authed_client, registrar_user):
    response = authed_client.get(reverse("patient-list"))
    assert response.status_code == 302

    logged = authed_client.login(username=registrar_user.username, password="demo12345")
    assert logged is True

    response = authed_client.get(reverse("patient-list"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_dashboard_access_for_manager(authed_client, manager_user):
    authed_client.login(username=manager_user.username, password="demo12345")
    response = authed_client.get(reverse("dashboard"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_dashboard_access_for_registrar(authed_client, registrar_user):
    authed_client.login(username=registrar_user.username, password="demo12345")
    response = authed_client.get(reverse("dashboard"))
    assert response.status_code == 200
