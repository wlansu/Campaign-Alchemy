from contextlib import nullcontext as does_not_raise
from typing import Callable

import pytest
from django.core.exceptions import PermissionDenied
from django.test.client import Client, RequestFactory
from django.urls import reverse
from PIL.ImageFile import ImageFile

from apps.locations.models import Location
from apps.locations.views import LocationDeleteView, LocationUpdateView
from apps.maps.models import Map
from apps.users.models import User


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user,expected_result_count,status_code",
    [
        (pytest.lazy_fixture("dm"), 1, 200),
        (pytest.lazy_fixture("player1"), 1, 200),
        (pytest.lazy_fixture("player2"), 0, 403),
    ],
)
def test_location_list(
    user: User,
    expected_result_count: int,
    status_code: int,
    client: Client,
    location: Location,
) -> None:
    """Any User with a Character in the Location's Map's Campaign can see the Locations."""
    client.force_login(user)
    response = client.get(
        reverse(
            "campaigns:maps:locations:list",
            kwargs={"campaign_pk": location.map.campaign_id, "map_pk": location.map_id},
        )
    )
    assert response.status_code == status_code
    if response.status_code == 200:
        assert len(response.context["locations"]) == expected_result_count


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user,expected_result",
    [
        (pytest.lazy_fixture("dm"), does_not_raise()),
        (pytest.lazy_fixture("player1"), does_not_raise()),
        (pytest.lazy_fixture("player2"), pytest.raises(PermissionDenied)),
    ],
)
def test_location_update(
    user: User, expected_result: Callable, location: Location, rf: RequestFactory
) -> None:
    """Any User with a Character in the Location's Map's Campaign can update the Location."""
    with expected_result:
        data = {"description": "Update test"}
        request = rf.post(
            reverse(
                "campaigns:maps:locations:update",
                kwargs={
                    "map_pk": location.map.pk,
                    "campaign_pk": location.map.campaign_id,
                    "location_pk": location.pk,
                },
            ),
            data=data,
        )
        request.htmx = True
        request.user = user
        request.data = data
        response = LocationUpdateView.as_view()(
            request,
            data=request.data,
            map_pk=location.map.pk,
            location_pk=location.pk,
            campaign_pk=location.map.campaign_id,
        )
        assert response.context_data["location"].description == "Update test"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user,expected_result",
    [
        (pytest.lazy_fixture("dm"), does_not_raise()),
        (pytest.lazy_fixture("player1"), does_not_raise()),
        (pytest.lazy_fixture("player2"), pytest.raises(PermissionDenied)),
    ],
)
def test_location_delete(
    user: User, expected_result: Callable, location: Location, rf: RequestFactory
) -> None:
    """Only the DM should be able to delete the Location."""
    with expected_result:
        request = rf.delete(
            reverse(
                "campaigns:maps:locations:delete",
                kwargs={
                    "map_pk": location.map_id,
                    "campaign_pk": location.map.campaign_id,
                    "location_pk": location.pk,
                },
            )
        )
        request.user = user
        response = LocationDeleteView.as_view()(
            request,
            map_pk=location.map_id,
            campaign_pk=location.map.campaign_id,
            location_pk=location.pk,
        )
        assert response.status_code == 302
        assert Location.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user,status_code",
    [
        (pytest.lazy_fixture("dm"), 204),
        (pytest.lazy_fixture("player1"), 204),
        (pytest.lazy_fixture("player2"), 302),
    ],
)
def test_location_create(
    user: User, status_code: int, client: Client, map: Map, mock_image: ImageFile
) -> None:
    """Any User with a Character in the Location's Map's Campaign can create a Location."""
    if not user.username == "player2":
        client.force_login(user)

    headers = {"HX-Request": "true"}
    response = client.post(
        reverse(
            "campaigns:maps:locations:create",
            kwargs={"campaign_pk": map.campaign_id, "map_pk": map.pk},
        ),
        headers=headers,
        data={"name": "Test", "longitude": 1, "latitude": 1, "image": mock_image},
    )
    assert response.status_code == status_code
    if not user.username == "player2":
        assert Location.objects.filter(name="Test").exists()
