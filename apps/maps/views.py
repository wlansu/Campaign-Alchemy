from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.forms import BaseForm
from django.http import HttpRequest, HttpResponse, HttpResponseBase
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.campaigns.models import Campaign
from apps.locations.forms import LocationForm
from apps.maps.models import Map
from apps.mixins import CanCreateMixin
from apps.users.models import User


class CampaignIncluded(CanCreateMixin):
    """Mixin that adds the campaign to the context."""

    def setup(self, request, *args, **kwargs) -> None:
        """Overloaded to set the campaign."""
        self.campaign = get_object_or_404(Campaign, pk=kwargs["campaign_pk"])
        super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        return context


class MapListView(CampaignIncluded, ListView):

    model = Map
    template_name = "maps/map_list.html"
    context_object_name = "maps"

    def get_queryset(self) -> QuerySet:
        """Acceptance criteria:
        - Anyone with access to the Campaign can view the maps.
        """
        campaign_pk = self.kwargs["campaign_pk"]
        user: User = self.request.user
        if user.has_read_access_to_campaign(campaign_pk=campaign_pk):
            return Map.objects.filter(campaign=campaign_pk)
        raise PermissionDenied


class MapDetailView(CanCreateMixin, DetailView):

    model = Map
    template_name = "maps/map_detail.html"
    context_object_name = "map"
    pk_url_kwarg = "map_pk"

    def get_object(self, queryset: QuerySet = None) -> Map:
        """Acceptance criteria:
        - Anyone with access to the Campaign can see the map.
        """
        map = super().get_object(queryset)
        user: User = self.request.user
        if user.has_read_access_to_campaign(campaign_pk=map.campaign_id):
            return map
        raise PermissionDenied

    def get_context_data(self, **kwargs) -> dict:
        """Pass the LocationForm to the template context."""
        context = super().get_context_data(**kwargs)
        context["location_form"] = LocationForm(
            initial={"map": Map.objects.get(id=self.kwargs["map_pk"])}
        )
        return context

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["maps/_partial_map_detail.html"]
        return [self.template_name]


class MapCreateView(CampaignIncluded, CreateView):

    model = Map
    fields = ["name", "description", "image"]
    template_name = "maps/map_form.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponseBase:
        """Acceptance criteria:
        - Any player with a character in the campaign can add a Map
        """
        user: User = request.user
        if not user.is_authenticated:
            return self.handle_no_permission()
        campaign_pk = kwargs["campaign_pk"]
        if user.has_read_access_to_campaign(campaign_pk=campaign_pk):
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """Set the active campaign by retrieving the campaign pk from the url.

        Return a No-Content and HTMX trigger to hide the modal and refresh the map list.
        """
        form.instance.campaign = Campaign.objects.get(id=self.kwargs["campaign_pk"])
        self.object = form.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "mapListChanged"})


class MapUpdateView(CanCreateMixin, UpdateView):

    model = Map
    fields = ["name", "description", "image"]
    template_name = "maps/map_form.html"
    context_object_name = "map"
    pk_url_kwarg = "map_pk"

    def get_object(self, queryset: QuerySet = None) -> Map:
        """Acceptance criteria:
        - Only a DM can update the map
        """
        map = super().get_object(queryset)
        if self.request.user == map.campaign.dm:
            return map
        raise PermissionDenied

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """Return a No-Content and HTMX trigger to hide the modal and refresh the map page."""
        self.object = form.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "mapChanged"})


class MapDeleteView(CanCreateMixin, DeleteView):

    model = Map
    template_name = "confirm_delete.html"
    pk_url_kwarg = "map_pk"

    def get_object(self, queryset: QuerySet = None) -> Map:
        """Acceptance criteria:
        - Only the DM can delete a Map
        """
        map = super().get_object(queryset)
        if self.request.user == map.campaign.dm:
            return map
        raise PermissionDenied()

    def get_success_url(self) -> str:
        return reverse(
            "campaigns:detail", kwargs={"campaign_pk": self.object.campaign_id}
        )
