from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.forms import HiddenInput
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBase
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.locations.forms import LocationForm
from apps.locations.models import Location
from apps.maps.models import Map
from apps.mixins import CanCreateMixin
from apps.users.models import User


class LocationCreateView(CanCreateMixin, CreateView):

    form_class = LocationForm
    template_name = "locations/location_form.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponseBase:
        """Anyone with access to the Campaign can update a Location.."""
        user: User = request.user
        if not user.is_authenticated:
            return self.handle_no_permission()
        campaign_pk = kwargs.get("campaign_pk", None)
        if not user.has_read_access_to_campaign(campaign_pk=campaign_pk):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: LocationForm) -> HttpResponse:
        form.instance.map = Map.objects.get(id=self.kwargs["map_pk"])
        return super().form_valid(form)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["campaign_pk"] = self.kwargs["campaign_pk"]
        context["map_pk"] = self.kwargs["map_pk"]
        return context

    def get_success_url(self) -> str:
        """
        Override get_success_url method to redirect to Map Detail.
        """
        return reverse(
            "campaigns:maps:detail",
            kwargs={
                "campaign_pk": self.kwargs["campaign_pk"],
                "map_pk": self.kwargs["map_pk"],
            },
        )


class LocationListView(CanCreateMixin, ListView):

    model = Location
    template_name = "locations/location_list.html"
    context_object_name = "locations"

    def get_queryset(self) -> QuerySet:
        campaign_pk = self.kwargs.get("campaign_pk", None)
        map_pk = self.kwargs.get("map_pk", None)
        user: User = self.request.user
        if campaign_pk and map_pk:
            if not user.has_read_access_to_campaign(campaign_pk=campaign_pk):
                raise PermissionDenied
            return (
                Location.objects.select_related("map", "map__campaign")
                .filter(map__campaign=campaign_pk)
                .filter(map=map_pk)
            )

        raise Http404


class LocationUpdateView(CanCreateMixin, UpdateView):
    """
    View for Campaigns Update.
    """

    model = Location
    form_class = LocationForm
    template_name = "locations/location_form.html"
    context_object_name = "location"
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


class LocationDeleteView(CanCreateMixin, DeleteView):
    """
    View for Location Delete.
    """

    model = Location
    template_name = "confirm_delete.html"
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
