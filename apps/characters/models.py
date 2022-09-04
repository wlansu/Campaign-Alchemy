from django.db import models
from model_utils.models import TimeStampedModel


class Character(TimeStampedModel):
    """A character in a campaign."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="characters/", blank=True)
    is_active = models.BooleanField(default=True)
    campaign = models.ForeignKey(
        "campaigns.Campaign", on_delete=models.CASCADE, related_name="characters"
    )
    player = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="characters"
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Character: {self.name}>"

    class Meta:
        verbose_name = "Character"
        verbose_name_plural = "Characters"
