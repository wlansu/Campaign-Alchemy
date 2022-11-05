from crispy_forms.bootstrap import InlineCheckboxes
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit
from django.forms import ModelForm, ModelMultipleChoiceField
from django.forms.fields import FloatField
from django.forms.widgets import CheckboxSelectMultiple, HiddenInput

from apps.characters.models import Character
from apps.locations.models import Location


class LocationForm(ModelForm):
    """Form to create/update a Location.

    The longitude and latitude are set through javascript by registering the location the User clicked.
    """

    longitude = FloatField(widget=HiddenInput())
    latitude = FloatField(widget=HiddenInput())
    characters = ModelMultipleChoiceField(
        queryset=Character.objects.none(), widget=CheckboxSelectMultiple, required=False
    )

    class Meta:
        model = Location
        fields = ["name", "description", "image", "longitude", "latitude", "characters"]

    def __init__(self, *args, **kwargs) -> None:
        campaign_id = kwargs.pop("campaign_id", None)
        super().__init__(*args, **kwargs)
        if campaign_id:
            self.fields["characters"].queryset = Character.objects.filter(
                campaign=campaign_id
            ).order_by("name")
        self.helper = FormHelper(self)
        self.helper.form_id = "location-form"
        self.helper.form_class = "location-form mb-4"
        self.helper.form_method = "GET"
        self.helper.use_custom_control = True
        self.helper.label_class = "font-weight-bold"
        self.helper.add_input(Submit("submit", "Submit", css_class="float-end"))
        self.helper.layout = Layout(
            Field("name"),
            Field("description"),
            Field("image"),
            Field("longitude", type="hidden"),
            Field("latitude", type="hidden"),
            InlineCheckboxes("characters", css_class="character-checkboxes"),
        )
