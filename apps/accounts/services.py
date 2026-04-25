from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import Group, Permission, User


ROLE_GROUP_MAPPING = {
    "admin": settings.ROLE_ADMIN,
    "registrar": settings.ROLE_REGISTRAR,
    "clinician": settings.ROLE_CLINICIAN,
    "manager": settings.ROLE_MANAGER,
}


def get_user_role_names(user: User) -> list[str]:
    return list(user.groups.values_list("name", flat=True))


def user_in_group(user: User, group_name: str) -> bool:
    return user.is_superuser or user.groups.filter(name=group_name).exists()


def user_is_manager_or_admin(user: User) -> bool:
    return user.is_superuser or user.groups.filter(
        name__in=[settings.ROLE_ADMIN, settings.ROLE_MANAGER]
    ).exists()


def ensure_role_groups() -> None:
    group_permissions = {
        settings.ROLE_ADMIN: Permission.objects.all(),
        settings.ROLE_REGISTRAR: Permission.objects.filter(
            content_type__app_label__in=["patients", "encounters", "referrals", "visits", "facilities"]
        ),
        settings.ROLE_CLINICIAN: Permission.objects.filter(
            content_type__app_label__in=["patients", "encounters", "visits", "prevention", "referrals"]
        ),
        settings.ROLE_MANAGER: Permission.objects.filter(
            content_type__app_label__in=[
                "patients",
                "encounters",
                "visits",
                "prevention",
                "referrals",
                "reports",
                "facilities",
                "accounts",
                "audit",
            ]
        ),
    }
    for name, permissions in group_permissions.items():
        group, _ = Group.objects.get_or_create(name=name)
        group.permissions.set(permissions)
