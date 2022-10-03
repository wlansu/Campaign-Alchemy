from django.urls import path

from apps.characters.views import (
    CharacterCreateView,
    CharacterDeleteView,
    CharacterDetailView,
    CharacterUpdateView,
    add_to_campaign,
    characters_hx,
    characters_page,
    remove_from_campaign,
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
    path("add/", view=add_to_campaign, name="add"),
    path("add/<int:character_pk>/", view=add_to_campaign, name="add"),
    path("remove/<int:character_pk>/", view=remove_from_campaign, name="remove"),
]
