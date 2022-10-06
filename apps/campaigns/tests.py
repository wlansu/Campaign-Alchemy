from contextlib import nullcontext as does_not_raise
from typing import Callable

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


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_input,expected",
    [
        (pytest.lazy_fixture("dm"), does_not_raise()),
        (pytest.lazy_fixture("player1"), does_not_raise()),
        (pytest.lazy_fixture("player2"), pytest.raises(Http404)),
    ],
)
def test_campaign_list(
    test_input: User, expected: Callable, campaign1: Campaign, rf: RequestFactory
) -> None:
    with expected:
        request = rf.get("campaigns:detail", kwargs={"campaign_pk": campaign1.pk})
        request.htmx = False
        request.user = test_input
        response = CampaignDetailView.as_view()(request, campaign_pk=campaign1.pk)
        assert response.status_code == 200
