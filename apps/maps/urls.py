from django.urls import path

from apps.maps.views import (
    LocationCreateView,
    LocationDeleteView,
    LocationUpdateView,
    MapCreateView,
    MapDeleteView,
    MapDetailView,
    MapListView,
    MapUpdateView,
)

app_name = "maps"
urlpatterns = [
    path("", view=MapListView.as_view(), name="list"),
    path("create/", view=MapCreateView.as_view(), name="create"),
    path("<int:map_pk>/update/", view=MapUpdateView.as_view(), name="update"),
    path("<int:map_pk>/", view=MapDetailView.as_view(), name="detail"),
    path("<int:map_pk>/delete/", view=MapDeleteView.as_view(), name="delete"),
    path(
        "<int:map_pk>/create_location/",
        LocationCreateView.as_view(),
        name="create_location",
    ),
    path(
        "<int:map_pk><int:location_pk>/update/",
        LocationUpdateView.as_view(),
        name="update_location",
    ),
    path(
        "<int:map_pk><int:location_pk>/delete",
        LocationDeleteView.as_view(),
        name="delete_location",
    ),
]
