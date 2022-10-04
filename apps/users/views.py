from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import BaseForm
from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return ["users/user_detail_partial.html"]
        return ["users/user_detail.html"]


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, UpdateView):

    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def form_valid(self, form: BaseForm) -> HttpResponse:
        self.object = form.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "objectChanged"})

    def get_object(self) -> User:
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()
