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


class Location(TimeStampedModel):
    """
    Model for Location.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    pixel_x = models.IntegerField(default=0)
    pixel_y = models.IntegerField(default=0)
    resolution_height = models.IntegerField(default=0)
    resolution_width = models.IntegerField(default=0)
    map = models.ForeignKey(
        "maps.Map", on_delete=models.CASCADE, related_name="locations"
    )

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Location: {self.name}>"

    def get_pixel_x(self, width: int) -> int:
        """Return the pixel x coordinate for the location."""
        if width == self.resolution_width:
            return self.pixel_x
        else:
            return int((self.pixel_x / self.resolution_width) * width)

    def get_pixel_y(self, height: int) -> int:
        """Return the pixel y coordinate for the location."""
        if height == self.resolution_height:
            return self.pixel_y
        else:
            return int((self.pixel_y / self.resolution_height) * height)

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
