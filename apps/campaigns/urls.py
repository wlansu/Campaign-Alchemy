from django.urls import path

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
    path("update/<int:pk>/", view=CampaignsUpdateView.as_view(), name="update"),
    path("<int:pk>/", view=CampaignsDetailView.as_view(), name="detail"),
    path("<int:pk>/delete/", view=CampaignsUpdateView.as_view(), name="delete"),
]
