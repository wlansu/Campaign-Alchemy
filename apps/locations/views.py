from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.forms import BaseForm
from django.http import HttpRequest, HttpResponse, HttpResponseBase
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.locations.forms import LocationForm
from apps.locations.models import Location
from apps.maps.models import Map
from apps.mixins import CanCreateMixin
from apps.users.models import User


class LocationDispatchMixin:
    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponseBase:
        """Anyone with access to the Campaign can perform CRUD operations on a Location."""
        user: User = request.user
        if not user.is_authenticated:
            return self.handle_no_permission()
        campaign_pk = kwargs["campaign_pk"]
        if not user.has_read_access_to_campaign(campaign_pk=campaign_pk):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class CampaignAndMapIncluded:
    def get_context_data(self, **kwargs) -> dict:
        """Pass the campaign and map pk's to the template context."""
        context = super().get_context_data(**kwargs)
        context["campaign_pk"] = self.kwargs["campaign_pk"]
        context["map_pk"] = self.kwargs["map_pk"]
        return context

    def get_success_url(self) -> str:
        return reverse(
            "campaigns:maps:detail",
            kwargs={
                "campaign_pk": self.kwargs["campaign_pk"],
                "map_pk": self.kwargs["map_pk"],
            },
        )


class LocationCreateView(
    CanCreateMixin, LocationDispatchMixin, CampaignAndMapIncluded, CreateView
):

    form_class = LocationForm
    template_name = "locations/location_form.html"

    def form_valid(self, form: LocationForm) -> HttpResponse:
        """Set the Locations Map by retrieving the map pk from the url.

        Return a No-Content and set the HTMX trigger so the modal will be closed and the location list refreshed.
        """
        form.instance.map = Map.objects.get(id=self.kwargs["map_pk"])
        self.object = form.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "locationListChanged"})


class LocationListView(CanCreateMixin, ListView):

    model = Location
    template_name = "locations/location_list.html"
    context_object_name = "locations"

    def get_queryset(self) -> QuerySet:
        """Acceptance criteria:
        - Anyone with access to the Campaign can see Locations.
        """
        campaign_pk = self.kwargs["campaign_pk"]
        map_pk = self.kwargs["map_pk"]
        user: User = self.request.user
        if campaign_pk and map_pk:
            if not user.has_read_access_to_campaign(campaign_pk=campaign_pk):
                raise PermissionDenied
            return (
                Location.objects.select_related("map", "map__campaign")
                .filter(map__campaign=campaign_pk)
                .filter(map=map_pk)
            )

        return Location.objects.none()


class LocationUpdateView(
    CanCreateMixin, LocationDispatchMixin, CampaignAndMapIncluded, UpdateView
):

    model = Location
    form_class = LocationForm
    template_name = "locations/location_form.html"
    context_object_name = "location"
    pk_url_kwarg = "location_pk"

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """Return a No-Content and set the HTMX trigger so the modal will be closed.

        There is no need to refresh the location list as the marker position cannot be changed.
        """
        self.object = form.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "locationChanged"})


class LocationDeleteView(CanCreateMixin, CampaignAndMapIncluded, DeleteView):

    model = Location
    template_name = "confirm_delete.html"
    pk_url_kwarg = "location_pk"

    def get_success_url(self) -> str:
        return reverse(
            "campaigns:maps:detail",
            kwargs={
                "campaign_pk": self.object.map.campaign_id,
                "map_pk": self.object.map_id,
            },
        )


class LocationDetailView(CanCreateMixin, CampaignAndMapIncluded, DetailView):

    model = Location
    template_name = "locations/location_detail.html"
    pk_url_kwarg = "location_pk"
    context_object_name = "location"

    def get_object(self, queryset: QuerySet = None) -> Location:
        """Acceptance criteria:
        - Anyone with access to the Campaign can view the Location.
        """
        user: User = self.request.user
        campaign_pk = self.kwargs["campaign_pk"]
        if user.has_read_access_to_campaign(campaign_pk=campaign_pk):
            return super().get_object(queryset)
        raise PermissionDenied
