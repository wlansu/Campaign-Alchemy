from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.campaigns.models import Campaign


class CampaignIncluded(LoginRequiredMixin):
    """Mixin that adds the campaign to the context."""

    def setup(self, request, *args, **kwargs) -> None:
        """Overloaded to set the campaign."""
        super().setup(request, *args, **kwargs)
        self.campaign = get_object_or_404(Campaign, pk=self.kwargs["campaign_pk"])

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.campaign
        return context


class CampaignsListView(LoginRequiredMixin, ListView):
    """
    View for Campaigns List.
    """

    model = Campaign
    template_name = "campaigns/campaigns_list.html"
    context_object_name = "campaigns"

    def get_queryset(self) -> QuerySet:
        """
        Get queryset for Campaigns List.
        """
        return Campaign.objects.filter(is_active=True)


class CampaignsDetailView(LoginRequiredMixin, DetailView):
    """
    View for Campaigns Detail.
    """

    model = Campaign
    template_name = "campaigns/campaigns_detail.html"
    context_object_name = "campaign"


class CampaignsCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    View for Campaigns Create.
    """

    model = Campaign
    fields = ["name", "description"]
    template_name = "campaigns/campaigns_form.html"
    success_message = _("Campaign successfully created")

    def form_valid(self, form):
        """
        Override form_valid method to set user as DM.
        """
        form.instance.dm = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """
        Override get_success_url method to redirect to Campaigns Detail.
        """
        return reverse("campaigns:detail", kwargs={"pk": self.object.pk})


class CampaignsUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    View for Campaigns Update.
    """

    model = Campaign
    fields = ["name", "description", "is_active"]
    template_name = "campaigns/campaigns_form.html"
    context_object_name = "campaign"
    success_message = _("Campaign successfully updated")

    def get_success_url(self) -> str:
        """
        Override get_success_url method to redirect to Campaigns Detail.
        """
        return reverse("campaigns:detail", kwargs={"pk": self.object.pk})
