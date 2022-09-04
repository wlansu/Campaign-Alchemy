from django.urls import path

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
    path("update/<int:pk>/", view=MapUpdateView.as_view(), name="update"),
    path("<int:pk>/", view=MapDetailView.as_view(), name="detail"),
    path("<int:pk>/delete/", view=MapDeleteView.as_view(), name="delete"),
]
