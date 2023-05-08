from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Case, Value, When
from django.forms import formset_factory, inlineformset_factory
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from guardian.decorators import permission_required
from guardian.shortcuts import assign_perm, get_objects_for_user

from eligibility.forms import (
    NationalSquadForm,
    NationalSquadFormSet,
    NationalTeamFormSet,
    SightingForm,
    SightingFormSet,
)
from eligibility.models import (
    Country,
    Event,
    NationalSquad,
    NationalTeam,
    Player,
    PlayerDeclaration,
)


@login_required
def declaration_list(request):
    if not request.user.groups.exists():
        return TemplateResponse(
            request, "eligibility/playerdeclaration_list_403.html", status=403
        )
    object_list = (
        get_objects_for_user(
            request.user,
            "eligibility.view_playerdeclaration",
            use_groups=True,
            any_perm=True,
            with_superuser=False,
        )
        .exclude(supersceded_by__isnull=False)
        .select_related()
        .distinct()
    )

    # TODO: improve performance of the above query
    paginator = Paginator(object_list, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page": page_obj,
    }
    return TemplateResponse(
        request, "eligibility/nations/playerdeclaration_list.html", context
    )


@permission_required(
    "eligibility.view_playerdeclaration",
    (PlayerDeclaration, "pk", "uuid"),
    accept_global_perms=True,
)
def declaration_verify(request, uuid):
    instance = get_object_or_404(PlayerDeclaration, uuid=uuid)
    player = get_object_or_404(Player, uuid=instance.player_id)
    form_count = len(instance.data) + 1
    formset_class = formset_factory(
        SightingForm,
        SightingFormSet,
        extra=0,
        min_num=form_count,
        max_num=form_count,
    )
    people = instance.data[:1] + instance.data

    if request.method == "POST":
        formset = formset_class(people=people, data=request.POST)
        if formset.is_valid():
            data = {}  # Group the values by the people they belong to
            for person, evidence in zip(people, formset.cleaned_data):
                data.setdefault(person, []).append(evidence["evidence"])
            instance.evidence_nation = [
                # First item is a pair, everything else we pick out the singleton.
                value if len(value) > 1 else value[0]
                for value in data.values()
            ]
            instance.save(update_fields=["evidence_nation"])
            return redirect(reverse("nations"))

    elif instance.evidence_nation:
        # When the data has previously been submitted, unpack it and pass to the
        # formset constructor to pre-populate the form fields.
        initial = [
            {"evidence": evidence}
            # First item is a pair, everything else is a singleton.
            for evidence in instance.evidence_nation[0] + instance.evidence_nation[1:]
        ]
        formset = formset_class(people=people, initial=initial)

    else:
        formset = formset_class(people=people)

    context = {
        "object": instance,
        "player": player,
        "formset": formset,
    }
    return TemplateResponse(
        request, "eligibility/nations/playerdeclaration_form.html", context
    )


@permission_required("eligibility.create_nationalsquad")
def event_list(request):
    date = timezone.now().date()
    object_list = Event.objects.filter(closing_date__gt=date).annotate(
        squad_date_class=Case(
            When(squad_date__gt=date, then=Value("warning")),
            default=Value("danger"),
        ),
        team_date_class=Case(
            When(team_date__gt=date, then=Value("warning")),
            default=Value("danger"),
        ),
    )
    context = {
        "object_list": object_list,
        "date": date,
        "cancel_url": reverse("nations"),
    }
    return TemplateResponse(request, "eligibility/nations/event_list.html", context)


@permission_required("eligibility.edit_event")
@transaction.atomic
def event_notify_squad(request, event):
    instance = get_object_or_404(Event, pk=event)

    # FIXME: creating these objects should probably be done outside of a
    #   request/response cycle.
    group_list = request.user.groups.filter(
        name__in=Country.objects.values_list("name")
    )
    group_count = group_list.count()
    for group in group_list:
        squad, created = instance.squads.get_or_create(name=group.name)
        if created:
            assign_perm("eligibility.change_nationalsquad", group, squad)

    formset_class = inlineformset_factory(
        Event,
        NationalSquad,
        form=NationalSquadForm,
        formset=NationalSquadFormSet,
        extra=0,
        can_delete=False,
    )

    queryset = (
        get_objects_for_user(
            request.user,
            "eligibility.change_nationalsquad",
            use_groups=True,
            any_perm=True,
            with_superuser=False,
        )
        .filter(event=event)
        .order_by("name")
    )

    if not queryset.exists():
        raise Http404("User has no national squads to manage.")

    context = {
        "object": instance,
        "object_list": queryset,
        "due_date": instance.squad_date,
        "cancel_url": reverse("events"),
    }

    if instance.squad_date < timezone.now().date():
        return TemplateResponse(
            request, "eligibility/nations/nationalsquad_list.html", context
        )

    if request.method == "POST":
        formset = formset_class(
            data=request.POST, instance=instance, queryset=queryset, user=request.user
        )
        if formset.is_valid():
            formset.save()
            return redirect(reverse("events"))
    else:
        formset = formset_class(instance=instance, queryset=queryset, user=request.user)

    context["formset"] = formset
    return TemplateResponse(request, "eligibility/nations/event_form.html", context)


@permission_required("eligibility.edit_event")
def event_notify_team(request, event):
    instance = get_object_or_404(Event, pk=event)

    squads = (
        get_objects_for_user(
            request.user,
            "eligibility.change_nationalsquad",
            use_groups=True,
            any_perm=True,
            with_superuser=False,
        )
        .filter(event=event)
        .order_by("name")
    )

    if not squads.exists():
        raise Http404("User has no national squads to manage.")

    groups = Group.objects.in_bulk(field_name="name")
    for squad in squads:
        team, created = NationalTeam.objects.get_or_create(squad=squad)
        if created:
            assign_perm("eligibility.change_nationalteam", groups[squad.name], team)

    queryset = NationalTeam.objects.filter(squad__event=instance)

    context = {
        "object": instance,
        "object_list": queryset,
        "due_date": instance.team_date,
        "cancel_url": reverse("events"),
    }

    if instance.squad_date < timezone.now().date():
        return TemplateResponse(
            request, "eligibility/nations/nationalteam_list.html", context
        )

    if request.method == "POST":
        formset = NationalTeamFormSet(data=request.POST, queryset=queryset)
        if formset.is_valid():
            formset.save()
            return redirect(reverse("events"))
    else:
        formset = NationalTeamFormSet(queryset=queryset)

    context["formset"] = formset
    return TemplateResponse(request, "eligibility/nations/event_form.html", context)
