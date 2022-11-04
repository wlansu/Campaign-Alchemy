from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.core.cache import cache
from django.db import models
from model_utils.models import TimeStampedModel
from tinymce.models import HTMLField


class Character(TimeStampedModel):

    name = models.CharField(max_length=255)
    description = HTMLField(blank=True)
    image = models.ImageField(upload_to="characters/", null=True, blank=True)
    campaign = models.ForeignKey(
        "campaigns.Campaign",
        on_delete=models.SET_NULL,
        related_name="characters",
        null=True,
    )
    player = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="player_characters",
        null=True,
    )
    creator = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="creator_characters",
        null=True,
    )  # The creator is needed to let the User view NPC's
    is_npc = models.BooleanField(
        default=False
    )  # If no Player was assigned the Character is an NPC
    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.SET_NULL,
        related_name="characters",
        null=True,
    )
    vector_column = SearchVectorField(null=True)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Character: {self.name}>"

    def save(self, *args, **kwargs) -> None:
        """Overloaded to set the player to None if is_npc is True.

        If a Character joins a Campaign; invalidate the user_has_read_access_to_campaign cache
            so the value is recalculated and the user has access to the Campaign.
        """
        not_in_campaign = False
        if not self.campaign_id:
            not_in_campaign = True
        super().save(*args, **kwargs)
        if not_in_campaign and self.campaign_id:
            cache.delete(f"{self.player_id}.user_has_read_access_to_campaign")
        if self.is_npc and kwargs.get("update_fields", None) == ["player"]:
            self.player = None
            self.save(update_fields=["player"])
        if not self.player and not self.is_npc:
            self.is_npc = True
            self.save(update_fields=["is_npc"])

    def get_absolute_url(self) -> str:
        from django.urls import reverse

        return reverse("characters:detail", kwargs={"character_pk": self.pk})

    class Meta:
        verbose_name = "Character"
        verbose_name_plural = "Characters"
        indexes = (GinIndex(fields=["vector_column"]), models.Index(fields=["name"]))
