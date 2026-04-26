from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.audit.services import log_action
from apps.core.i18n import lang_text
from apps.core.models import Notification
from apps.telemedicine.models import OnlineConsultation, PatientConsent, Teleconsilium


def get_consent_text() -> str:
    return lang_text(
        "Я подтверждаю согласие на получение телемедицинской консультации и обработку персональных "
        "медицинских данных в рамках системы AulMed. Я понимаю, что при экстренных состояниях "
        "необходимо обращаться в службу 103.",
        "Мен AulMed жүйесі аясында телемедициналық консультация алуға және жеке медициналық "
        "деректерімді өңдеуге келісім беремін. Шұғыл жағдайларда 103 қызметіне жүгіну қажет екенін "
        "түсінемін.",
    )


def ensure_online_consultation_for_appointment(*, appointment, created_by):
    consultation, created = OnlineConsultation.objects.get_or_create(
        appointment=appointment,
        defaults={
            "patient": appointment.patient,
            "doctor": appointment.doctor or created_by,
            "facility": appointment.facility,
            "status": OnlineConsultation.Status.SCHEDULED if appointment.status in {"approved", "scheduled"} else OnlineConsultation.Status.REQUESTED,
            "scheduled_start": appointment.scheduled_datetime or appointment.requested_datetime,
            "scheduled_end": (appointment.scheduled_datetime or appointment.requested_datetime) + timedelta(minutes=appointment.duration_minutes),
            "complaint": appointment.reason,
            "created_by": created_by,
            "jitsi_domain": settings.JITSI_DOMAIN,
        },
    )
    if not created:
        updated_fields = []
        for field, value in {
            "patient": appointment.patient,
            "doctor": appointment.doctor or consultation.doctor,
            "facility": appointment.facility,
            "complaint": appointment.reason,
            "scheduled_start": appointment.scheduled_datetime or appointment.requested_datetime,
            "scheduled_end": (appointment.scheduled_datetime or appointment.requested_datetime) + timedelta(minutes=appointment.duration_minutes),
        }.items():
            current_value = getattr(consultation, f"{field}_id") if field in {"patient", "doctor", "facility"} else getattr(consultation, field)
            compare_value = value.pk if field in {"patient", "doctor", "facility"} and value is not None else value
            if current_value != compare_value:
                setattr(consultation, field, value)
                updated_fields.append(field)
        target_status = OnlineConsultation.Status.SCHEDULED if appointment.status in {"approved", "scheduled"} else consultation.status
        if consultation.status != target_status:
            consultation.status = target_status
            updated_fields.append("status")
        if updated_fields:
            consultation.save()
    log_action(
        user=created_by,
        action="create" if created else "update",
        entity_type="OnlineConsultation",
        entity_id=consultation.pk,
        description=f"Ensured online consultation for appointment {appointment.pk}",
        changes={"appointment_id": appointment.pk, "created": created},
    )
    return consultation


def start_consultation(*, user, consultation: OnlineConsultation):
    consultation.status = OnlineConsultation.Status.IN_PROGRESS
    consultation.actual_started_at = timezone.now()
    consultation.save(update_fields=["status", "actual_started_at", "updated_at"])
    log_action(
        user=user,
        action="start_consultation",
        entity_type="OnlineConsultation",
        entity_id=consultation.pk,
        description=f"Started consultation {consultation.pk}",
        changes={"status": consultation.status},
    )
    return consultation


def complete_consultation(*, user, consultation: OnlineConsultation, cleaned_data: dict):
    for field, value in cleaned_data.items():
        setattr(consultation, field, value)
    consultation.status = OnlineConsultation.Status.COMPLETED
    consultation.actual_ended_at = timezone.now()
    consultation.save()
    log_action(
        user=user,
        action="complete_consultation",
        entity_type="OnlineConsultation",
        entity_id=consultation.pk,
        description=f"Completed consultation {consultation.pk}",
        changes=cleaned_data,
    )
    return consultation


def cancel_consultation(*, user, consultation: OnlineConsultation):
    consultation.status = OnlineConsultation.Status.CANCELLED
    consultation.save(update_fields=["status", "updated_at"])
    log_action(
        user=user,
        action="cancel_consultation",
        entity_type="OnlineConsultation",
        entity_id=consultation.pk,
        description=f"Cancelled consultation {consultation.pk}",
        changes={"status": consultation.status},
    )
    return consultation


def accept_patient_consent(*, user, patient, consultation, ip_address: str | None):
    consent, created = PatientConsent.objects.get_or_create(
        patient=patient,
        consultation=consultation,
        consent_type=PatientConsent.ConsentType.TELEMEDICINE,
        defaults={
            "accepted_at": timezone.now(),
            "accepted_by": user,
            "text_snapshot": get_consent_text(),
            "ip_address": ip_address,
        },
    )
    log_action(
        user=user,
        action="accept_consent",
        entity_type="PatientConsent",
        entity_id=consent.pk,
        description=f"Accepted telemedicine consent for consultation {consultation.pk}",
        changes={"consultation_id": consultation.pk, "created": created},
    )
    return consent


def create_teleconsilium(*, user, cleaned_data: dict):
    invited_doctors = cleaned_data.pop("invited_doctors", [])
    teleconsilium = Teleconsilium.objects.create(primary_doctor=user, **cleaned_data)
    teleconsilium.invited_doctors.set(invited_doctors)
    for doctor in invited_doctors:
        Notification.objects.create(
            user=doctor,
            notification_type="teleconsilium",
            title=lang_text(f"Телеконсилиум: {teleconsilium.topic}", f"Телеконсилиум: {teleconsilium.topic}"),
            body=lang_text(
                f"Вы приглашены на телеконсилиум №{teleconsilium.pk}.",
                f"Сіз №{teleconsilium.pk} телеконсилиумына шақырылдыңыз.",
            ),
            due_date=teleconsilium.scheduled_at.date(),
        )
    log_action(
        user=user,
        action="create",
        entity_type="Teleconsilium",
        entity_id=teleconsilium.pk,
        description=f"Created teleconsilium {teleconsilium.pk}",
        changes={"topic": teleconsilium.topic, "invited_doctors": [doctor.pk for doctor in invited_doctors]},
    )
    return teleconsilium


def update_teleconsilium(*, user, teleconsilium: Teleconsilium, cleaned_data: dict):
    invited_doctors = cleaned_data.pop("invited_doctors", None)
    for field, value in cleaned_data.items():
        setattr(teleconsilium, field, value)
    teleconsilium.save()
    if invited_doctors is not None:
        teleconsilium.invited_doctors.set(invited_doctors)
    log_action(
        user=user,
        action="update",
        entity_type="Teleconsilium",
        entity_id=teleconsilium.pk,
        description=f"Updated teleconsilium {teleconsilium.pk}",
        changes=cleaned_data,
    )
    return teleconsilium
