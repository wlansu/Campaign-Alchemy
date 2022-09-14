from django.urls import path

from apps.locations.views import (
    LocationDeleteView,
    LocationUpdateView,
    add_location,
    location_list,
)

app_name = "locations"
urlpatterns = [
    path("create/", view=add_location, name="create"),
    path("list/", view=location_list, name="list"),
    path("<int:location_pk>/update/", view=LocationUpdateView.as_view(), name="update"),
    # path("<int:map_pk>/", view=LocationDetailView.as_view(), name="detail"),
    path("<int:location_pk>/delete/", view=LocationDeleteView.as_view(), name="delete"),
]
