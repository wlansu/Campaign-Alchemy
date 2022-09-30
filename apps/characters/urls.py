from django.urls import path

from apps.characters.views import (
    CharacterCreateView,
    CharacterDeleteView,
    CharacterDetailView,
    CharacterUpdateView,
    characters_hx,
    characters_page,
)

app_name = "characters"
urlpatterns = [
    path("", view=characters_page, name="list"),
    path("hx-list/", view=characters_hx, name="hx-list"),
    path("create/", view=CharacterCreateView.as_view(), name="create"),
    path(
        "detail/<int:character_pk>/", view=CharacterDetailView.as_view(), name="detail"
    ),
    path(
        "update/<int:character_pk>/", view=CharacterUpdateView.as_view(), name="update"
    ),
    path(
        "<int:character_pk>/delete/", view=CharacterDeleteView.as_view(), name="delete"
    ),
]
