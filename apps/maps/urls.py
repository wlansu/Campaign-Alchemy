from django.urls import include, path

from apps.maps.views import (
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
        "<int:map_pk>/locations/", include("apps.locations.urls", namespace="locations")
    ),
]
