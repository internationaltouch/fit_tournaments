from typing import Any

from django import forms
from django.forms import ModelForm

from eligibility.models import PlayerDeclaration


class PlayerDeclarationSearchForm(forms.Form):
    search_text = forms.CharField(required=False, label="Name or Country")
    search_year = forms.IntegerField(required=False, label="Year of Birth")


class PlayerDeclarationForm(ModelForm):
    class Meta:
        model = PlayerDeclaration
        fields = ["verified_comments"]
        labels = {"verified_comments": "Verifier Comments"}

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.verified_by = user
        self.fields["verified_comments"].widget.attrs["placeholder"] = "Comments"
        self.fields["approve"] = forms.BooleanField(
            label="",
            required=True,
            help_text="You must tick this box to verify the declaration.",
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
            self.instance.save(update_fields=["verified_comments", "verified_by"])
            self._save_m2m()
        else:
            # If not committing, add a method to the form to allow deferred
            # saving of m2m data.
            self.save_m2m = self._save_m2m
        return self.instance
