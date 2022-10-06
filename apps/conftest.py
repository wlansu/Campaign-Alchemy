import pytest
from model_bakery import baker

from apps.campaigns.models import Campaign
from apps.characters.models import Character
from apps.users.models import User
from apps.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def dm() -> User:
    user = baker.make(User, is_active=True, username="dm")
    return user


@pytest.fixture
def player1() -> User:
    user = baker.make(User, is_active=True, username="player1")
    return user


@pytest.fixture
def player2() -> User:
    user = baker.make(User, is_active=True, username="player2")
    return user


@pytest.fixture
def character1(player1) -> Character:
    character = baker.make(Character, player=player1)
    return character


@pytest.fixture
def campaign1(dm: User, character1: User) -> Campaign:
    campaign = baker.make(Campaign, dm=dm, characters=[character1])
    return campaign
