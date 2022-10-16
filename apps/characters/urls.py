from django.urls import path

from apps.characters.views import (
    CharacterCreateView,
    CharacterDeleteView,
    CharacterDetailView,
    CharacterListView,
    CharacterUpdateView,
    NPCListView,
    add_to_campaign,
    remove_from_campaign,
)

app_name = "characters"
urlpatterns = [
    path("", view=CharacterListView.as_view(), name="list"),
    path("npcs/", view=NPCListView.as_view(), name="npcs"),
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
