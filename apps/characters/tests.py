import tempfile
from contextlib import nullcontext as does_not_raise
from pathlib import Path
from typing import Callable

import pytest
from django.core.exceptions import PermissionDenied
from django.core.files.images import ImageFile
from django.http import Http404
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
    "test_input,expected",
    [
        (pytest.lazy_fixture("dm"), does_not_raise()),
        (pytest.lazy_fixture("player1"), does_not_raise()),
        (pytest.lazy_fixture("player2"), pytest.raises(Http404)),
    ],
)
def test_character_detail(
    test_input: User,
    expected: Callable,
    campaign1: Campaign,
    character1: Character,
    rf: RequestFactory,
) -> None:
    """If a player doesn't have a character in this character's campaign it shouldn't be able to see it."""
    with expected:
        request = rf.get("characters:detail", kwargs={"character_pk": character1.pk})
        request.htmx = False
        request.user = test_input
        CharacterDetailView.as_view()(request, character_pk=character1.pk)


@pytest.mark.django_db
@pytest.mark.parametrize("endpoint", ["characters:list", "characters:hx-list"])
@pytest.mark.parametrize(
    "test_input,expected",
    [
        (pytest.lazy_fixture("dm"), 0),
        (pytest.lazy_fixture("player1"), 1),
        (pytest.lazy_fixture("player2"), 0),
    ],
)
def test_character_list(
    test_input: User,
    expected: int,
    endpoint: str,
    character1: Character,
    client: Client,
) -> None:
    """If there is 1 Character in the object_list the user has access.

    If no campaign_pk is passed in as a parameter for the hx-list view then only the user's characters should be
        displayed since the request is for the normal character list and not the campaign's character list.
    """
    client.force_login(test_input)
    response = client.get(reverse(endpoint))
    assert response.status_code == 200
    assert len(response.context["characters"]) == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_input,expected,status_code",
    [
        (pytest.lazy_fixture("dm"), 1, 200),
        (pytest.lazy_fixture("player1"), 1, 200),
        (pytest.lazy_fixture("player2"), 0, 403),
    ],
)
def test_character_hx_list(
    test_input: User,
    expected: int,
    status_code: int,
    character1: Character,
    campaign1: Campaign,
    client: Client,
) -> None:
    """If there is 1 Character in the object_list the user has access.

    Any user that has access to the campaign should see the campaign's characters.
    """
    headers = {"HX-Request": "true"}
    client.force_login(test_input)
    response = client.get(
        reverse("campaigns:characters:hx-list", kwargs={"campaign_pk": campaign1.pk}),
        **headers
    )
    assert response.status_code == status_code
    characters = response.context.get("characters", None)
    if characters:
        assert len(response.context["characters"]) == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_input,expected",
    [
        (pytest.lazy_fixture("dm"), pytest.raises(PermissionDenied)),
        (pytest.lazy_fixture("player1"), does_not_raise()),
        (pytest.lazy_fixture("player2"), pytest.raises(PermissionDenied)),
    ],
)
def test_character_update(
    test_input: User, expected: Callable, character1: Character, rf: RequestFactory
) -> None:
    """Only the player should be able to update the Character."""
    with expected:
        data = {"description": "Update test"}
        request = rf.post(
            reverse("characters:update", kwargs={"character_pk": character1.pk}),
            data=data,
        )
        request.htmx = True
        request.user = test_input
        request.data = data
        response = CharacterUpdateView.as_view()(
            request, data=request.data, character_pk=character1.pk
        )
        assert response.context_data["character"].description == "Update test"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_input,expected",
    [
        (pytest.lazy_fixture("dm"), pytest.raises(PermissionDenied)),
        (pytest.lazy_fixture("player1"), does_not_raise()),
        (pytest.lazy_fixture("player2"), pytest.raises(PermissionDenied)),
    ],
)
def test_character_delete(
    test_input: User, expected: Callable, character1: Character, rf: RequestFactory
) -> None:
    """Only the player should be able to delete the Character."""
    with expected:
        request = rf.delete(
            reverse("characters:delete", kwargs={"character_pk": character1.pk})
        )
        request.user = test_input
        response = CharacterDeleteView.as_view()(request, character_pk=character1.pk)
        assert response.status_code == 302
        assert Character.objects.count() == 0


@override_settings(MEDIA_ROOT=Path(tempfile.gettempdir()))
@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_input,expected",
    [
        (pytest.lazy_fixture("dm"), 204),
        (pytest.lazy_fixture("player1"), 204),
        (pytest.lazy_fixture("player2"), 302),
    ],
)
def test_character_create(
    test_input: User, expected: int, client: Client, mock_image: ImageFile
) -> None:
    """All logged-in users can create a character."""
    if not test_input.username == "player2":
        client.force_login(test_input)

    headers = {"HX-Request": "true"}
    response = client.post(
        reverse("characters:create"),
        headers=headers,
        data={"name": "Test", "image": mock_image},
        format="multipart",
    )
    assert response.status_code == expected
    if response.status_code == 204:
        assert Character.objects.filter(name="Test").exists()
