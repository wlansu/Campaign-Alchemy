from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from django.core.mail import send_mail
from django.db import models
from django.db.models import BooleanField, CharField
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
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
    can_create = BooleanField(default=False)

    @cached_property
    def is_dm(self) -> bool:
        """True if the User is a DM in any campaign."""
        return self.dm_in_campaigns.count() > 0

    def get_absolute_url(self) -> str:
        """Get url for user's detail view."""
        return reverse("users:detail", kwargs={"username": self.username})

    def has_read_access_to_campaign(self, campaign_pk: int) -> bool:
        """Determine whether a User has read access to a Campaign.

        If any of the User's Characters is in a Campaign then the User has access.
        """
        has_read_access = cache.get(f"{self.id}.user_has_read_access_to_campaign")
        if not has_read_access:
            from apps.campaigns.models import Campaign

            campaign = get_object_or_404(Campaign, id=campaign_pk)

            if self.id == campaign.dm_id:
                return True

            player_characters = self.player_characters.values_list("player_id")
            creator_characters = self.creator_characters.values_list("player_id")
            all_characters = player_characters.union(creator_characters)
            campaign_characters = campaign.characters.values_list("player_id")
            has_read_access = any(
                character_id in campaign_characters for character_id in all_characters
            )
            cache.set(
                f"{self.id}.user_has_read_access_to_campaign", has_read_access, 600
            )
        return has_read_access

    def save(self, *args, **kwargs) -> None:
        """Overloaded in order to send the Admin an email when a new User is created."""
        send_email = False
        if not self.pk:
            send_email = True

        super().save(*args, **kwargs)
        if send_email:
            send_mail(
                "New user registered",
                f"{self.username} signed up.",
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMINS[0][1]],
                fail_silently=False,
            )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = (models.Index(fields=["name", "can_create"]),)
