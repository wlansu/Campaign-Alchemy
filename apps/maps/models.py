from django.db import models
from model_utils.models import TimeStampedModel


class Map(TimeStampedModel):
    """
    Model for Maps.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="maps/")
    is_active = models.BooleanField(default=True)
    campaign = models.ForeignKey(
        "campaigns.Campaign", on_delete=models.CASCADE, related_name="maps"
    )

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Map: {self.name}>"

    class Meta:
        verbose_name = "Map"
        verbose_name_plural = "Maps"
