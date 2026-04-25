from __future__ import annotations

from django.contrib.auth.models import User
from django.utils import timezone

from apps.audit.services import log_action
from apps.prevention.models import PreventionEvent


def create_prevention_event(*, user: User, cleaned_data: dict) -> PreventionEvent:
    event = PreventionEvent.objects.create(**cleaned_data)
    log_action(
        user=user,
        action="create",
        entity_type="PreventionEvent",
        entity_id=event.pk,
        description=f"Создано профилактическое мероприятие для {event.patient}",
        changes=cleaned_data,
    )
    return event


def update_prevention_event(*, user: User, event: PreventionEvent, cleaned_data: dict) -> PreventionEvent:
    for field, value in cleaned_data.items():
        setattr(event, field, value)
    event.save()
    log_action(
        user=user,
        action="update",
        entity_type="PreventionEvent",
        entity_id=event.pk,
        description=f"Обновлено профилактическое мероприятие {event.pk}",
        changes=cleaned_data,
    )
    return event


def mark_overdue_events() -> int:
    """Переводит просроченные запланированные мероприятия в статус overdue."""
    updated = PreventionEvent.objects.filter(
        status="planned",
        planned_date__lt=timezone.localdate(),
        completed_date__isnull=True,
    ).update(status="overdue")
    return updated
