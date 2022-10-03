from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q, QuerySet
from django.forms import BaseForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from apps.characters.forms import AddToCampaignForm
from apps.characters.models import Character


def _get_characters(request: HttpRequest) -> QuerySet:
    """Return a QuerySet of characters filtered by creator and user."""
    return Character.objects.filter(Q(creator=request.user) | Q(player=request.user))


def characters_page(request: HttpRequest) -> HttpResponse:
    """Return the full characters list page."""
    characters = _get_characters(request)
    return render(
        request=request,
        template_name="characters/list.html",
        context={"characters": characters},
    )


def characters_hx(request: HttpRequest, campaign_pk: int = None) -> HttpResponse:
    """HX-Request: return a partial template."""
    query = request.GET.get("search", None)
    characters = _get_characters(request)
    if campaign_pk:
        characters = characters.filter(campaign=campaign_pk)
    if query:
        characters = characters.filter(name__icontains=query)
    return render(
        request=request,
        template_name="characters/partial_list.html",
        context={"characters": characters},
    )


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


def remove_from_campaign(request: HttpRequest, character_pk: int) -> HttpResponse:
    character = get_object_or_404(Character, id=character_pk)
    if request.user == character.player:
        character.campaign = None
        character.save()
    return HttpResponse(status=204, headers={"HX-Trigger": "characterChanged"})


class CharacterDetailView(LoginRequiredMixin, DetailView):
    """
    View for Characters Detail.
    """

    model = Character
    template_name = "characters/character_detail.html"
    context_object_name = "character"
    pk_url_kwarg = "character_pk"

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["characters/character_detail_partial.html"]
        return [self.template_name]


class CharacterCreateView(LoginRequiredMixin, CreateView):
    """Create a new Character."""

    model = Character
    fields = ["name", "description", "image", "is_npc"]
    template_name = "characters/character_form.html"
    success_message = "Character successfully created"

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """
        The user that creates a character is its owner.
        If a character is not an NPC then the player is the creator.
        """
        form.instance.creator = self.request.user
        if form.data.get("is_npc") != "on":
            form.instance.player = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """
        Override get_success_url method to redirect to Characters Detail.
        """
        return reverse("characters:detail", kwargs={"character_pk": self.object.pk})


class CharacterUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for Characters Update.
    """

    model = Character
    fields = ["name", "description", "image", "is_npc", "is_active"]
    template_name = "characters/character_form.html"
    context_object_name = "character"
    pk_url_kwarg = "character_pk"

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """Set character as NPC or Player."""
        if form.data.get("is_npc") != "on":
            form.instance.player = self.request.user
        else:
            form.instance.player = None
        self.object = form.save()

        return HttpResponse(status=204, headers={"HX-Trigger": "characterChanged"})


class CharacterDeleteView(SuccessMessageMixin, DeleteView):
    """
    View for Character Delete.
    """

    model = Character
    template_name = "confirm_delete.html"
    success_message = "Character successfully deleted"
    pk_url_kwarg = "character_pk"

    def get_success_url(self) -> str:
        """
        Override get_success_url method to redirect to Characters List.
        """
        return reverse("characters:list")
