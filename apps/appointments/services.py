from __future__ import annotations

from django.contrib.auth.models import User
from django.db import transaction

from apps.appointments.models import Appointment
from apps.audit.services import log_action
from apps.telemedicine.services import ensure_online_consultation_for_appointment


@transaction.atomic
def create_appointment(*, user: User, patient, cleaned_data: dict) -> Appointment:
    appointment = Appointment.objects.create(patient=patient, created_by=user, **cleaned_data)
    log_action(
        user=user,
        action="create",
        entity_type="Appointment",
        entity_id=appointment.pk,
        description=f"Created appointment {appointment.pk} for {appointment.patient}",
        changes=cleaned_data,
    )
    if appointment.appointment_type == Appointment.AppointmentType.ONLINE:
        ensure_online_consultation_for_appointment(appointment=appointment, created_by=user)
    return appointment


@transaction.atomic
def update_appointment(*, user: User, appointment: Appointment, cleaned_data: dict) -> Appointment:
    previous_status = appointment.status
    previous_type = appointment.appointment_type
    for field, value in cleaned_data.items():
        setattr(appointment, field, value)
    appointment.save()
    log_action(
        user=user,
        action="status_change" if previous_status != appointment.status else "update",
        entity_type="Appointment",
        entity_id=appointment.pk,
        description=f"Updated appointment {appointment.pk}",
        changes=cleaned_data,
    )
    if appointment.appointment_type == Appointment.AppointmentType.ONLINE and appointment.status in {
        Appointment.Status.APPROVED,
        Appointment.Status.SCHEDULED,
    }:
        ensure_online_consultation_for_appointment(appointment=appointment, created_by=user)
    elif previous_type != appointment.appointment_type and appointment.appointment_type == Appointment.AppointmentType.ONLINE:
        ensure_online_consultation_for_appointment(appointment=appointment, created_by=user)
    return appointment
