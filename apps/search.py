from itertools import chain

from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.campaigns.models import Campaign
from apps.characters.models import Character
from apps.maps.models import Map


def search_all(request: HttpRequest) -> HttpResponse:
    """Full text search across all models."""
    query = request.GET.get("search", None)
    characters = Character.objects.filter(vector_column=query).filter(
        player=request.user
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

    results = chain(characters, campaigns, maps)

    return render(
        request=request,
        context={"results": results},
        template_name="search_results.html",
    )
