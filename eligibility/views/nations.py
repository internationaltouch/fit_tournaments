from django.contrib.auth.decorators import login_required
from django.db.models import Case, Value, When
from django.forms import formset_factory
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from guardian.decorators import permission_required
from guardian.shortcuts import get_objects_for_user

from eligibility.forms import SightingForm, SightingFormSet
from eligibility.models import Country, Event, Player, PlayerDeclaration


@login_required
def declaration_list(request):
    if not request.user.groups.exists():
        return TemplateResponse(
            request, "eligibility/playerdeclaration_list_403.html", status=403
        )
    qs = get_objects_for_user(
        request.user,
        "eligibility.view_playerdeclaration",
        use_groups=True,
        any_perm=True,
    )
    object_list = qs.exclude(supersceded_by__isnull=False)
    context = {
        "object_list": object_list,
    }
    return TemplateResponse(request, "eligibility/nations/playerdeclaration_list.html", context)


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
        squad_date_class=Case(When(squad_date__gt=date, then=Value("warning")), default=Value("danger")),
        team_date_class=Case(When(team_date__gt=date, then=Value("warning")), default=Value("danger")),
    )
    group_list = request.user.groups.filter(name__in=Country.objects.values_list("name"))
    context = {
        "object_list": object_list,
        "group_list": group_list,  # FIXME: not required, just using while developing.
        "date": date,
        "cancel_url": reverse("nations"),
    }
    return TemplateResponse(request, "eligibility/nations/event_list.html", context)
