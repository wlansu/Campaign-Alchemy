from typing import Optional

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q, QuerySet
from django.forms import BaseForm
from django.http import Http404, HttpResponse
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


class CampaignListView(LoginRequiredMixin, ListView):
    """
    View for Campaigns List.
    """

    model = Campaign
    template_name = "campaigns/campaign_list.html"
    context_object_name = "campaigns"

    def get_queryset(self) -> QuerySet:
        return Campaign.objects.filter(
            Q(dm=self.request.user) | Q(characters__player=self.request.user)
        ).distinct()

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["campaigns/campaign_partial_list.html"]
        return [self.template_name]


class CampaignDetailView(LoginRequiredMixin, DetailView):
    """
    View for Campaigns Detail.
    """

    model = Campaign
    template_name = "campaigns/campaign_detail.html"
    context_object_name = "campaign"
    pk_url_kwarg = "campaign_pk"

    def get_object(
        self, queryset: Optional[QuerySet] = None
    ) -> Campaign | HttpResponse:
        campaign = super().get_object(queryset)
        if (
            self.request.user == campaign.dm
            or self.request.user.id
            in campaign.characters.values_list("player", flat=True)
        ):
            return campaign
        raise Http404

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["campaigns/campaign_partial_detail.html"]
        return [self.template_name]


class CampaignCreateView(LoginRequiredMixin, CreateView):
    """
    View for Campaigns Create.
    """

    model = Campaign
    fields = ["name", "description", "image"]
    template_name = "campaigns/campaign_form.html"

    def form_valid(self, form: BaseForm) -> HttpResponse:
        form.instance.dm = self.request.user
        self.object = form.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "campaignListChanged"})


class CampaignUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    View for Campaigns Update.
    """

    model = Campaign
    fields = ["name", "description", "image"]
    template_name = "campaigns/campaign_form.html"
    context_object_name = "campaign"
    pk_url_kwarg = "campaign_pk"

    def get_object(self, queryset: Optional[QuerySet] = None) -> Campaign:
        campaign = super().get_object(queryset)
        if self.request.user == campaign.dm:
            return campaign
        raise PermissionDenied()

    def form_valid(self, form: BaseForm) -> HttpResponse:
        self.object = form.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "campaignChanged"})


class CampaignDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    View for Campaign Delete.
    """

    model = Campaign
    template_name = "confirm_delete.html"
    success_message = _("Campaign successfully deleted")
    pk_url_kwarg = "campaign_pk"

    def get_object(self, queryset: Optional[QuerySet] = None) -> Campaign:
        campaign = super().get_object(queryset)
        if self.request.user == campaign.dm:
            return campaign
        raise PermissionDenied()

    def get_success_url(self) -> str:
        """
        Override get_success_url method to redirect to Campaigns List.
        """
        return reverse("campaigns:list")
