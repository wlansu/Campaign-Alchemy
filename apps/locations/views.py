from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.forms import HiddenInput
from django.http import HttpRequest, HttpResponse, HttpResponseBase
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.generic import DeleteView, UpdateView

from apps.locations.forms import LocationForm
from apps.locations.models import Location
from apps.maps.models import Map
from apps.users.models import User


@login_required
@require_http_methods(["GET", "POST"])
def add_location(request: HttpRequest, campaign_pk: int, map_pk: int) -> HttpResponse:
    user: User = request.user
    if not user.has_read_access_to_campaign(campaign_pk=campaign_pk):
        raise PermissionDenied
    if request.method == "POST":
        form = LocationForm(request.POST, files=request.FILES)
        form.instance.map = Map.objects.get(id=map_pk)
        if form.is_valid():
            form.save()
            return redirect(
                reverse(
                    "campaigns:maps:detail",
                    kwargs={
                        "campaign_pk": campaign_pk,
                        "map_pk": map_pk,
                    },
                )
            )
    else:
        form = LocationForm()
        return render(
            request,
            "locations/location_form.html",
            {"form": form, "campaign_pk": campaign_pk, "map_pk": map_pk},
        )


@login_required
@require_http_methods(["GET"])
def location_list(request: HttpRequest, campaign_pk: int, map_pk: int) -> HttpResponse:
    user: User = request.user
    if not user.has_read_access_to_campaign(campaign_pk=campaign_pk):
        raise PermissionDenied
    return render(
        request,
        "locations/location_list.html",
        {
            "locations": Location.objects.filter(map=map_pk),
        },
    )


class LocationUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    View for Campaigns Update.
    """

    model = Location
    form_class = LocationForm
    template_name = "locations/location_form.html"
    context_object_name = "location"
    success_message = _("Location successfully updated")
    pk_url_kwarg = "location_pk"

    def get_success_url(self) -> str:
        """
        Override get_success_url method to redirect to Map Detail.
        """
        return reverse(
            "campaigns:maps:detail",
            kwargs={
                "campaign_pk": self.object.map.campaign_pk,
                "map_pk": self.object.map.pk,
            },
        )

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponseBase:
        """Anyone with access to the Campaign can update a Location.."""
        user: User = request.user
        if not user.is_authenticated:
            return self.handle_no_permission()
        campaign_pk = kwargs.get("campaign_pk", None)
        if not user.has_read_access_to_campaign(campaign_pk=campaign_pk):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["campaign_pk"] = self.object.map.campaign_id
        context["map_pk"] = self.object.map.id
        return context

    def get_form(self, form_class=None) -> LocationForm:
        form = super().get_form(form_class)
        form.fields["longitude"].widget = HiddenInput()
        form.fields["latitude"].widget = HiddenInput()
        return form


class LocationDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    View for Location Delete.
    """

    model = Location
    template_name = "confirm_delete.html"
    success_message = _("Location successfully deleted")
    pk_url_kwarg = "location_pk"

    def get_success_url(self) -> str:
        """
        Override get_success_url method to redirect to Map Detail.
        """
        return reverse(
            "campaigns:maps:detail",
            kwargs={
                "campaign_pk": self.object.map.campaign_id,
                "map_pk": self.object.map.pk,
            },
        )

    def get_object(self, queryset: QuerySet = None) -> Map:
        """Only a DM can delete a location."""
        location = super().get_object(queryset)
        if self.request.user == location.map.campaign.dm:
            return location
        raise PermissionDenied

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["campaign_pk"] = self.object.map.campaign_id
        context["map_pk"] = self.object.map.id
        return context
