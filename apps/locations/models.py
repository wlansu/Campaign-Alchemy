from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from model_utils.models import TimeStampedModel
from tinymce.models import HTMLField


class Location(TimeStampedModel):

    name = models.CharField(max_length=255)
    description = HTMLField(blank=True)
    longitude = models.FloatField(default=0)
    latitude = models.FloatField(default=0)
    map = models.ForeignKey(
        "maps.Map", on_delete=models.CASCADE, related_name="locations"
    )
    image = models.ImageField(upload_to="locations/", blank=True, null=True)
    vector_column = SearchVectorField(null=True)
    hidden = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Location: {self.name}>"

    def get_absolute_url(self) -> str:
        """There is no traditional detail view for Location.

        Redirect to the Map detail page with the active location set to this Location.
        """
        from django.urls import reverse

        return (
            reverse(
                "campaigns:maps:detail",
                kwargs={
                    "campaign_pk": self.map.campaign_id,
                    "map_pk": self.map_id,
                },
            )
            + f"?active_location={self.pk}"
        )

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        indexes = (models.Index(fields=["name"]), GinIndex(fields=["vector_column"]))
