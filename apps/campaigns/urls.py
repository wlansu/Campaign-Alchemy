from django.urls import include, path

from apps.campaigns.views import (
    CampaignCreateView,
    CampaignDeleteView,
    CampaignDetailView,
    CampaignListView,
    CampaignUpdateView,
)

app_name = "campaigns"
urlpatterns = [
    path("", view=CampaignListView.as_view(), name="list"),
    path("create/", view=CampaignCreateView.as_view(), name="create"),
    path("update/<int:campaign_pk>/", view=CampaignUpdateView.as_view(), name="update"),
    path("<int:campaign_pk>/", view=CampaignDetailView.as_view(), name="detail"),
    path("<int:campaign_pk>/delete/", view=CampaignDeleteView.as_view(), name="delete"),
    path("<int:campaign_pk>/maps/", include("apps.maps.urls", namespace="maps")),
]
