from django.contrib.auth.models import AbstractUser
from django.db.models import BooleanField, CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for Campaign Alchemy.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    can_be_dm = BooleanField(default=True)

    def get_absolute_url(self) -> str:
        """Get url for user's detail view."""
        return reverse("users:detail", kwargs={"username": self.username})

    def has_read_access_to_campaign(self, campaign_id: int) -> bool:
        """Determine whether a User has read access to a Campaign.

        If any of the User's Characters is in a Campaign then the User has access.
        """
        from apps.campaigns.models import Campaign

        campaign = Campaign.objects.get(id=campaign_id)

        if self.id == campaign.dm_id:
            return True

        player_characters = self.characters.values_list("player_id")
        campaign_characters = campaign.characters.values_list("player_id")
        return any(
            character_id in campaign_characters for character_id in player_characters
        )
