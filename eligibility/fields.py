from bootstrap5.widgets import RadioSelectButtonGroup
from django import forms
from django.core import serializers
from django.core.serializers.base import DeserializationError
from django.db import models
from django.forms import model_to_dict
from django.utils.translation import gettext_lazy as _

from eligibility.utils import boolean_coerce

# FORM FIELDS


class BooleanChoiceField(forms.TypedChoiceField):
    widget = RadioSelectButtonGroup

    def __init__(self, *args, **kwargs):
        defaults = {
            "choices": [
                ("1", _("Yes")),
                ("0", _("No")),
            ],
            "initial": "0",
            "coerce": boolean_coerce,
            "required": True,
        }
        defaults.update(kwargs)
        super().__init__(*args, **defaults)

    def prepare_value(self, value):
        if value is not None:
            return str(int(value))


# MODEL FIELDS


class BooleanField(models.BooleanField):
    def formfield(self, **kwargs):
        defaults = {"form_class": BooleanChoiceField}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class JSONField(models.JSONField):
    def from_db_value(self, value, expression, connection):
        try:
            cached_values = [
                obj.object for obj in serializers.deserialize("json", value)
            ]
            db_sync = [
                each._meta.model._default_manager.get(pk=each.pk)
                for each in cached_values
            ]
            for db, cached in zip(db_sync, cached_values):
                data = model_to_dict(cached)
                for key in data:
                    setattr(db, key, getattr(cached, key))
            return db_sync
        except DeserializationError:
            return super().from_db_value(value, expression, connection)
