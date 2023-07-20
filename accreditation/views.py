from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from search_views.search import SearchListView

from accreditation.forms import PlayerDeclarationForm
from eligibility.models import PlayerDeclaration


class SuperUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class PlayerDeclarationSearchList(SuperUserRequiredMixin, SearchListView):
    queryset = PlayerDeclaration.objects.select_related("player", "elected_country")
    paginate_by = 30
    template_name = "accreditation/playerdeclaration_list.html"
    form_class = PlayerDeclarationSearchForm
    filter_class = PlayerDeclarationFilter


class PlayerDeclarationView(SuperUserRequiredMixin, UpdateView):
    queryset = PlayerDeclaration.objects.filter(supersceded_by__isnull=True)
    form_class = PlayerDeclarationForm
    template_name = "accreditation/playerdeclaration_form.html"
    success_url = reverse_lazy("accreditation")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs
