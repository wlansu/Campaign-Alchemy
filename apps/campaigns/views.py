from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.forms import BaseForm
from django.http import HttpResponse
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
    pk_url_kwarg = "campaign_pk"


class CampaignsCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    View for Campaigns Create.
    """

    model = Campaign
    fields = ["name", "description"]
    template_name = "campaigns/campaigns_form.html"
    success_message = _("Campaign successfully created")

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """
        Override form_valid method to set user as DM.
        """
        # TODO: check type of form, it's likely not correct.
        form.instance.dm = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """
        Override get_success_url method to redirect to Campaigns Detail.
        """
        return reverse("campaigns:detail", kwargs={"campaign_pk": self.object.pk})


class CampaignsUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    View for Campaigns Update.
    """

    model = Campaign
    fields = ["name", "description", "is_active"]
    template_name = "campaigns/campaigns_form.html"
    context_object_name = "campaign"
    success_message = _("Campaign successfully updated")
    pk_url_kwarg = "campaign_pk"

    def get_success_url(self) -> str:
        """
        Override get_success_url method to redirect to Campaigns Detail.
        """
        return reverse("campaigns:detail", kwargs={"campaign_pk": self.object.pk})
