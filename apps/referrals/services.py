from __future__ import annotations

from django.contrib.auth.models import User

from apps.audit.services import log_action
from apps.referrals.models import Referral


def create_referral(*, user: User, cleaned_data: dict) -> Referral:
    referral = Referral.objects.create(**cleaned_data)
    log_action(
        user=user,
        action="create",
        entity_type="Referral",
        entity_id=referral.pk,
        description=f"Создано направление для {referral.patient}",
        changes=cleaned_data,
    )
    return referral


def update_referral(*, user: User, referral: Referral, cleaned_data: dict) -> Referral:
    previous_status = referral.status
    for field, value in cleaned_data.items():
        setattr(referral, field, value)
    referral.save()
    action = "status_change" if previous_status != referral.status else "update"
    log_action(
        user=user,
        action=action,
        entity_type="Referral",
        entity_id=referral.pk,
        description=f"Обновлено направление {referral.pk}",
        changes=cleaned_data,
    )
    return referral
