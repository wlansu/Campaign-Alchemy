import pytest
from django.http import Http404
from django.test import Client
from django.test.client import RequestFactory
from model_bakery import baker

from apps.campaigns.models import Campaign
from apps.campaigns.views import CampaignDetailView
from apps.characters.models import Character
from apps.users.models import User


@pytest.fixture
def dm(client: Client) -> User:
    user = baker.make(User, is_active=True)
    client.force_login(user)
    return user


@pytest.fixture
def player1(client: Client) -> User:
    user = baker.make(User, is_active=True)
    client.force_login(user)
    return user


@pytest.fixture
def player2(client: Client) -> User:
    user = baker.make(User, is_active=True)
    client.force_login(user)
    return user


@pytest.fixture
def character1(player1) -> Character:
    character = baker.make(Character, player=player1)
    return character


@pytest.fixture
def campaign1(dm: User, character1: User) -> Campaign:
    campaign = baker.make(Campaign, dm=dm, characters=[character1])
    return campaign


# @pytest.mark.django_db
# @pytest.mark.parametrize(
#     "test_input,expected", [(dm, 200), (player1, 200), (player2, 404)]
# )
# def test_campaign_list(
#     test_input: User, expected: int, client: Client, campaign1: Campaign
# ) -> None:
#     response = client.get(
#         reverse("campaigns:detail", kwargs={"campaign_pk": campaign1.pk})
#     )
#     assert response.status_code == expected


@pytest.mark.django_db
def test_campaign_detail(rf: RequestFactory) -> None:
    dm = baker.make(User, is_active=True)
    player1 = baker.make(User, is_active=True)
    player2 = baker.make(User, is_active=True)
    character = baker.make(Character, player=player1)
    campaign = baker.make(Campaign, characters=[character], dm=dm)
    request = rf.get("campaigns:detail", kwargs={"campaign_pk": campaign.pk})
    request.htmx = False

    request.user = dm
    response1 = CampaignDetailView.as_view()(request, campaign_pk=campaign.pk)
    assert response1.status_code == 200

    request.user = player1
    response2 = CampaignDetailView.as_view()(request, campaign_pk=campaign.pk)
    assert response2.status_code == 200

    request.user = player2
    with pytest.raises(Http404):
        CampaignDetailView.as_view()(request, campaign_pk=campaign.pk)
