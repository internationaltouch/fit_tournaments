from django import forms

from eligibility.mixins import BootstrapFormControlMixin
from eligibility.models import GrandParent, Parent, Player, PlayerDeclaration


class PlayerForm(BootstrapFormControlMixin, forms.ModelForm):
    class Meta:
        model = Player
        fields = "__all__"


class ParentForm(forms.ModelForm):
    class Meta:
        model = Parent
        exclude = ("child",)


class GrandParentForm(BootstrapFormControlMixin, forms.ModelForm):
    class Meta:
        model = GrandParent
        exclude = ("child",)


class PlayerDeclarationForm(BootstrapFormControlMixin, forms.ModelForm):
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
