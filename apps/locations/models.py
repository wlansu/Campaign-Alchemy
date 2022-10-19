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

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Location: {self.name}>"

    def get_absolute_url(self) -> str:
        from django.urls import reverse

        return reverse(
            "campaigns:maps:locations:detail",
            kwargs={
                "campaign_pk": self.map.campaign_id,
                "map_pk": self.map_id,
                "location_pk": self.pk,
            },
        )

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        indexes = (models.Index(fields=["name"]),)
        ordering = ("-created",)
