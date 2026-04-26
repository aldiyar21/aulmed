from __future__ import annotations

from django.contrib.auth.models import User

from apps.audit.services import log_action
from apps.core.i18n import lang_text
from apps.encounters.models import Encounter


def create_encounter(*, user: User, cleaned_data: dict) -> Encounter:
    encounter = Encounter.objects.create(**cleaned_data)
    log_action(
        user=user,
        action="create",
        entity_type="Encounter",
        entity_id=encounter.pk,
        description=lang_text(
            f"Создано обращение пациента {encounter.patient}",
            f"Пациенттің қабылдауы құрылды: {encounter.patient}",
        ),
        changes=cleaned_data,
    )
    return encounter


def update_encounter(*, user: User, encounter: Encounter, cleaned_data: dict) -> Encounter:
    for field, value in cleaned_data.items():
        setattr(encounter, field, value)
    encounter.save()
    log_action(
        user=user,
        action="update",
        entity_type="Encounter",
        entity_id=encounter.pk,
        description=lang_text(
            f"Обновлено обращение {encounter.pk}",
            f"Қабылдау жаңартылды: {encounter.pk}",
        ),
        changes=cleaned_data,
    )
    return encounter
