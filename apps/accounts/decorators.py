from __future__ import annotations

from collections.abc import Iterable
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from apps.accounts.services import user_in_group


def roles_required(*groups: str):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if request.user.is_superuser or any(user_in_group(request.user, name) for name in groups):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied

        return _wrapped

    return decorator
