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
from apps.maps.models import Map
from apps.maps.views import MapDeleteView, MapDetailView, MapUpdateView
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
def test_map_detail(
    test_input: User,
    expected: Callable,
    map: Map,
    rf: RequestFactory,
) -> None:
    """If a player doesn't have a Map in this map's campaign it shouldn't be able to see it."""
    with expected:
        request = rf.get(
            "campaigns:maps:detail",
            kwargs={"map_pk": map.pk, "campaign_pk": map.campaign_id},
        )
        request.htmx = False
        request.user = test_input
        MapDetailView.as_view()(request, map_pk=map.pk)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_input,expected,status_code",
    [
        (pytest.lazy_fixture("dm"), 1, 200),
        (pytest.lazy_fixture("player1"), 1, 200),
        (pytest.lazy_fixture("player2"), 0, 403),
    ],
)
def test_map_list(
    test_input: User, expected: int, status_code: int, client: Client, map: Map
) -> None:
    """If there is 1 Map in the object_list the user has access."""
    client.force_login(test_input)
    response = client.get(
        reverse("campaigns:maps:list", kwargs={"campaign_pk": map.campaign_id})
    )
    assert response.status_code == status_code
    if response.status_code == 200:
        assert len(response.context_data["maps"]) == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_input,expected",
    [
        (pytest.lazy_fixture("dm"), does_not_raise()),
        (pytest.lazy_fixture("player1"), pytest.raises(PermissionDenied)),
        (pytest.lazy_fixture("player2"), pytest.raises(PermissionDenied)),
    ],
)
def test_map_update(
    test_input: User, expected: Callable, map: Map, rf: RequestFactory
) -> None:
    """Only the dm should be able to update the Map."""
    with expected:
        data = {"description": "Update test"}
        request = rf.post(
            reverse(
                "campaigns:maps:update",
                kwargs={"map_pk": map.pk, "campaign_pk": map.campaign_id},
            ),
            data=data,
        )
        request.htmx = True
        request.user = test_input
        request.data = data
        response = MapUpdateView.as_view()(request, data=request.data, map_pk=map.pk)
        assert response.context_data["map"].description == "Update test"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_input,expected",
    [
        (pytest.lazy_fixture("dm"), does_not_raise()),
        (pytest.lazy_fixture("player1"), pytest.raises(PermissionDenied)),
        (pytest.lazy_fixture("player2"), pytest.raises(PermissionDenied)),
    ],
)
def test_map_delete(
    test_input: User, expected: Callable, map: Map, rf: RequestFactory
) -> None:
    """Only the DM should be able to delete the Map."""
    with expected:
        request = rf.delete(
            reverse(
                "campaigns:maps:delete",
                kwargs={"map_pk": map.pk, "campaign_pk": map.campaign_id},
            )
        )
        request.user = test_input
        response = MapDeleteView.as_view()(
            request, map_pk=map.pk, campaign_pk=map.campaign_id
        )
        assert response.status_code == 302
        assert Map.objects.count() == 0


@override_settings(MEDIA_ROOT=Path(tempfile.gettempdir()))
@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_input,expected",
    [
        (pytest.lazy_fixture("dm"), 204),
        (pytest.lazy_fixture("player1"), 403),
        (pytest.lazy_fixture("player2"), 403),
    ],
)
def test_map_create(
    test_input: User,
    expected: int,
    client: Client,
    mock_image: ImageFile,
    campaign1: Campaign,
) -> None:
    """All DM's users can create a Map."""
    if not test_input.username == "player2":
        client.force_login(test_input)

    headers = {"HX-Request": "true"}
    response = client.post(
        reverse("campaigns:maps:create", kwargs={"campaign_pk": campaign1.id}),
        headers=headers,
        data={"name": "Test", "image": mock_image},
        format="multipart",
    )
    assert response.status_code == expected
    if response.status_code == 204:
        assert Map.objects.filter(name="Test").exists()
