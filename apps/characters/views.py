from typing import Optional

from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.forms import BaseForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from apps.characters.forms import AddToCampaignForm
from apps.characters.models import Character
from apps.mixins import CanCreateMixin, create_required


@create_required
@require_http_methods(["GET"])
def characters_page(request: HttpRequest) -> HttpResponse:
    """Return the full characters list page.

    This should only return the player's own characters.
    """
    characters = Character.objects.filter(player=request.user)
    return render(
        request=request,
        template_name="characters/list.html",
        context={"characters": characters},
    )


@create_required
@require_http_methods(["GET"])
def characters_hx(request: HttpRequest, campaign_pk: int = None) -> HttpResponse:
    """HX-Request: return a partial template."""
    if campaign_pk:
        if not request.user.has_read_access_to_campaign(campaign_pk=campaign_pk):
            raise PermissionDenied
        characters = Character.objects.select_related("campaign").filter(
            campaign=campaign_pk
        )
    else:
        characters = Character.objects.filter(player=request.user)

    return render(
        request=request,
        template_name="characters/partial_list.html",
        context={"characters": characters},
    )


@create_required
@require_http_methods(["GET", "POST"])
def add_to_campaign(request: HttpRequest, character_pk: int = None) -> HttpResponse:
    """Add a Character to a Campaign."""
    if request.method == "POST":
        form = AddToCampaignForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            return HttpResponse(
                status=204, headers={"HX-Trigger": "characterListChanged"}
            )
    else:
        form = AddToCampaignForm()
        if character_pk:
            form.initial["character_pk"] = character_pk

    return render(
        request=request,
        template_name="characters/add_to_campaign_form.html",
        context={"form": form},
    )


@create_required
@require_http_methods(["GET"])
def remove_from_campaign(request: HttpRequest, character_pk: int) -> HttpResponse:
    character = get_object_or_404(Character, player=request.user, id=character_pk)
    character.campaign = None
    character.save()
    return HttpResponse(status=204, headers={"HX-Trigger": "characterListChanged"})


class CharacterDetailView(CanCreateMixin, DetailView):
    """
    View for Characters Detail.
    """

    model = Character
    template_name = "characters/character_detail.html"
    context_object_name = "character"
    pk_url_kwarg = "character_pk"

    def get_object(self, queryset: Optional[QuerySet] = None) -> Character:
        character = super().get_object(queryset)
        if (
            character.player == self.request.user
            or self.request.user.has_read_access_to_campaign(
                campaign_pk=character.campaign_id
            )
        ):
            return character
        raise PermissionDenied

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["characters/character_detail_partial.html"]
        return [self.template_name]


class CharacterCreateView(CanCreateMixin, CreateView):
    """Create a new Character."""

    model = Character
    fields = ["name", "description", "image", "is_npc"]
    template_name = "characters/character_form.html"

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """
        If a character is not an NPC then the player is the creator.
        """
        if form.data.get("is_npc") != "on":
            form.instance.player = self.request.user
        self.object = form.save()

        return HttpResponse(status=204, headers={"HX-Trigger": "characterListChanged"})


class CharacterUpdateView(CanCreateMixin, UpdateView):
    """
    View for Characters Update.
    """

    model = Character
    fields = ["name", "description", "image", "is_npc"]
    template_name = "characters/character_form.html"
    context_object_name = "character"
    pk_url_kwarg = "character_pk"

    def get_object(self, queryset: Optional[QuerySet] = None) -> Character:
        character = super().get_object(queryset)
        if character.player == self.request.user:
            return character
        raise PermissionDenied

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """Set character as NPC or Player."""
        if form.data.get("is_npc") != "on":
            form.instance.player = self.request.user
        else:
            form.instance.player = None
        self.object = form.save()

        return HttpResponse(status=204, headers={"HX-Trigger": "characterChanged"})


class CharacterDeleteView(CanCreateMixin, DeleteView):
    """
    View for Character Delete.
    """

    model = Character
    template_name = "confirm_delete.html"
    pk_url_kwarg = "character_pk"

    def get_object(self, queryset: Optional[QuerySet] = None) -> Character:
        character = super().get_object(queryset)
        if character.player == self.request.user:
            return character
        raise PermissionDenied

    def get_success_url(self) -> str:
        """
        Override get_success_url method to redirect to Characters List.
        """
        return reverse("characters:list")
