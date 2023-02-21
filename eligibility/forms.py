from django import forms
from django.forms import BaseFormSet, BaseInlineFormSet
from guardian.shortcuts import get_objects_for_user
from modelforms.forms import ModelForm

from eligibility.models import (
    GrandParent,
    NationalSquad,
    Parent,
    Player,
    PlayerDeclaration,
)


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = "__all__"


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
    name = forms.HiddenInput()
    class Meta:
        model = NationalSquad
        fields = ("name", "players")


class PlayerDeclarationMultipleChoiceField(forms.ModelMultipleChoiceField):
    widget = forms.CheckboxSelectMultiple
    def label_from_instance(self, obj):
        return str(obj.player)


class NationalSquadFormSet(BaseInlineFormSet):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields["name"].widget = forms.HiddenInput()
        form.fields["players"] = PlayerDeclarationMultipleChoiceField(
            queryset=get_objects_for_user(
                self.user,
                "eligibility.view_playerdeclaration",
                use_groups=True,
                any_perm=True,
            ).filter(
                supersceded_by__isnull=True,
                elected_country__name=form.instance.name,
            ),
            label=form.initial.get("name", form.instance.name),
            required=False,
        )
