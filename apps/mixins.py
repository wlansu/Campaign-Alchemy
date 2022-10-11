from typing import Any

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
