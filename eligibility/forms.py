from eligibility.models import Player
from django import forms
from eligibility.mixins import BootstrapFormControlMixin


class PlayerForm(BootstrapFormControlMixin, forms.ModelForm):
    class Meta:
        model = Player
        fields = "__all__"