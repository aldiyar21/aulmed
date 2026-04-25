from __future__ import annotations

import random
from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import EmployeeProfile
from apps.accounts.services import ensure_role_groups
from apps.appointments.models import Appointment
from apps.documents.models import MedicalDocument, PatientFile, Prescription
from apps.documents.services import create_medical_document, create_prescription
from apps.encounters.models import Encounter
from apps.facilities.models import Facility
from apps.monitoring.models import VitalReading
from apps.monitoring.services import create_vital_reading
from apps.patients.models import Patient, PatientCondition
from apps.prevention.models import PreventionEvent
from apps.referrals.models import Referral
from apps.telemedicine.models import OnlineConsultation, Teleconsilium
from apps.telemedicine.services import (
    create_teleconsilium,
    ensure_online_consultation_for_appointment,
)
from apps.visits.models import HomeVisit, HomeVisitPatient


class Command(BaseCommand):
    help = "Заполняет систему демонстрационными данными"

    settlements = ["Аксай", "Жанатурмыс", "Карасу", "Теренколь", "Жайык"]

    def handle(self, *args, **options):
        ensure_role_groups()
        self._create_facilities()
        self._create_employees()
        self._create_patients()
        self._link_patient_user()
        self._create_encounters()
        self._create_visits()
        self._create_prevention()
        self._create_referrals()
        self._create_appointments_and_consultations()
        self._create_documents_and_prescriptions()
        self._create_vitals()
        self._create_patient_file()
        self.stdout.write(self.style.SUCCESS("Демо-данные загружены"))

    def _create_facilities(self):
        facilities = [
            ("ФАП Аксай", "fap", "Кызылординская область", "Сырдарьинский", "Аксай"),
            ("Амбулатория Жанатурмыс", "ambulatoria", "Кызылординская область", "Жалагашский", "Жанатурмыс"),
            ("Сельская поликлиника Карасу", "clinic", "Кызылординская область", "Шиелийский", "Карасу"),
        ]
        for name, facility_type, region, district, settlement in facilities:
            Facility.objects.get_or_create(
                name=name,
                defaults={
                    "facility_type": facility_type,
                    "region": region,
                    "district": district,
                    "settlement_name": settlement,
                    "address": f"{settlement}, ул. Центральная, 1",
                    "phone": "+77242000000",
                },
            )

    def _create_employees(self):
        facilities = list(Facility.objects.all())
        roles = [
            ("admin", "Системный", "Администратор", "admin"),
            ("registrator", "Айгерим", "Регистратор", "registrar"),
            ("manager", "Ерлан", "Заведующий", "manager"),
            ("doctor", "Марат", "Врач", "clinician"),
            ("doctor2", "Сауле", "Врач", "clinician"),
            ("doctor3", "Нуржан", "Фельдшер", "clinician"),
        ]
        for index, (username, first_name, position, role_code) in enumerate(roles):
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={"first_name": first_name, "last_name": f"Тестов{index}"},
            )
            user.first_name = first_name
            user.last_name = f"Тестов{index}"
            user.is_staff = True
            user.set_password("demo12345")
            user.save()
            EmployeeProfile.objects.get_or_create(
                user=user,
                defaults={
                    "facility": facilities[index % len(facilities)],
                    "position": position,
                    "role_code": role_code,
                    "phone": f"+7701000{index:04d}",
                },
            )
            group_name = {
                "admin": "Администратор системы",
                "registrar": "Регистратор",
                "manager": "Руководитель",
                "clinician": "Медработник",
            }[role_code]
            user.groups.set([Group.objects.get(name=group_name)])

    def _create_patients(self):
        facilities = list(Facility.objects.all())
        last_names = ["Серикова", "Абдрахманова", "Тулегенов", "Смагулов", "Куанышбекова", "Исаев"]
        first_names = ["Айжан", "Бекзат", "Дина", "Ерасыл", "Жанар", "Мадина", "Руслан", "Самат"]
        social_categories = [choice[0] for choice in Patient.SOCIAL_CATEGORY_CHOICES]
        risks = [choice[0] for choice in Patient.RISK_LEVEL_CHOICES]
        for index in range(100):
            facility = facilities[index % len(facilities)]
            patient, created = Patient.objects.get_or_create(
                iin=f"{900000000000 + index}",
                defaults={
                    "last_name": random.choice(last_names),
                    "first_name": random.choice(first_names),
                    "middle_name": "Тестович",
                    "birth_date": timezone.localdate() - timedelta(days=random.randint(365, 30000)),
                    "sex": "female" if index % 2 == 0 else "male",
                    "phone": f"+7702{index:07d}",
                    "address": f"ул. Полевая, д. {index + 1}",
                    "settlement_name": random.choice(self.settlements),
                    "facility": facility,
                    "social_category": random.choice(social_categories),
                    "risk_level": random.choice(risks),
                    "attachment_date": timezone.localdate() - timedelta(days=random.randint(30, 1000)),
                    "notes": "Демо-пациент",
                },
            )
            if created and index % 4 == 0:
                PatientCondition.objects.create(
                    patient=patient,
                    condition_name="Артериальная гипертензия",
                    icd_code="I10",
                    is_chronic=True,
                    diagnosed_at=timezone.localdate() - timedelta(days=600),
                )

    def _link_patient_user(self):
        patient_user, _ = User.objects.get_or_create(username="patient", defaults={"first_name": "Пациент"})
        patient_user.set_password("demo12345")
        patient_user.is_staff = False
        patient_user.save()
        patient_user.groups.set([Group.objects.get(name="Пациент")])
        patient = Patient.objects.order_by("pk").first()
        if patient and patient.patient_user_id != patient_user.pk:
            patient.patient_user = patient_user
            patient.save(update_fields=["patient_user"])

    def _create_encounters(self):
        if Encounter.objects.exists():
            return
        patients = list(Patient.objects.active()[:20])
        clinicians = list(EmployeeProfile.objects.filter(role_code="clinician"))
        types = [choice[0] for choice in Encounter.ENCOUNTER_TYPES]
        results = [choice[0] for choice in Encounter.RESULT_TYPES]
        for _ in range(40):
            patient = random.choice(patients)
            clinician = random.choice(clinicians)
            Encounter.objects.create(
                patient=patient,
                facility=patient.facility,
                clinician=clinician,
                encounter_type=random.choice(types),
                encounter_date=timezone.localdate() - timedelta(days=random.randint(0, 90)),
                reason_for_visit="Жалобы на общее недомогание",
                diagnosis_text="Острое респираторное заболевание",
                services_provided="Осмотр, рекомендации, назначение лечения",
                result_type=random.choice(results),
                next_visit_date=timezone.localdate() + timedelta(days=random.randint(3, 30)),
                notes="Демо-обращение",
            )

    def _create_visits(self):
        if HomeVisit.objects.exists():
            return
        clinicians = list(EmployeeProfile.objects.filter(role_code="clinician"))
        patients = list(Patient.objects.active()[:20])
        for _ in range(5):
            sample_patient = random.choice(patients)
            visit = HomeVisit.objects.create(
                planned_date=timezone.localdate() + timedelta(days=random.randint(-5, 15)),
                facility=sample_patient.facility,
                assigned_employee=random.choice(clinicians),
                settlement_name=sample_patient.settlement_name,
                status=random.choice(["planned", "completed", "cancelled"]),
                purpose="Патронаж и осмотр на дому",
                route_notes="Маршрут по населенному пункту",
                result_summary="Часть выезда выполнена",
            )
            for patient in random.sample(patients, k=random.randint(1, 3)):
                HomeVisitPatient.objects.get_or_create(home_visit=visit, patient=patient)

    def _create_prevention(self):
        if PreventionEvent.objects.exists():
            return
        patients = list(Patient.objects.active()[:20])
        clinicians = list(EmployeeProfile.objects.filter(role_code="clinician"))
        event_types = [choice[0] for choice in PreventionEvent.EVENT_TYPES]
        statuses = [choice[0] for choice in PreventionEvent.STATUS_CHOICES]
        for _ in range(15):
            status = random.choice(statuses)
            planned_date = timezone.localdate() + timedelta(days=random.randint(-30, 30))
            completed_date = planned_date if status == "completed" else None
            PreventionEvent.objects.create(
                patient=random.choice(patients),
                event_type=random.choice(event_types),
                planned_date=planned_date,
                completed_date=completed_date,
                status=status,
                assigned_employee=random.choice(clinicians),
                notes="Демо-мероприятие",
            )

    def _create_referrals(self):
        if Referral.objects.exists():
            return
        patients = list(Patient.objects.active()[:20])
        creators = list(EmployeeProfile.objects.exclude(role_code="registrar"))
        priorities = [choice[0] for choice in Referral.PRIORITY_CHOICES]
        statuses = [choice[0] for choice in Referral.STATUS_CHOICES]
        for _ in range(10):
            patient = random.choice(patients)
            Referral.objects.create(
                patient=patient,
                source_encounter=patient.encounters.first(),
                created_by=random.choice(creators),
                destination_org="Областная консультативная поликлиника",
                destination_specialist=random.choice(["Кардиолог", "Эндокринолог", "Невролог"]),
                reason="Требуется специализированная консультация",
                priority=random.choice(priorities),
                status=random.choice(statuses),
                referral_date=timezone.localdate() - timedelta(days=random.randint(0, 60)),
                result_note="Результат уточняется",
            )

    def _create_appointments_and_consultations(self):
        patient = Patient.objects.order_by("pk").first()
        doctor = User.objects.get(username="doctor")
        manager = User.objects.get(username="manager")
        if not Appointment.objects.exists():
            statuses = [
                Appointment.Status.REQUESTED,
                Appointment.Status.SCHEDULED,
                Appointment.Status.APPROVED,
            ]
            for index, status in enumerate(statuses, start=1):
                appointment = Appointment.objects.create(
                    patient=patient,
                    facility=patient.facility,
                    doctor=doctor,
                    created_by=patient.patient_user or manager,
                    appointment_type=Appointment.AppointmentType.ONLINE,
                    status=status,
                    requested_datetime=timezone.now() + timedelta(days=index),
                    scheduled_datetime=timezone.now() + timedelta(days=index, hours=1),
                    duration_minutes=30,
                    reason=f"Онлайн-запись {index}",
                )
                consultation = ensure_online_consultation_for_appointment(appointment=appointment, created_by=manager)
                if index == 3:
                    consultation.status = OnlineConsultation.Status.COMPLETED
                    consultation.anamnesis = "Жалобы на слабость"
                    consultation.diagnosis_text = "ОРВИ"
                    consultation.treatment_plan = "Покой, обильное питье"
                    consultation.doctor_recommendations = "Контроль температуры"
                    consultation.actual_started_at = timezone.now() - timedelta(hours=2)
                    consultation.actual_ended_at = timezone.now() - timedelta(hours=1, minutes=40)
                    consultation.save()
        if not Teleconsilium.objects.exists():
            create_teleconsilium(
                user=doctor,
                cleaned_data={
                    "patient": patient,
                    "facility": patient.facility,
                    "topic": "Сложный случай АГ",
                    "description": "Обсуждение дистанционного ведения пациента",
                    "status": Teleconsilium.Status.SCHEDULED,
                    "scheduled_at": timezone.now() + timedelta(days=2),
                    "invited_doctors": list(User.objects.filter(username__in=["doctor2", "doctor3"])),
                },
            )

    def _create_documents_and_prescriptions(self):
        patient = Patient.objects.order_by("pk").first()
        doctor = User.objects.get(username="doctor")
        consultation = OnlineConsultation.objects.filter(status=OnlineConsultation.Status.COMPLETED).first()
        if not MedicalDocument.objects.exists():
            create_medical_document(
                user=doctor,
                cleaned_data={
                    "patient": patient,
                    "consultation": consultation,
                    "document_type": MedicalDocument.DocumentType.RECOMMENDATION,
                    "title": "Рекомендации после онлайн-консультации",
                    "content": "Продолжить наблюдение, контролировать температуру и давление.",
                    "status": MedicalDocument.Status.ISSUED,
                },
            )
        if not Prescription.objects.exists():
            create_prescription(
                user=doctor,
                cleaned_data={
                    "patient": patient,
                    "consultation": consultation,
                    "status": Prescription.Status.ISSUED,
                    "notes": "Демо-рецепт",
                },
                items=[
                    {
                        "medication_name": "Парацетамол",
                        "dosage": "500 мг",
                        "frequency": "2 раза в день",
                        "duration": "3 дня",
                        "instructions": "После еды",
                    },
                    {
                        "medication_name": "Витамин C",
                        "dosage": "1000 мг",
                        "frequency": "1 раз в день",
                        "duration": "5 дней",
                        "instructions": "",
                    },
                ],
            )

    def _create_vitals(self):
        if VitalReading.objects.exists():
            return
        patient = Patient.objects.order_by("pk").first()
        patient_user = patient.patient_user
        for index in range(5):
            create_vital_reading(
                user=patient_user,
                patient=patient,
                source=VitalReading.Source.PATIENT_MANUAL,
                cleaned_data={
                    "recorded_at": timezone.now() - timedelta(days=index),
                    "systolic_bp": 120 + index,
                    "diastolic_bp": 80 + index,
                    "pulse": 72 + index,
                    "temperature": 36.6,
                    "spo2": 98,
                    "glucose": 5.2,
                    "weight": 70.0,
                    "comment": "Демо-показатель",
                },
            )

    def _create_patient_file(self):
        if PatientFile.objects.exists():
            return
        patient = Patient.objects.order_by("pk").first()
        doctor = User.objects.get(username="doctor")
        patient_file = PatientFile.objects.create(
            patient=patient,
            uploaded_by=doctor,
            result_type=PatientFile.ResultType.DOCUMENT,
            title="Демо-результат обследования",
            description="Тестовый файл для телемедицинского MVP",
            result_date=timezone.localdate(),
        )
        try:
            patient_file.file.save("demo-result.pdf", ContentFile(b"Demo examination result"), save=True)
        except Exception:
            patient_file.delete()
