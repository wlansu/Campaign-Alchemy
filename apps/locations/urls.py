from django.urls import path

from apps.locations.views import (
    LocationCreateView,
    LocationDeleteView,
    LocationListView,
    LocationUpdateView,
)

app_name = "locations"
urlpatterns = [
    path("create/", view=LocationCreateView.as_view(), name="create"),
    path("list/", view=LocationListView.as_view(), name="list"),
    path("<int:location_pk>/update/", view=LocationUpdateView.as_view(), name="update"),
    # path("<int:map_pk>/", view=LocationDetailView.as_view(), name="detail"),
    path("<int:location_pk>/delete/", view=LocationDeleteView.as_view(), name="delete"),
]
