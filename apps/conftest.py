import tempfile

import pytest
from django.core.files.images import ImageFile
from model_bakery import baker
from PIL import Image

from apps.campaigns.models import Campaign
from apps.characters.models import Character
from apps.maps.models import Map
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
def character2(player2) -> Character:
    character = baker.make(Character, player=player2)
    return character


@pytest.fixture
def campaign1(dm: User, character1: User) -> Campaign:
    campaign = baker.make(Campaign, dm=dm, characters=[character1])
    return campaign


@pytest.fixture
def mock_image() -> ImageFile:
    image = Image.new("RGBA", size=(50, 50), color=(256, 0, 0))
    image_file = tempfile.NamedTemporaryFile(suffix=".png")
    image.save(image_file)
    image_file.seek(0)
    return ImageFile(image_file)


@pytest.fixture
def map(campaign1: Campaign) -> Map:
    map = baker.make(Map, campaign=campaign1)
    return map
