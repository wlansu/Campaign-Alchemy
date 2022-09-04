from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
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
from apps.maps.models import Map
from apps.utils.decorators import campaign_not_set


class MapListView(LoginRequiredMixin, ListView):
    """
    View for Maps List.
    """

    model = Map
    template_name = "maps/maps_list.html"
    context_object_name = "maps"

    @campaign_not_set
    def get_queryset(self):
        """
        Get queryset for Maps List.
        """
        return Map.objects.filter(is_active=True).filter(
            campaign=self.request.session["campaign_id"]
        )


class MapDetailView(LoginRequiredMixin, DetailView):
    """
    View for Maps Detail.
    """

    model = Map
    template_name = "maps/maps_detail.html"
    context_object_name = "map"


class MapCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
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
        return reverse("maps:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        """
        Override form_valid method to set the active campaign.
        """
        form.instance.campaign = Campaign.objects.get(
            id=self.request.session["campaign_id"]
        )
        return super().form_valid(form)


class MapUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
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


class MapDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
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
