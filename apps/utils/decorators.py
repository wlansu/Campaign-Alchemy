from functools import wraps

from django.shortcuts import redirect

from apps.campaigns.models import Campaign


def campaign_not_set(function):
    """
    Decorator for views that require a campaign to be set in the session.
    """

    @wraps(function)
    def wrapper(request, *args, **kwargs):
        try:
            Campaign.objects.get(id=request.session.get("campaign_id", None))
        except Campaign.DoesNotExist:
            return redirect("campaigns:create")
        return function(request, *args, **kwargs)

    return wrapper
