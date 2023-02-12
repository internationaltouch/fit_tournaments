from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet, formset_factory, inlineformset_factory
from modelforms.forms import ModelForm

from eligibility.fields import BooleanChoiceField
from eligibility.models import GrandParent, Parent, Person, Player, PlayerDeclaration
from eligibility.utils import boolean_coerce


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
        if index:
            form.fields[
                "evidence"
            ].label = (
                f"{self.people[index]} was born in {self.people[index].birthplace}"
            )
            form.fields["evidence"].help_text = (
                f"Note the documentation you viewed that demonstrates {self.people[index]} "
                f"was born in {self.people[index].birthplace}."
            )
            form.fields["evidence"].widget.attrs[
                "placeholder"
            ] = "Examples: birth certificate, passport, etc"
        else:
            form.fields[
                "evidence"
            ].label = (
                f"{self.people[index]} is a resident of {self.people[index].residency}"
            )
            form.fields["evidence"].help_text = (
                f"Note the documentation you viewed that demonstrates {self.people[index]} "
                f"is a resident of {self.people[index].residency}, including dates."
            )
            form.fields["evidence"].widget.attrs[
                "placeholder"
            ] = "Examples: rental statements, utility bills, etc"
