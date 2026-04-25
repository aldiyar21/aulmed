from __future__ import annotations

from collections.abc import Iterable

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from apps.accounts.services import user_in_group


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_groups: Iterable[str] = ()

    def test_func(self) -> bool:
        user = self.request.user
        return user.is_superuser or any(user_in_group(user, group) for group in self.allowed_groups)
