from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponseBase


class CanCreateMixin(LoginRequiredMixin):
    """A User must have the `can_create` boolean set in order to perform any actions.

    After signing up an admin has to set the boolean, otherwise anyone could start creating campaigns and characters.

    TODO: If this ever gets traction this will be set after payment.
    """

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        if not getattr(request.user, "can_create", False):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class CanCreateCampaignMixin(CanCreateMixin):
    """Check whether the User has the `can_be_dm` boolean.

    This is set to always be True for now but can change in the future.
    """

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        if not getattr(request.user, "can_be_dm", False):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
