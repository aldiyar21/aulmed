import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from apps.prevention.models import PreventionEvent
from apps.prevention.services import mark_overdue_events


@pytest.mark.django_db
def test_prevention_event_marked_overdue(clinician_user, patient):
    event = PreventionEvent.objects.create(
        patient=patient,
        event_type="screening",
        planned_date=timezone.localdate() - timedelta(days=3),
        status="planned",
        assigned_employee=clinician_user.employee_profile,
    )
    updated = mark_overdue_events()
    event.refresh_from_db()
    assert updated >= 1
    assert event.status == "overdue"
