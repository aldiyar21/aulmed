from __future__ import annotations

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from apps.accounts.services import get_linked_patient, user_in_group, user_is_patient


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


def patient_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if user_is_patient(request.user) and get_linked_patient(request.user):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied

    return _wrapped
