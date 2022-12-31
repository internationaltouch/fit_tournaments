from django.core import serializers
from django.core.exceptions import ValidationError


def person_clean(instance, country_names):
    """
    Utility to handle raising ValidationError's for Player, Parent, and GrandParent models.
    """
    errors = {}

    if instance.country_of_birth_other:
        if instance.country_of_birth:
            errors.setdefault("country_of_birth_other", []).append(
                "You may only provide a custom country of birth "
                "if you have not selected from the above."
            )
        if instance.country_of_birth_other.strip().lower() in country_names:
            errors.setdefault("country_of_birth_other", []).append(
                "You can't manually type in a country of birth "
                "that appears in the list above."
            )
    elif not instance.country_of_birth:
        errors.setdefault("country_of_birth", []).append(
            "You must indicate the country of birth."
        )

    if hasattr(instance, "residence_other"):
        if instance.residence_other:
            if instance.residence:
                errors.setdefault("residence_other", []).append(
                    "You may only provide a custom country of residence "
                    "if you have not selected from the above."
                )
            if instance.residence_other.strip().lower() in country_names:
                errors.setdefault("residence_other", []).append(
                    "You can't manually type in a country of residence "
                    "that appears in the list above."
                )
        elif not instance.residence:
            errors.setdefault("residence", []).append(
                "You must indicate the country of residence."
            )

    if errors:
        raise ValidationError(errors)


def person_snapshot(instance):
    objects = [instance]
    for parent in instance.parent_set.select_related():
        objects.append(parent)
        for grandparent in parent.grandparent_set.all():
            objects.append(grandparent)
    return serializers.serialize("json", objects)
