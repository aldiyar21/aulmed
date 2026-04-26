from __future__ import annotations

from apps.audit.services import log_action
from apps.monitoring.models import VitalReading


def create_vital_reading(*, user, patient, source: str, cleaned_data: dict) -> VitalReading:
    reading = VitalReading.objects.create(patient=patient, recorded_by=user, source=source, **cleaned_data)
    log_action(
        user=user,
        action="create_vital_reading",
        entity_type="VitalReading",
        entity_id=reading.pk,
        description=f"Created vital reading for patient {patient}",
        changes=cleaned_data,
    )
    return reading
