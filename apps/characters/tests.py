import tempfile
from contextlib import nullcontext as does_not_raise
from pathlib import Path
from typing import Callable

import pytest
from django.core.exceptions import PermissionDenied
from django.core.files.images import ImageFile
from django.test import override_settings
from django.test.client import Client, RequestFactory
from django.urls import reverse

from apps.campaigns.models import Campaign
from apps.characters.models import Character
from apps.characters.views import (
    CharacterDeleteView,
    CharacterDetailView,
    CharacterUpdateView,
)
from apps.users.models import User


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user,expected_result",
    [
        (pytest.lazy_fixture("dm"), does_not_raise()),
        (pytest.lazy_fixture("player1"), does_not_raise()),
        (pytest.lazy_fixture("player2"), pytest.raises(PermissionDenied)),
    ],
)
def test_character_detail(
    user: User,
    expected_result: Callable,
    campaign1: Campaign,
    character1: Character,
    rf: RequestFactory,
) -> None:
    """If a player doesn't have a character in this character's campaign it shouldn't be able to see it."""
    with expected_result:
        request = rf.get("characters:detail", kwargs={"character_pk": character1.pk})
        request.htmx = False
        request.user = user
        CharacterDetailView.as_view()(request, character_pk=character1.pk)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user,expected_result_count",
    [
        (pytest.lazy_fixture("dm"), 0),
        (pytest.lazy_fixture("player1"), 1),
        (pytest.lazy_fixture("player2"), 0),
    ],
)
def test_character_list(
    user: User,
    expected_result_count: int,
    character1: Character,
    client: Client,
) -> None:
    """If there is 1 Character in the object_list the user has access.

    If no campaign_pk is passed in as a parameter for the list view then only the user's characters should be
        displayed since the request is for the normal character list and not the campaign's character list.
    """
    client.force_login(user)
    response = client.get(reverse("characters:list"))
    assert response.status_code == 200
    assert len(response.context["characters"]) == expected_result_count


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user,expected_result_count,status_code",
    [
        (pytest.lazy_fixture("dm"), 1, 200),
        (pytest.lazy_fixture("player1"), 1, 200),
        (pytest.lazy_fixture("player2"), 0, 403),
    ],
)
def test_character_campaign_list(
    user: User,
    expected_result_count: int,
    status_code: int,
    character1: Character,
    campaign1: Campaign,
    client: Client,
) -> None:
    """If there is 1 Character in the object_list the user has access.

    Any user that has access to the campaign should see the campaign's characters.
    """
    headers = {"Request": "true"}
    client.force_login(user)
    response = client.get(
        reverse("campaigns:characters:list", kwargs={"campaign_pk": campaign1.pk}),
        **headers
    )
    assert response.status_code == status_code
    characters = response.context.get("characters", None)
    if characters:
        assert len(response.context["characters"]) == expected_result_count


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user,expected_result",
    [
        (pytest.lazy_fixture("dm"), pytest.raises(PermissionDenied)),
        (pytest.lazy_fixture("player1"), does_not_raise()),
        (pytest.lazy_fixture("player2"), pytest.raises(PermissionDenied)),
    ],
)
def test_character_update(
    user: User, expected_result: Callable, character1: Character, rf: RequestFactory
) -> None:
    """Only the player should be able to update the Character."""
    with expected_result:
        data = {"description": "Update test"}
        request = rf.post(
            reverse("characters:update", kwargs={"character_pk": character1.pk}),
            data=data,
        )
        request.htmx = True
        request.user = user
        request.data = data
        response = CharacterUpdateView.as_view()(
            request, data=request.data, character_pk=character1.pk
        )
        assert response.context_data["character"].description == "Update test"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user,expected_result",
    [
        (pytest.lazy_fixture("dm"), pytest.raises(PermissionDenied)),
        (pytest.lazy_fixture("player1"), does_not_raise()),
        (pytest.lazy_fixture("player2"), pytest.raises(PermissionDenied)),
    ],
)
def test_character_delete(
    user: User, expected_result: Callable, character1: Character, rf: RequestFactory
) -> None:
    """Only the player should be able to delete the Character."""
    with expected_result:
        request = rf.delete(
            reverse("characters:delete", kwargs={"character_pk": character1.pk})
        )
        request.user = user
        response = CharacterDeleteView.as_view()(request, character_pk=character1.pk)
        assert response.status_code == 302
        assert Character.objects.count() == 0


@override_settings(MEDIA_ROOT=Path(tempfile.gettempdir()))
@pytest.mark.django_db
@pytest.mark.parametrize(
    "user,status_code",
    [
        (pytest.lazy_fixture("dm"), 204),
        (pytest.lazy_fixture("player1"), 204),
        (pytest.lazy_fixture("player2"), 302),
    ],
)
@pytest.mark.parametrize(
    "data",
    [{"name": "Test", "image": pytest.lazy_fixture("mock_image")}, {"name": "Test"}],
)
def test_character_create(
    user: User, status_code: int, data: dict, client: Client, mock_image: ImageFile
) -> None:
    """All logged-in users can create a character."""
    if not user.username == "player2":
        client.force_login(user)

    headers = {"Request": "true"}
    response = client.post(
        reverse("characters:create"),
        headers=headers,
        data=data,
        format="multipart",
    )
    assert response.status_code == status_code
    if response.status_code == 204:
        assert Character.objects.filter(name="Test").exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user,status_code",
    [
        (pytest.lazy_fixture("dm"), 404),
        (pytest.lazy_fixture("player1"), 404),
        (pytest.lazy_fixture("player2"), 204),
    ],
)
def test_add_character_to_campaign(
    user: User,
    status_code: int,
    client: Client,
    campaign1: Campaign,
    character2: Character,
) -> None:
    """Only a Player can add their character to a Campaign by using the invite_code."""
    client.force_login(user)
    headers = {"Request": "true"}
    response = client.post(
        reverse("characters:add", kwargs={"character_pk": character2.pk}),
        headers=headers,
        data={"invite_code": campaign1.invite_code, "character_pk": character2.pk},
    )
    assert response.status_code == status_code
    if response.status_code == 204:
        character2.refresh_from_db()
        assert character2.campaign == campaign1


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user,status_code",
    [
        (pytest.lazy_fixture("dm"), 204),
        (pytest.lazy_fixture("player1"), 204),
        (pytest.lazy_fixture("player2"), 403),
    ],
)
def test_remove_character_from_campaign(
    user: User,
    status_code: int,
    client: Client,
    campaign1: Campaign,
    character1: Character,
) -> None:
    """Only a Player, or their DM, can remove their character to a Campaign by using the invite_code."""
    client.force_login(user)
    headers = {"Request": "true"}
    response = client.get(
        reverse("characters:remove", kwargs={"character_pk": character1.pk}),
        headers=headers,
    )
    assert response.status_code == status_code
    character1.refresh_from_db()
    if response.status_code == 204:
        assert character1.campaign is None
    else:
        assert character1.campaign


@pytest.mark.django_db
def test_user_has_access_cache_invalidation(
    character2: Character, campaign1: Campaign, client: Client
) -> None:
    """Check that the user_has_read_access_to_campaign cache is invalidated correctly."""
    client.force_login(character2.player)
    headers = {"Request": "true"}
    denied = client.get(
        reverse("campaigns:detail", kwargs={"campaign_pk": campaign1.pk})
    )
    assert denied.status_code == 403
    join = client.post(
        reverse("characters:add", kwargs={"character_pk": character2.pk}),
        headers=headers,
        data={"character_pk": character2.pk, "invite_code": campaign1.invite_code},
    )
    assert join.status_code == 204
    accepted = client.get(
        reverse("campaigns:detail", kwargs={"campaign_pk": campaign1.pk})
    )
    assert accepted.status_code == 200
