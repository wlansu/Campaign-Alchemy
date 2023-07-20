from typing import Optional

from django.core.exceptions import PermissionDenied
from django.db.models import Q, QuerySet
from django.forms import BaseForm
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.campaigns.models import Campaign
from apps.mixins import CanCreateCampaignMixin, CanCreateMixin


class CampaignListView(CanCreateMixin, ListView):
    """List of Campaigns the User has access to."""

    model = Campaign
    template_name = "campaigns/campaign_list.html"
    context_object_name = "campaigns"

    def get_queryset(self) -> QuerySet:
        """Access criteria:
        - The User is the DM for the Campaign
        - The User has a Character in the Campaign
        """
        return Campaign.objects.filter(
            Q(dm=self.request.user) | Q(characters__player=self.request.user)
        ).distinct()

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["campaigns/_partial_campaign_list.html"]
        return [self.template_name]


class CampaignDetailView(CanCreateMixin, DetailView):
    model = Campaign
    template_name = "campaigns/campaign_detail.html"
    context_object_name = "campaign"
    pk_url_kwarg = "campaign_pk"

    def get_object(
        self, queryset: Optional[QuerySet] = None
    ) -> Campaign | HttpResponse:
        """Access criteria:
        - The User is the DM for the Campaign
        - The User has a Character in the Campaign
        """
        campaign = super().get_object(queryset)
        if (
            self.request.user == campaign.dm
            or self.request.user.id
            in campaign.characters.values_list("player", flat=True)
        ):
            return campaign
        raise PermissionDenied

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["campaigns/_partial_campaign_detail.html"]
        return [self.template_name]


class CampaignCreateView(CanCreateCampaignMixin, CreateView):
    """Create a new Campaign.

    Any User with the `can_create` boolean can create a new Campaign
        and becomes its DM by doing so.
    """

    model = Campaign
    fields = ["name", "description", "image"]
    template_name = "campaigns/campaign_form.html"

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """Set the creator as DM.

        Return a No-Content and set the HTMX trigger so the modal will be closed and the campaign list refreshed.
        """
        form.instance.dm = self.request.user
        self.object = form.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "campaignListChanged"})


class CampaignUpdateView(CanCreateMixin, UpdateView):
    model = Campaign
    fields = ["name", "description", "image"]
    template_name = "campaigns/campaign_form.html"
    context_object_name = "campaign"
    pk_url_kwarg = "campaign_pk"

    def get_object(self, queryset: Optional[QuerySet] = None) -> Campaign:
        """Access criteria:
        - Only a Campaign's DM can perform updates
        """
        campaign = super().get_object(queryset)
        if self.request.user == campaign.dm:
            return campaign
        raise PermissionDenied

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """Return a No-Content and set the HTMX trigger so the modal will be closed
        and the campaign detail page refreshed.
        """
        self.object = form.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "campaignChanged"})


class CampaignDeleteView(CanCreateMixin, DeleteView):
    model = Campaign
    template_name = "confirm_delete.html"
    pk_url_kwarg = "campaign_pk"

    def get_object(self, queryset: Optional[QuerySet] = None) -> Campaign:
        """Acceptance criteria:
        - Only the DM can delete a Campaign
        """
        campaign = super().get_object(queryset)
        if self.request.user == campaign.dm:
            return campaign
        raise PermissionDenied

    def get_success_url(self) -> str:
        return reverse("campaigns:list")
