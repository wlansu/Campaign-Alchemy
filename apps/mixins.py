from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, QuerySet

from apps.campaigns.models import Campaign
from apps.characters.models import Character


class CampaignPermissionRequiredMixin(LoginRequiredMixin):
    def get_queryset(self) -> QuerySet:
        return Campaign.objects.filter(
            Q(dm=self.request.user) | Q(characters__player=self.request.user)
        ).distinct()


class CharacterPermissionRequiredMixin(LoginRequiredMixin):
    def get_queryset(self) -> QuerySet:
        return Character.objects.filter(
            Q(creator=self.request.user) | Q(player=self.request.user)
        ).distinct()
