from django.forms import ModelForm
from django.forms.fields import FloatField
from django.forms.widgets import HiddenInput

from apps.locations.models import Location


class LocationForm(ModelForm):
    """Form to create/update a Location."""

    longitude = FloatField(widget=HiddenInput())
    latitude = FloatField(widget=HiddenInput())

    class Meta:
        model = Location
        fields = ["name", "description", "longitude", "latitude"]
