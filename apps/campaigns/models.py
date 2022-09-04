from django.db import models
from model_utils.models import TimeStampedModel


class Campaign(TimeStampedModel):
    """
    Model for Campaigns.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="campaigns/", blank=True)
    is_active = models.BooleanField(default=True)
    dm = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="dm_in_campaigns",
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Campaign: {self.name}>"

    class Meta:
        verbose_name = "Campaign"
        verbose_name_plural = "Campaigns"
