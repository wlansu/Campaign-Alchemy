from contextlib import nullcontext as does_not_raise
from typing import Callable

import pytest
from django.core.exceptions import PermissionDenied
from django.test.client import Client, RequestFactory
from django.urls import reverse

from apps.campaigns.models import Campaign
from apps.campaigns.views import (
    CampaignDeleteView,
    CampaignDetailView,
    CampaignUpdateView,
)
from apps.users.models import User


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_input,expected",
    [
        (pytest.lazy_fixture("dm"), does_not_raise()),
        (pytest.lazy_fixture("player1"), does_not_raise()),
        (pytest.lazy_fixture("player2"), pytest.raises(PermissionDenied)),
    ],
)
def test_campaign_detail(
    test_input: User, expected: Callable, campaign1: Campaign, rf: RequestFactory
) -> None:
    """A player without a character in the Campaign should get a 404 Exception when trying to access the detail view."""
    with expected:
        request = rf.get("campaigns:detail", kwargs={"campaign_pk": campaign1.pk})
        request.htmx = False
        request.user = test_input
        CampaignDetailView.as_view()(request, campaign_pk=campaign1.pk)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_input,expected",
    [
        (pytest.lazy_fixture("dm"), 1),
        (pytest.lazy_fixture("player1"), 1),
        (pytest.lazy_fixture("player2"), 0),
    ],
)
def test_campaign_list(
    test_input: User,
    expected: int,
    campaign1: Campaign,
    client: Client,
) -> None:
    """If there is 1 Campaign in the object_list the user has access.

    The dm and player1 who has a character in the Campaign should be able to see it.
    Player2 does not have a character in the Campaign and should not.
    """
    headers = {"HX-Request": "true"}
    client.force_login(test_input)
    response = client.get(reverse("campaigns:list"), **headers)
    assert response.status_code == 200
    assert len(response.context_data["campaigns"]) == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_input,expected",
    [
        (pytest.lazy_fixture("dm"), does_not_raise()),
        (pytest.lazy_fixture("player1"), pytest.raises(PermissionDenied)),
        (pytest.lazy_fixture("player2"), pytest.raises(PermissionDenied)),
    ],
)
def test_campaign_update(
    test_input: User, expected: Callable, campaign1: Campaign, rf: RequestFactory
) -> None:
    """Only the DM should be able to update the Campaign."""
    with expected:
        data = {"description": "Update test"}
        request = rf.post(
            reverse("campaigns:update", kwargs={"campaign_pk": campaign1.pk}), data=data
        )
        request.htmx = True
        request.user = test_input
        request.data = data
        response = CampaignUpdateView.as_view()(
            request, data=request.data, campaign_pk=campaign1.pk
        )
        assert response.context_data["campaign"].description == "Update test"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_input,expected",
    [
        (pytest.lazy_fixture("dm"), does_not_raise()),
        (pytest.lazy_fixture("player1"), pytest.raises(PermissionDenied)),
        (pytest.lazy_fixture("player2"), pytest.raises(PermissionDenied)),
    ],
)
def test_campaign_delete(
    test_input: User, expected: Callable, campaign1: Campaign, rf: RequestFactory
) -> None:
    """Only the DM should be able to delete the Campaign."""
    with expected:
        request = rf.delete(
            reverse("campaigns:delete", kwargs={"campaign_pk": campaign1.pk})
        )
        request.user = test_input
        response = CampaignDeleteView.as_view()(request, campaign_pk=campaign1.pk)
        assert response.status_code == 302
        assert Campaign.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_input,expected",
    [
        (pytest.lazy_fixture("dm"), 204),
        (pytest.lazy_fixture("player1"), 204),
        (pytest.lazy_fixture("player2"), 302),
    ],
)
def test_campaign_create(test_input: User, expected: int, client: Client) -> None:
    """All logged-in users can create a campaign."""
    if not test_input.username == "player2":
        client.force_login(test_input)

    headers = {"HX-Request": "true"}
    response = client.post(
        reverse("campaigns:create"), headers=headers, data={"name": "Test"}
    )
    assert response.status_code == expected
    if response.status_code == 204:
        assert Campaign.objects.filter(name="Test").exists()
