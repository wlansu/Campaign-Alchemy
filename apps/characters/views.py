from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q, QuerySet
from django.forms import BaseForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

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


def characters_hx(request: HttpRequest) -> HttpResponse:
    """HX-Request: return a partial template."""
    query = request.GET.get("search", None)
    characters = _get_characters(request)
    if query:
        characters = characters.filter(name__icontains=query)
    return render(
        request=request,
        template_name="characters/partial_list.html",
        context={"characters": characters},
    )


class CharacterDetailView(LoginRequiredMixin, DetailView):
    """
    View for Characters Detail.
    """

    model = Character
    template_name = "characters/character_detail.html"
    context_object_name = "character"
    pk_url_kwarg = "character_pk"


class CharacterCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Create a new Character."""

    model = Character
    fields = ["name", "description", "image", "is_npc"]
    template_name = "characters/character_form.html"
    success_message = "Character successfully created"

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """
        Override form_valid method to set user as creator and is_active to True.
        """
        form.instance.creator = self.request.user
        form.instance.is_active = True
        if form.data.get("is_npc") != "on":
            form.instance.player = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """
        Override get_success_url method to redirect to Characters Detail.
        """
        return reverse("characters:detail", kwargs={"character_pk": self.object.pk})


class CharacterUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    View for Characters Update.
    """

    model = Character
    fields = ["name", "description", "image", "is_npc", "is_active"]
    template_name = "characters/character_form.html"
    context_object_name = "character"
    success_message = "Character successfully updated"
    pk_url_kwarg = "character_pk"

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """
        Override form_valid method set user as player if is_npc is false and vice versa.
        """
        if form.data.get("is_npc") != "on":
            form.instance.player = self.request.user
        else:
            form.instance.player = None
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """
        Override get_success_url method to redirect to Characters Detail.
        """
        return reverse("characters:detail", kwargs={"character_pk": self.object.pk})


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
