from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from django.contrib.auth.models import User
from django.db import models

from apps.audit.models import AuditLog


def _serialize_value(value):
    if isinstance(value, models.Model):
        return {"id": value.pk, "label": str(value)}
    if isinstance(value, (date, datetime, time)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, dict):
        return {key: _serialize_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_serialize_value(item) for item in value]
    return value


def log_action(
    *,
    user: User | None,
    action: str,
    entity_type: str,
    entity_id: int | str,
    description: str,
    changes: dict | None = None,
) -> AuditLog:
    return AuditLog.objects.create(
        user=user,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        description=description,
        changes_json=_serialize_value(changes or {}),
    )
