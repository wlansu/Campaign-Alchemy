from django.db import models
from model_utils.models import TimeStampedModel


class Character(TimeStampedModel):
    """A character created by a User.

    Can be an NPC if it is not assigned to a player.

    A Character always needs to have a creator, if a User deletes their account
        their creator_characters will also be deleted.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="characters/", null=True)
    is_active = models.BooleanField(default=True)
    creator = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="creator_characters"
    )
    campaign = models.ForeignKey(
        "campaigns.Campaign",
        on_delete=models.SET_NULL,
        related_name="characters",
        null=True,
    )
    player = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, related_name="characters", null=True
    )
    location = models.ForeignKey(
        "characters.Character",
        on_delete=models.SET_NULL,
        related_name="characters",
        null=True,
    )

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Character: {self.name}>"

    def is_npc(self) -> bool:
        """Return whether the character is an NPC or not.

        A character is an NPC if no player is assigned.
        """
        return hasattr(self, "player")

    class Meta:
        verbose_name = "Character"
        verbose_name_plural = "Characters"
