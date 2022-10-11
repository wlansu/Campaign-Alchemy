from uuid import UUID

from django import forms
from django.core.exceptions import PermissionDenied, ValidationError

from apps.campaigns.models import Campaign
from apps.characters.models import Character


class AddToCampaignForm(forms.Form):
    invite_code = forms.UUIDField(required=True)
    character_pk = forms.IntegerField(widget=forms.HiddenInput(), required=True)

    def __init__(self, *args, **kwargs):
        """Set the request so the user can be accessed."""
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean_invite_code(self) -> UUID:
        """Check whether the invite code is for an existing Campaign."""
        data = self.cleaned_data["invite_code"]
        campaign_exists = Campaign.objects.filter(invite_code=data).exists()
        if not campaign_exists:
            raise ValidationError("Invite code is not valid.")
        return data

    def clean_character_pk(self) -> int:
        """Check that the Character exists."""
        data = self.cleaned_data["character_pk"]
        character_exists = Character.objects.filter(
            id=data, player=self.request.user
        ).exists()
        if not character_exists:
            raise PermissionDenied
        return data

    def save(self) -> None:
        """Add the Character to the Campaign."""
        campaign = Campaign.objects.get(invite_code=self.cleaned_data["invite_code"])
        character = Character.objects.get(id=self.cleaned_data["character_pk"])
        campaign.characters.add(character)
