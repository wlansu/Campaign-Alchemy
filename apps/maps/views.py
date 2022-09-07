from dataclasses import dataclass

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.campaigns.models import Campaign
from apps.maps.models import Location, Map


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
    template_name = "maps/maps_list.html"
    context_object_name = "maps"

    def get_queryset(self):
        """
        Get queryset for Maps List.
        """
        return Map.objects.filter(is_active=True).filter(
            campaign=self.kwargs["campaign_pk"]
        )


class MapDetailView(CampaignIncluded, DetailView):
    """
    View for Maps Detail.
    """

    model = Map
    template_name = "maps/maps_detail.html"
    context_object_name = "map"
    pk_url_kwarg = "map_pk"


class MapCreateView(CampaignIncluded, SuccessMessageMixin, CreateView):
    """
    View for Map Create.
    """

    model = Map
    fields = ["name", "description", "image"]
    template_name = "maps/maps_form.html"
    success_message = _("Map successfully created")

    def get_success_url(self):
        """
        Override get_success_url method to redirect to Campaigns Detail.
        """
        return reverse(
            "campaigns:maps:detail",
            kwargs={"campaign_pk": self.campaign.pk, "pk": self.object.pk},
        )

    def form_valid(self, form):
        """
        Override form_valid method to set the active campaign.
        """
        form.instance.campaign = Campaign.objects.get(id=self.kwargs["campaign_pk"])
        return super().form_valid(form)


class MapUpdateView(CampaignIncluded, SuccessMessageMixin, UpdateView):
    """
    View for Campaigns Update.
    """

    model = Map
    fields = ["name", "description", "is_active", "image"]
    template_name = "maps/maps_form.html"
    context_object_name = "map"
    success_message = _("Map successfully updated")

    def get_success_url(self):
        """
        Override get_success_url method to redirect to Campaigns Detail.
        """
        return reverse("maps:detail", kwargs={"pk": self.object.pk})


class MapDeleteView(CampaignIncluded, SuccessMessageMixin, DeleteView):
    """
    View for Map Delete.
    """

    model = Map
    template_name = "confirm_delete.html"
    success_message = _("Map successfully deleted")

    def get_success_url(self):
        """
        Override get_success_url method to redirect to Campaigns List.
        """
        return reverse("campaigns:detail", kwargs={"pk": self.object.campaign.pk})


@dataclass()
class MapIncluded(LoginRequiredMixin):
    """Mixin that adds the Map to the context."""

    map: Map

    def setup(self, request, *args, **kwargs) -> None:
        """Overloaded to set the campaign."""
        super().setup(request, *args, **kwargs)
        self.map = get_object_or_404(Map, pk=kwargs["map_pk"])

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["map"] = self.map
        return context


class LocationCreateView(MapIncluded, SuccessMessageMixin, CreateView):
    """
    View for Location Create.
    """

    model = Location
    fields = ["name", "description", "image", "pixel_y", "pixel_x"]
    template_name = "locations/locations_form.html"
    success_message = _("Location successfully created")

    def get_success_url(self):
        """
        Override get_success_url method to redirect to Maps Detail.
        """
        return reverse(
            "campaigns:maps:detail",
            kwargs={
                "campaign_pk": self.object.map.campaign_pk,
                "map_pk": self.object.map.pk,
            },
        )

    def form_valid(self, form):
        """
        Override form_valid method to set the active map.
        """
        form.instance.map = Map.objects.get(id=self.kwargs["map_pk"])
        return super().form_valid(form)


class LocationUpdateView(MapIncluded, SuccessMessageMixin, UpdateView):
    """
    View for Campaigns Update.
    """

    model = Location
    fields = ["name", "description", "is_active", "image"]
    template_name = "locations/locations_form.html"
    context_object_name = "location"
    success_message = _("Location successfully updated")

    def get_success_url(self):
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


class LocationDeleteView(MapIncluded, SuccessMessageMixin, DeleteView):
    """
    View for Location Delete.
    """

    model = Location
    template_name = "confirm_delete.html"
    success_message = _("Location successfully deleted")

    def get_success_url(self):
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
