from django.urls import include, path

from apps.campaigns.views import (
    CampaignsCreateView,
    CampaignsDetailView,
    CampaignsListView,
    CampaignsUpdateView,
)

app_name = "campaigns"
urlpatterns = [
    path("", view=CampaignsListView.as_view(), name="list"),
    path("create/", view=CampaignsCreateView.as_view(), name="create"),
    path(
        "update/<int:campaign_pk>/", view=CampaignsUpdateView.as_view(), name="update"
    ),
    path("<int:campaign_pk>/", view=CampaignsDetailView.as_view(), name="detail"),
    path(
        "<int:campaign_pk>/delete/", view=CampaignsUpdateView.as_view(), name="delete"
    ),
    path("<int:campaign_pk>/maps/", include("apps.maps.urls", namespace="maps")),
]
