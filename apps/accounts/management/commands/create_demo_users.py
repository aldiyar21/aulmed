from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from apps.accounts.models import EmployeeProfile
from apps.accounts.services import ensure_role_groups
from apps.facilities.models import Facility


class Command(BaseCommand):
    help = "Создает роли и демо-пользователей"

    def handle(self, *args, **options):
        ensure_role_groups()
        facility = Facility.objects.first()
        users = [
            ("admin", "Администратор", "admin", settings.ROLE_ADMIN),
            ("registrator", "Регистратор", "registrar", settings.ROLE_REGISTRAR),
            ("doctor", "Медработник", "clinician", settings.ROLE_CLINICIAN),
            ("manager", "Руководитель", "manager", settings.ROLE_MANAGER),
        ]
        for username, first_name, role_code, group_name in users:
            user, created = User.objects.get_or_create(username=username, defaults={"first_name": first_name})
            user.first_name = first_name
            user.set_password("demo12345")
            user.is_staff = True
            user.save()
            user.groups.set([Group.objects.get(name=group_name)])
            EmployeeProfile.objects.get_or_create(
                user=user,
                defaults={
                    "facility": facility,
                    "position": first_name,
                    "role_code": role_code,
                    "phone": "+77000000000",
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Создан пользователь {username}"))
