from django.forms import ModelForm
from django.forms.fields import FloatField
from django.forms.widgets import HiddenInput

from apps.locations.models import Location


class LocationForm(ModelForm):
    """Form to create/update a Location.

    The longitude and latitude are set through javascript by registering the location the User clicked.
    """

    longitude = FloatField(widget=HiddenInput())
    latitude = FloatField(widget=HiddenInput())

    class Meta:
        model = Location
        fields = ["name", "description", "image", "longitude", "latitude"]


class DMLocationForm(LocationForm):
    class Meta(LocationForm.Meta):
        fields = [
            "name",
            "hidden",
            "description",
            "image",
            "longitude",
            "latitude",
        ]
