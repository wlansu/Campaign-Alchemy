import uuid

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from model_utils.models import TimeStampedModel
from tinymce.models import HTMLField


class Campaign(TimeStampedModel):

    name = models.CharField(max_length=255)
    description = HTMLField(blank=True)
    image = models.ImageField(upload_to="campaigns/", blank=True)
    dm = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="dm_in_campaigns",
    )
    invite_code = models.UUIDField(
        unique=True, null=True
    )  # Used to add player's to a Campaign.
    vector_column = SearchVectorField(null=True)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Campaign: {self.name}>"

    def get_absolute_url(self) -> str:
        from django.urls import reverse

        return reverse("campaigns:detail", kwargs={"campaign_pk": self.pk})

    @staticmethod
    def _generate_invite_code() -> uuid.UUID:
        return uuid.uuid4()

    class Meta:
        verbose_name = "Campaign"
        verbose_name_plural = "Campaigns"
        indexes = (GinIndex(fields=["vector_column"]), models.Index(fields=["name"]))

    def save(self, *args, **kwargs) -> None:
        """Set the invite code if it doesn't exist yet."""
        if not self.pk or not self.invite_code:
            self.invite_code = self._generate_invite_code()
        super().save(*args, **kwargs)
