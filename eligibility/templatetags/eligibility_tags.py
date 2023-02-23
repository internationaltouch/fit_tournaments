import pdb
from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from django.db.models import Model
from django.db.models.query import QuerySet
from django.forms import model_to_dict
from django.template.library import Library

register = Library()


@dataclass
class DiffItem:
    value: str
    state: Optional[bool] = None


@register.filter("pdb")
def do_pdb(obj):
    if settings.DEBUG:
        pdb.set_trace()
    return obj


@register.filter("fieldname")
def get_fieldname(obj, field):
    return obj._meta.get_field(field).verbose_name


@register.filter("type")
def get_type(obj):
    if isinstance(obj, QuerySet):
        return obj.model._meta.verbose_name
    elif isinstance(obj, Model):
        return obj._meta.verbose_name
    else:
        return obj.__class__.__name__


@register.filter("dirty")
def get_dirty(obj):
    return obj.get_dirty_fields(check_relationship=True, verbose=True)


@register.filter("model_to_dict")
def do_model_to_dict(obj, exclude=None):
    if exclude is not None:
        exclude = (exclude,)
    return model_to_dict(obj, exclude=exclude)


@register.filter("diff")
def do_diff(lhs, rhs):
    left, right = set(lhs), set(rhs)
    full_set = left | right
    ordered_set = sorted(full_set)
    result = []
    for each in ordered_set:
        if each in left and each in right:
            result.append(DiffItem(each))
        else:
            result.append(DiffItem(each, each in right))
    return result
