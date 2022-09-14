from django.forms import ModelForm

from apps.locations.models import Location


class LocationForm(ModelForm):
    """Form to create/update a Location."""

    class Meta:
        model = Location
        fields = ["name", "description", "longitude", "latitude"]
