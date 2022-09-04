from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.campaigns.models import Campaign


class CampaignsListView(LoginRequiredMixin, ListView):
    """
    View for Campaigns List.
    """

    model = Campaign
    template_name = "campaigns/campaigns_list.html"
    context_object_name = "campaigns"

    def get_queryset(self):
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

    def get(self, request, *args, **kwargs):
        """
        Override get method to set the active campaign.
        """
        self.request.session["campaign_id"] = self.get_object().id
        return super().get(request, *args, **kwargs)


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

    def get_success_url(self):
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

    def get_success_url(self):
        """
        Override get_success_url method to redirect to Campaigns Detail.
        """
        return reverse("campaigns:detail", kwargs={"pk": self.object.pk})
