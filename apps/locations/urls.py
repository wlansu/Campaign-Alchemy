from django.urls import path

from apps.locations.views import (
    LocationCreateView,
    LocationDeleteView,
    LocationDetailView,
    LocationListView,
    LocationUpdateView,
    sort_locations,
)

app_name = "locations"
urlpatterns = [
    path("create/", view=LocationCreateView.as_view(), name="create"),
    path("list/", view=LocationListView.as_view(), name="list"),
    path("sort/", view=sort_locations, name="sort"),
    path("<int:location_pk>/update/", view=LocationUpdateView.as_view(), name="update"),
    path("<int:location_pk>/", view=LocationDetailView.as_view(), name="detail"),
    path("<int:location_pk>/delete/", view=LocationDeleteView.as_view(), name="delete"),
]
