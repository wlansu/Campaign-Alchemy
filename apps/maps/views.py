from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.forms import BaseForm
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBase
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


class CampaignIncluded(LoginRequiredMixin):
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
    """
    View for Maps List.
    """

    model = Map
    template_name = "maps/map_list.html"
    context_object_name = "maps"

    def get_queryset(self) -> QuerySet:
        """
        Get queryset for Maps List.
        """
        campaign_pk = self.kwargs["campaign_pk"]
        if self.request.user.has_read_access_to_campaign(campaign_pk=campaign_pk):
            return Map.objects.filter(campaign=campaign_pk)
        raise PermissionDenied()


class MapDetailView(LoginRequiredMixin, DetailView):
    """
    View for Maps Detail.
    """

    model = Map
    template_name = "maps/map_detail.html"
    context_object_name = "map"
    pk_url_kwarg = "map_pk"

    def get_object(self, queryset: QuerySet = None) -> Map:
        map = super().get_object(queryset)
        if self.request.user.has_read_access_to_campaign(campaign_pk=map.campaign_id):
            return map
        raise PermissionDenied()

    def get_context_data(self, **kwargs) -> dict:
        """Add location form to context."""
        context = super().get_context_data(**kwargs)
        context["location_form"] = LocationForm(
            initial={"map": Map.objects.get(id=self.kwargs["map_pk"])}
        )
        return context

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["maps/map_partial_detail.html"]
        return [self.template_name]


class MapCreateView(CampaignIncluded, CreateView):
    """
    View for Map Create.
    """

    model = Map
    fields = ["name", "description", "image"]
    template_name = "maps/map_form.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponseBase:
        """Only a DM can create a Map."""
        campaign_pk = kwargs.get("campaign_pk", None)
        if not campaign_pk:
            raise Http404
        campaign = get_object_or_404(Campaign, id=campaign_pk)
        if request.user == campaign.dm:
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """
        Override form_valid method to set the active campaign.
        """
        form.instance.campaign = Campaign.objects.get(id=self.kwargs["campaign_pk"])
        self.object = form.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "mapListChanged"})


class MapUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for Campaigns Update.
    """

    model = Map
    fields = ["name", "description", "image"]
    template_name = "maps/map_form.html"
    context_object_name = "map"
    pk_url_kwarg = "map_pk"

    def get_object(self, queryset: QuerySet = None) -> Map:
        """Only a DM can update the map."""
        map = super().get_object(queryset)
        if self.request.user == map.campaign.dm:
            return map
        raise PermissionDenied

    def form_valid(self, form: BaseForm) -> HttpResponse:
        self.object = form.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "mapChanged"})


class MapDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    View for Map Delete.
    """

    model = Map
    template_name = "confirm_delete.html"
    pk_url_kwarg = "map_pk"
    success_message = "Map successfully deleted"

    def get_object(self, queryset: QuerySet = None) -> Map:
        map = super().get_object(queryset)
        if self.request.user == map.campaign.dm:
            return map
        raise PermissionDenied()

    def get_success_url(self) -> str:
        """
        Override get_success_url method to redirect to Campaigns List.
        """
        return reverse(
            "campaigns:detail", kwargs={"campaign_pk": self.object.campaign_id}
        )
