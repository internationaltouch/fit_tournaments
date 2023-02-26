from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.generic import DetailView
from guardian.decorators import permission_required
from guardian.shortcuts import assign_perm, get_objects_for_user

from eligibility.forms import (
    GrandParentForm,
    ParentForm,
    PlayerDeclarationForm,
    PlayerForm,
)
from eligibility.models import GrandParent, Parent, Player, PlayerDeclaration


@login_required
def player_list(request):
    players = (
        get_objects_for_user(
            request.user, "eligibility.change_player", with_superuser=False
        )
        .eligibility_by_birth()
        .eligibility_by_residence()
        .prefetch_related(
            Prefetch(
                "declarations",
                queryset=PlayerDeclaration.objects.defer("data", "evidence_nation"),
            ),
        )
    )
    context = {
        "object_list": players,
    }
    return TemplateResponse(request, "eligibility/player_list.html", context)


@login_required
def player_create(request):
    if request.method == "POST":
        form = PlayerForm(data=request.POST)
        if form.is_valid():
            instance = form.save()
            # XXX: This is really important! Without setting the change
            #      permission on the newly created object, it will not be
            #      editable in the player_edit view.
            assign_perm("eligibility.change_player", request.user, instance)
            return redirect(instance.get_absolute_url())
    else:
        form = PlayerForm()
    context = {"form": form, "cancel_url": reverse("players")}
    return TemplateResponse(request, "eligibility/player_form.html", context)


@permission_required("eligibility.change_player", (Player, "pk", "pk"))
def player_edit(request, pk):
    instance = get_object_or_404(Player, pk=pk)
    if request.method == "POST":
        form = PlayerForm(data=request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(reverse("players"))
    else:
        form = PlayerForm(instance=instance)
    context = {
        "object": instance,
        "form": form,
    }
    try:
        instance.can_declare()
    except ValueError as exc:
        context["declaration"] = str(exc)
    return TemplateResponse(request, "eligibility/player_form_detail.html", context)


@permission_required("eligibility.change_player", (Player, "pk", "player"))
def parent_edit(request, player, pk=None):
    child = get_object_or_404(Player, pk=player)
    if pk is None:
        instance = Parent(child=child)
    else:
        instance = get_object_or_404(child.parent_set, pk=pk)
    if request.method == "POST":
        form = ParentForm(data=request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(child.get_absolute_url())
    else:
        form = ParentForm(instance=instance)

    context = {
        "object": instance if pk is not None else None,
        "form": form,
        "player": child,
        "cancel_url": child.get_absolute_url(),
    }
    return TemplateResponse(request, "eligibility/parent_form.html", context)


@permission_required("eligibility.change_player", (Player, "pk", "player"))
def grandparent_edit(request, player, parent, pk=None):
    grandchild = get_object_or_404(Player, pk=player)
    child = get_object_or_404(grandchild.parent_set, pk=parent)
    if pk is None:
        instance = GrandParent(child=child)
    else:
        instance = get_object_or_404(child.grandparent_set, pk=pk)
    if request.method == "POST":
        form = GrandParentForm(data=request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(grandchild.get_absolute_url())
    else:
        form = GrandParentForm(instance=instance)

    context = {
        "object": instance if pk is not None else None,
        "form": form,
        "parent": child,
        "player": grandchild,
        "cancel_url": grandchild.get_absolute_url(),
    }
    return TemplateResponse(request, "eligibility/grandparent_form.html", context)


@permission_required("eligibility.change_player", (Player, "pk", "player"))
def declaration_create(request, player):
    player = get_object_or_404(Player, pk=player)
    try:
        player.can_declare()
    except ValueError as exc:
        raise Http404(f"Unable to make player declaration for {player}: {exc}") from exc
    instance = PlayerDeclaration(player=player, author=request.user)
    if request.method == "POST":
        form = PlayerDeclarationForm(data=request.POST, instance=instance)
        if form.is_valid():
            instance = form.save()
            group, _ = Group.objects.get_or_create(name=instance.elected_country)
            assign_perm("eligibility.view_playerdeclaration", group, instance)
            return redirect(reverse("players"))
    else:
        form = PlayerDeclarationForm(instance=instance)
    context = {
        "object": instance,
        "form": form,
        "player": player,
        "cancel_url": player.get_absolute_url(),
    }
    return TemplateResponse(request, "eligibility/playerdeclaration_form.html", context)


class PlayerDeclarationView(LoginRequiredMixin, DetailView):
    model = PlayerDeclaration
