import json

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils import timezone


def boolean_coerce(value):
    if value in {1, "1"}:
        return True
    if value in {0, "0"}:
        return False


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
    return json.loads(serializers.serialize("json", objects))


def person_declaration_clean(instance):
    errors = {}

    if instance.timestamp is None:
        # This is how we know we have not yet been saved. Future updates MUST not
        # be allowed to modify the contents of the "name", "eligible_for", or
        # "data" fields.
        try:
            instance.name = instance.player.name
            instance.eligible_for = instance.player.eligible()
            instance.data = person_snapshot(instance.player)
        except ObjectDoesNotExist:
            errors.setdefault("player", []).append(
                "Player must be eligible for at least one country to make a declaration."
            )

    if (
        instance.elected_country_id
        and instance.elected_country.name not in instance.eligible_for
    ):
        errors.setdefault("elected_country", []).append(
            f"{instance.elected_country} is not one that player is eligible for. "
            f"Choices are {', '.join(instance.eligible_for)}."
        )

    if instance.supersceded_by:
        if instance.supersceded_by == instance:
            errors.setdefault("supersceded_by", []).append(
                "A declaration may not superscede itself."
            )

        if instance.supersceded_by.player != instance.player:
            errors.setdefault("supersceded_by", []).append(
                "Must superscede a declaration from the same player."
            )

    if errors:
        raise ValidationError(errors)


def get_age(person, census_date=None):
    if census_date is None:
        census_date = timezone.now().today()
    return (
        census_date.year
        - person.date_of_birth.year
        - (
            (census_date.month, census_date.day)
            < (person.date_of_birth.month, person.date_of_birth.day)
        )
    )
