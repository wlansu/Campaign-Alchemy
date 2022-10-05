from django.contrib.auth.models import AbstractUser
from django.db.models import BooleanField, CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for Campaign Alchemy.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    can_be_dm = BooleanField(default=True)

    def get_absolute_url(self) -> str:
        """Get url for user's detail view."""
        return reverse("users:detail", kwargs={"username": self.username})
