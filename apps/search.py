from itertools import chain

from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.campaigns.models import Campaign
from apps.characters.models import Character
from apps.locations.models import Location
from apps.maps.models import Map
from apps.users.models import User


def search_all(request: HttpRequest) -> HttpResponse:
    """Full text search across all models.

    See: https://pganalyze.com/blog/full-text-search-django-postgres
    """
    query = request.GET.get("search")
    user: User = request.user
    characters = (
        Character.objects.filter(vector_column=query)
        .filter(
            Q(player=request.user)
            | Q(creator=request.user)
            | Q(campaign__dm=request.user)
            | Q(campaign__characters__player=request.user)
        )
        .distinct()
    )
    campaigns = (
        Campaign.objects.filter(vector_column=query)
        .filter(Q(dm=request.user) | Q(characters__player=request.user))
        .distinct()
    )
    maps = (
        Map.objects.filter(vector_column=query)
        .filter(
            Q(campaign__dm=request.user) | Q(campaign__characters__player=request.user)
        )
        .distinct()
    )
    locations = (
        Location.objects.filter(vector_column=query)
        .filter(
            Q(map__campaign__dm=request.user)
            | Q(map__campaign__characters__player=request.user)
        )
        .distinct()
    )
    if not user.is_dm:
        # TODO: I would rather do this in the query itself but it would become exceedingly complex,
        #   if it could be done at all.
        locations = locations.exclude(hidden=True)

    results = chain(characters, campaigns, maps, locations)

    return render(
        request=request,
        context={"results": results},
        template_name="search_results.html",
    )
