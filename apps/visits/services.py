from __future__ import annotations

from django.contrib.auth.models import User
from django.db import transaction

from apps.audit.services import log_action
from apps.core.i18n import lang_text
from apps.visits.models import HomeVisit, HomeVisitPatient


@transaction.atomic
def create_home_visit(*, user: User, cleaned_data: dict, patients) -> HomeVisit:
    visit = HomeVisit.objects.create(**cleaned_data)
    HomeVisitPatient.objects.bulk_create(
        [HomeVisitPatient(home_visit=visit, patient=patient) for patient in patients]
    )
    log_action(
        user=user,
        action="create",
        entity_type="HomeVisit",
        entity_id=visit.pk,
        description=lang_text(
            f"Создан выезд {visit.pk}",
            f"Үйге бару құрылды: {visit.pk}",
        ),
        changes={"patients": [patient.pk for patient in patients], **cleaned_data},
    )
    return visit


@transaction.atomic
def update_home_visit(*, user: User, visit: HomeVisit, cleaned_data: dict, patients) -> HomeVisit:
    for field, value in cleaned_data.items():
        setattr(visit, field, value)
    visit.save()
    visit.visit_patients.all().delete()
    HomeVisitPatient.objects.bulk_create(
        [HomeVisitPatient(home_visit=visit, patient=patient) for patient in patients]
    )
    log_action(
        user=user,
        action="update",
        entity_type="HomeVisit",
        entity_id=visit.pk,
        description=lang_text(
            f"Обновлен выезд {visit.pk}",
            f"Үйге бару жаңартылды: {visit.pk}",
        ),
        changes={"patients": [patient.pk for patient in patients], **cleaned_data},
    )
    return visit
