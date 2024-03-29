from django import forms
from django.db.models import Q
from django.forms import BaseFormSet, BaseInlineFormSet, modelformset_factory
from django.utils.safestring import mark_safe
from guardian.shortcuts import get_objects_for_user
from modelforms.forms import ModelForm

from eligibility.models import (
    DeclarationExceptionRequest,
    GrandParent,
    NationalSquad,
    NationalTeam,
    Parent,
    Player,
    PlayerDeclaration,
)
from eligibility.utils import get_age


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = (
            "name",
            "date_of_birth",
            "country_of_birth",
            "country_of_birth_other",
            "residence",
            "residence_other",
        )


class ParentForm(ModelForm):
    class Meta:
        model = Parent
        fields = (
            "name",
            "date_of_birth",
            "country_of_birth",
            "country_of_birth_other",
            "adopted",
        )


class GrandParentForm(ModelForm):
    class Meta:
        model = GrandParent
        fields = (
            "name",
            "date_of_birth",
            "country_of_birth",
            "country_of_birth_other",
            "adopted",
        )


class DeclarationExceptionRequestForm(ModelForm):
    class Meta:
        model = DeclarationExceptionRequest
        fields = ("reason",)
        labels = {
            "reason": "Please provide an explanation as to why you cannot complete the declaration in the form."
        }


class PlayerDeclarationAdminForm(ModelForm):
    class Meta:
        model = PlayerDeclaration
        fields = (
            "player",
            "elected_country",
            "supersceded_by",
            "verified_by",
            "verified_comments",
        )

    def save(self, commit=True):
        """
        Save this form's self.instance object if commit=True. Otherwise, add
        a save_m2m() method to the form which can be called after the instance
        is saved manually at a later time. Return the model instance.
        """
        if self.errors:
            raise ValueError(
                "The %s could not be %s because the data didn't validate."
                % (
                    self.instance._meta.object_name,
                    "created" if self.instance._state.adding else "changed",
                )
            )
        if commit:
            # If committing, save the instance and the m2m data immediately.
            self.instance.save(
                update_fields=[
                    "player",
                    "elected_country",
                    "evidence_nation",
                    "verified_by",
                    "verified_comments",
                ]
            )
            self._save_m2m()
        else:
            # If not committing, add a method to the form to allow deferred
            # saving of m2m data.
            self.save_m2m = self._save_m2m
        return self.instance


class PlayerDeclarationForm(forms.ModelForm):
    class Meta:
        model = PlayerDeclaration
        fields = ("elected_country",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Shrink the queryset to only permit choices from the countries the player data
        # would permit based on their eligible countries.
        player = self.instance.player
        qs = self.fields["elected_country"].queryset.filter(name__in=player.eligible())
        try:
            current = player.declarations.first()
            if current is not None:
                qs = qs.exclude(name=current.elected_country)
        except PlayerDeclaration.DoesNotExist:
            pass
        self.fields["elected_country"].queryset = qs


class SightingForm(forms.Form):
    evidence = forms.CharField(label="", required=True)


class SightingFormSet(BaseFormSet):
    def __init__(self, people, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.people = people

    def add_fields(self, form, index):
        super().add_fields(form, index)

        person = self.people[index]
        help_text = f"Note the documentation you viewed that demonstrates {person} "

        if index:
            label = f"{person} was born in {person.birthplace}"
            placeholder = "Examples: birth certificate, passport, etc"
            help_text += f"was born in {person.birthplace}."
        else:
            label = f"{person} is a resident of {person.residency}"
            placeholder = "Examples: rental statements, utility bills, etc"
            help_text += f"is a resident of {person.residency}, including dates."

        field = form.fields["evidence"]
        field.label = label
        field.widget.attrs["placeholder"] = placeholder
        field.help_text = help_text


class NationalSquadForm(forms.ModelForm):
    class Meta:
        model = NationalSquad
        fields = ("players",)


class PlayerDeclarationMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        res = f"{obj.player} ({get_age(obj.player)})"
        for country in obj.eligible_for:
            if obj.supersceded_by:
                color = (
                    "danger"
                    if country == obj.supersceded_by.elected_country.name
                    else "secondary"
                )
            else:
                color = (
                    "success" if country == obj.elected_country.name else "secondary"
                )
            res += f' <span class="badge bg-{color}">{country}</span>'
        return mark_safe(res)


class NationalSquadFormSet(BaseInlineFormSet):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def add_fields(self, form, index):
        super().add_fields(form, index)
        queryset = (
            get_objects_for_user(
                self.user,
                "eligibility.view_playerdeclaration",
                use_groups=True,
                any_perm=True,
            )
            .filter(elected_country__name=form.instance.name)
            .filter(
                Q(
                    # If a declaration has been superseded we do not want to use it.
                    supersceded_by__isnull=True,
                    # If the nation has not recorded that they've verified the
                    # eligibility standing of the individual in the declaration, we
                    # don't want them to be able to select them.
                    evidence_nation__isnull=False,
                )
                |
                # We want to make sure that already selected items remain in the
                # queryset, even if they've subsequently gone out of scope; we can
                # give the nation visual feedback.
                Q(pk__in=form.instance.players.all())
            )
        )
        form.fields["players"] = PlayerDeclarationMultipleChoiceField(
            queryset=queryset,
            required=False,
            widget=forms.CheckboxSelectMultiple,
            help_text=(
                f"Select the names of players dual-eligible for {form.instance.name} "
                f"that you are naming in the squad. Only players included in this "
                f"squad will be able to be progressed to the final teams."
            ),
        )


class NationalTeamForm(ModelForm):
    class Meta:
        model = NationalTeam
        fields = ("players",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["players"] = PlayerDeclarationMultipleChoiceField(
            queryset=(
                self.instance.squad.players.exclude(supersceded_by__isnull=False)
                | self.instance.players.all()
            ),
            required=False,
            widget=forms.CheckboxSelectMultiple,
            help_text=(
                f"Select the names of players dual-eligible for {self.instance.squad.name} "
                f"that you are naming in one of your final <strong>teams</strong>."
            ),
        )


NationalTeamFormSet = modelformset_factory(
    NationalTeam,
    form=NationalTeamForm,
    fields=("players",),
    extra=0,
    can_delete=False,
)
