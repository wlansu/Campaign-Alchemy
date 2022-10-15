from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from model_utils.models import TimeStampedModel
from tinymce.models import HTMLField


class Map(TimeStampedModel):
    """
    Model for Maps.
    """

    name = models.CharField(max_length=255)
    description = HTMLField(blank=True)
    image = models.ImageField(upload_to="maps/")
    resolution_height = models.IntegerField(null=True)
    resolution_width = models.IntegerField(null=True)
    campaign = models.ForeignKey(
        "campaigns.Campaign", on_delete=models.CASCADE, related_name="maps"
    )
    vector_column = SearchVectorField(null=True)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Map: {self.name}>"

    def save(self, *args, **kwargs) -> None:
        """Set the resolutions on image save."""
        super().save(*args, **kwargs)
        if self.image and not all([self.resolution_height, self.resolution_width]):
            width, height = self.image._get_image_dimensions()
            self.resolution_width = width
            self.resolution_height = height
            self.save(update_fields=["resolution_height", "resolution_width"])

    class Meta:
        verbose_name = "Map"
        verbose_name_plural = "Maps"
        indexes = (GinIndex(fields=["vector_column"]), models.Index(fields=["name"]))
