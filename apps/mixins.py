from typing import Any

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponseBase


class CanCreateMixin(LoginRequiredMixin):
    """A User must have the `can_create` boolean set in order to perform any actions."""

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        if not hasattr(request.user, "can_create"):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


def create_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    """
    Decorator for views that checks that the user.can_create boolean is set, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: True if hasattr(u, "can_create") and u.is_authenticated else False,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
