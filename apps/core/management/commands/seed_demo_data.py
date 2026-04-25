from __future__ import annotations

import random
from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import EmployeeProfile
from apps.accounts.services import ensure_role_groups
from apps.encounters.models import Encounter
from apps.facilities.models import Facility
from apps.patients.models import Patient, PatientCondition
from apps.prevention.models import PreventionEvent
from apps.referrals.models import Referral
from apps.visits.models import HomeVisit, HomeVisitPatient


class Command(BaseCommand):
    help = "Заполняет систему демонстрационными данными"

    settlements = ["Аксай", "Жанатурмыс", "Карасу", "Теренколь", "Жайык"]
    positions = ["Фельдшер", "Врач общей практики", "Регистратор", "Заведующий"]

    def handle(self, *args, **options):
        ensure_role_groups()
        self._create_facilities()
        self._create_employees()
        self._create_patients()
        self._create_encounters()
        self._create_visits()
        self._create_prevention()
        self._create_referrals()
        self.stdout.write(self.style.SUCCESS("Демо-данные загружены"))

    def _create_facilities(self):
        if Facility.objects.count() >= 3:
            return
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
        if EmployeeProfile.objects.count() >= 8:
            return
        facilities = list(Facility.objects.all())
        roles = [
            ("admin", "Системный", "Администратор", "admin"),
            ("registrator", "Айгерим", "Регистратор", "registrar"),
            ("manager", "Ерлан", "Заведующий", "manager"),
            ("doctor1", "Марат", "Врач", "clinician"),
            ("doctor2", "Сауле", "Врач", "clinician"),
            ("doctor3", "Нуржан", "Фельдшер", "clinician"),
            ("nurse1", "Гульмира", "Медсестра", "clinician"),
            ("nurse2", "Асель", "Фельдшер", "clinician"),
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
            profile, _ = EmployeeProfile.objects.get_or_create(
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
        if Patient.objects.count() >= 100:
            return
        facilities = list(Facility.objects.all())
        last_names = ["Серикова", "Абдрахманов", "Тулегенова", "Смагулов", "Куанышбекова", "Исаев"]
        first_names = ["Айжан", "Бекзат", "Дина", "Ерасыл", "Жанар", "Мадина", "Руслан", "Самат"]
        social_categories = [choice[0] for choice in Patient.SOCIAL_CATEGORY_CHOICES]
        risks = [choice[0] for choice in Patient.RISK_LEVEL_CHOICES]
        for index in range(100):
            facility = facilities[index % len(facilities)]
            defaults = {
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
            }
            if index < 80:
                patient, created = Patient.objects.get_or_create(
                    iin=f"{900000000000 + index}",
                    defaults=defaults,
                )
            else:
                patient = Patient.objects.create(iin=None, **defaults)
                created = True
            if created and index % 4 == 0:
                PatientCondition.objects.create(
                    patient=patient,
                    condition_name="Артериальная гипертензия",
                    icd_code="I10",
                    is_chronic=True,
                    diagnosed_at=timezone.localdate() - timedelta(days=600),
                )

    def _create_encounters(self):
        if Encounter.objects.count() >= 150:
            return
        patients = list(Patient.objects.active()[:100])
        clinicians = list(EmployeeProfile.objects.filter(role_code="clinician"))
        types = [choice[0] for choice in Encounter.ENCOUNTER_TYPES]
        results = [choice[0] for choice in Encounter.RESULT_TYPES]
        for index in range(150):
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
        if HomeVisit.objects.count() >= 20:
            return
        clinicians = list(EmployeeProfile.objects.filter(role_code="clinician"))
        patients = list(Patient.objects.active())
        for index in range(20):
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
            for patient in random.sample(patients, k=random.randint(1, 4)):
                HomeVisitPatient.objects.get_or_create(home_visit=visit, patient=patient)

    def _create_prevention(self):
        if PreventionEvent.objects.count() >= 40:
            return
        patients = list(Patient.objects.active())
        clinicians = list(EmployeeProfile.objects.filter(role_code="clinician"))
        event_types = [choice[0] for choice in PreventionEvent.EVENT_TYPES]
        statuses = [choice[0] for choice in PreventionEvent.STATUS_CHOICES]
        for index in range(40):
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
        if Referral.objects.count() >= 25:
            return
        patients = list(Patient.objects.active())
        creators = list(EmployeeProfile.objects.exclude(role_code="registrar"))
        priorities = [choice[0] for choice in Referral.PRIORITY_CHOICES]
        statuses = [choice[0] for choice in Referral.STATUS_CHOICES]
        for index in range(25):
            patient = random.choice(patients)
            Referral.objects.create(
                patient=patient,
                source_encounter=patient.encounters.order_by("?").first(),
                created_by=random.choice(creators),
                destination_org="Областная консультативная поликлиника",
                destination_specialist=random.choice(["Кардиолог", "Эндокринолог", "Невролог"]),
                reason="Требуется специализированная консультация",
                priority=random.choice(priorities),
                status=random.choice(statuses),
                referral_date=timezone.localdate() - timedelta(days=random.randint(0, 60)),
                result_note="Результат уточняется",
            )
