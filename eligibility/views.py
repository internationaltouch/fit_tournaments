from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from eligibility.forms import (
    GrandParentForm,
    ParentForm,
    PlayerDeclarationForm,
    PlayerForm,
)
from eligibility.models import GrandParent, Parent, Player, PlayerDeclaration


def index(request):
    return TemplateResponse(request, "eligibility/index.html")


class PlayerList(LoginRequiredMixin, ListView):
    model = Player


class PlayerCreate(LoginRequiredMixin, CreateView):
    model = Player
    form_class = PlayerForm

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = reverse("players")
        return context


class PlayerEdit(LoginRequiredMixin, UpdateView):
    model = Player
    form_class = PlayerForm
    template_name = "eligibility/player_form_detail.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        try:
            self.object.can_declare()
        except ValueError as exc:
            context["declaration"] = str(exc)
        return context


class ParentCreate(LoginRequiredMixin, CreateView):
    model = Parent
    form_class = ParentForm

    def get_success_url(self) -> str:
        return reverse("player", args=(self.kwargs["player"],))

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        player = get_object_or_404(Player, pk=self.kwargs["player"])
        kwargs["instance"] = Parent(child=player)
        return kwargs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        player = context["form"].instance.child
        context["player"] = player
        context["cancel_url"] = reverse("player", args=(player.pk,))
        return context


class ParentEdit(LoginRequiredMixin, UpdateView):
    model = Parent
    form_class = ParentForm

    def get_success_url(self) -> str:
        return reverse("player", args=(self.kwargs["player"],))

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        player = context["form"].instance.child
        context["player"] = player
        context["cancel_url"] = reverse("player", args=(player.pk,))
        return context


class GrandParentCreate(LoginRequiredMixin, CreateView):
    model = GrandParent
    form_class = GrandParentForm

    def get_success_url(self) -> str:
        return reverse("player", args=(self.kwargs["player"],))

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        parent = get_object_or_404(Parent, pk=self.kwargs["parent"])
        kwargs["instance"] = GrandParent(child=parent)
        return kwargs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        parent = context["form"].instance.child
        context["parent"] = parent
        context["cancel_url"] = reverse("player", args=(parent.child.pk,))
        return context


class GrandParentEdit(LoginRequiredMixin, UpdateView):
    model = GrandParent
    form_class = GrandParentForm

    def get_success_url(self) -> str:
        return reverse("player", args=(self.kwargs["player"],))

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        parent = context["form"].instance.child
        context["parent"] = parent
        context["player"] = parent.child
        context["cancel_url"] = reverse("player", args=(parent.child.pk,))
        return context


class PlayerDeclarationCreate(LoginRequiredMixin, CreateView):
    model = PlayerDeclaration
    form_class = PlayerDeclarationForm
    success_url = reverse_lazy("players")

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        player = get_object_or_404(Player, pk=self.kwargs["player"])
        try:
            player.can_declare()
        except ValueError as exc:
            raise Http404(
                f"Unable to make player declaration for {player}: {exc}"
            ) from exc
        if kwargs["instance"] is None:
            kwargs["instance"] = PlayerDeclaration(player=player)
        return kwargs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        player = context["form"].instance.player
        context["player"] = player
        context["cancel_url"] = reverse("player", args=(player.pk,))
        return context


class PlayerDeclarationView(LoginRequiredMixin, DetailView):
    model = PlayerDeclaration
