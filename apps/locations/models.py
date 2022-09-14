from pathlib import Path

from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel
from PIL import Image


class Location(TimeStampedModel):
    """
    Model for Location.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="locations/", null=True)
    thumbnail = models.ImageField(upload_to="locations/thumbnails/", null=True)
    longitude = models.FloatField(default=0)
    latitude = models.FloatField(default=0)
    map = models.ForeignKey(
        "maps.Map", on_delete=models.CASCADE, related_name="locations"
    )

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Location: {self.name}>"

    def create_thumbnail(self) -> None:
        """Create a thumbnail from the image the user uploaded to display on the map."""
        try:
            image = Image.open(self.image)
            image.thumbnail((100, 90))
            name = Path(self.image.name)
            # omit Path() if MEDIA_ROOT is already a Path object
            thumbnail_path = Path(settings.MEDIA_ROOT) / f"thumb_{name.stem}.png"
            self.thumbnail = thumbnail_path.name  # it should be relative path
            image.save(thumbnail_path, "PNG")  # if it doesn't like Path, str() it
        except IOError:
            pass

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        if self.image:
            self.create_thumbnail()

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
