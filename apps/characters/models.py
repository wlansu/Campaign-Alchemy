from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from model_utils.models import TimeStampedModel


class Character(TimeStampedModel):
    """A character created by a User.

    Can be an NPC if it is not assigned to a player.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="characters/", null=True)
    campaign = models.ForeignKey(
        "campaigns.Campaign",
        on_delete=models.SET_NULL,
        related_name="characters",
        null=True,
    )
    player = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, related_name="characters", null=True
    )
    is_npc = models.BooleanField(default=False)
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
        """Overloaded to set the player to None if is_npc is True."""
        super().save(*args, **kwargs)
        if self.is_npc and kwargs.get("update_fields", None) == ["player"]:
            self.player = None
            self.save(update_fields=["player"])

    def get_absolute_url(self) -> str:
        from django.urls import reverse

        return reverse("characters:detail", kwargs={"character_pk": self.pk})

    class Meta:
        verbose_name = "Character"
        verbose_name_plural = "Characters"
        indexes = (GinIndex(fields=["vector_column"]),)
