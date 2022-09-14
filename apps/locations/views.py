from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import HiddenInput
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DeleteView, UpdateView

from apps.locations.forms import LocationForm
from apps.locations.models import Location
from apps.maps.models import Map


class MapIncluded(LoginRequiredMixin):
    """Mixin that adds the Map to the context."""

    def setup(self, request, *args, **kwargs) -> None:
        """Overloaded to set the campaign."""
        super().setup(request, *args, **kwargs)
        self.map = get_object_or_404(Map, pk=kwargs["map_pk"])

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["map"] = self.map
        return context


class LocationCreateView(MapIncluded, SuccessMessageMixin, CreateView):
    """
    View for Location Create.
    """

    model = Location
    fields = ["name", "description", "image", "latitude", "longitude"]
    template_name = "locations/locations_form.html"
    success_message = _("Location successfully created")

    def get_success_url(self) -> str:
        """
        Override get_success_url method to redirect to Maps Detail.
        """
        return reverse(
            "campaigns:maps:detail",
            kwargs={
                "campaign_pk": self.object.map.campaign_pk,
                "map_pk": self.object.map.pk,
            },
        )

    def form_valid(self, form) -> HttpResponse:
        """
        Override form_valid method to set the active map.
        """
        form.instance.map = Map.objects.get(id=self.kwargs["map_pk"])
        return super().form_valid(form)


@login_required
@require_http_methods(["GET", "POST"])
def add_location(request: HttpRequest, campaign_pk: int, map_pk: int) -> HttpResponse:
    if request.method == "POST":
        form = LocationForm(request.POST, files=request.FILES)
        form.instance.map = Map.objects.get(id=map_pk)
        if form.is_valid():
            form.save()
            return redirect(
                reverse(
                    "campaigns:maps:detail",
                    kwargs={
                        "campaign_pk": campaign_pk,
                        "map_pk": map_pk,
                    },
                )
            )
    else:
        form = LocationForm()
        form.fields["longitude"].widget = HiddenInput()
        form.fields["latitude"].widget = HiddenInput()
        return render(
            request,
            "locations/locations_form.html",
            {"form": form, "campaign_pk": campaign_pk, "map_pk": map_pk},
        )


@login_required
@require_http_methods(["GET"])
def location_list(request: HttpRequest, campaign_pk: int, map_pk: int) -> HttpResponse:
    return render(
        request,
        "locations/locations_list.html",
        {
            "locations": Location.objects.filter(map=map_pk),
        },
    )


class LocationUpdateView(MapIncluded, SuccessMessageMixin, UpdateView):
    """
    View for Campaigns Update.
    """

    model = Location
    form_class = LocationForm
    template_name = "locations/locations_form.html"
    context_object_name = "location"
    success_message = _("Location successfully updated")
    pk_url_kwarg = "location_pk"

    def get_success_url(self) -> str:
        """
        Override get_success_url method to redirect to Map Detail.
        """
        return reverse(
            "campaigns:maps:detail",
            kwargs={
                "campaign_pk": self.object.map.campaign_pk,
                "map_pk": self.object.map.pk,
            },
        )

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["campaign_pk"] = self.map.campaign_id
        context["map_pk"] = self.map.id
        return context

    def get_form(self, form_class=None) -> LocationForm:
        form = super().get_form(form_class)
        form.fields["longitude"].widget = HiddenInput()
        form.fields["latitude"].widget = HiddenInput()
        return form


class LocationDeleteView(MapIncluded, SuccessMessageMixin, DeleteView):
    """
    View for Location Delete.
    """

    model = Location
    template_name = "confirm_delete.html"
    success_message = _("Location successfully deleted")
    pk_url_kwarg = "location_pk"

    def get_success_url(self) -> str:
        """
        Override get_success_url method to redirect to Map Detail.
        """
        return reverse(
            "campaigns:maps:detail",
            kwargs={
                "campaign_pk": self.object.map.campaign_pk,
                "map_pk": self.object.map.pk,
            },
        )
