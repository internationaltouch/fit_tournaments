from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import BooleanField, Case, F, Q, Value, When, Count
from django.db.models.query import QuerySet


class PersonQuerySet(QuerySet):
    def eligibility_by_birth(self):
        return self.annotate(
            birthplace=Case(
                When(country_of_birth__isnull=True, then=F("country_of_birth_other")),
                default=F("country_of_birth__name"),
            ),
        )


class PlayerQueryset(PersonQuerySet):
    def eligibility_by_residence(self):
        return self.annotate(
            residency=Case(
                When(residence__isnull=True, then=F("residence_other")),
                default=F("residence__name"),
            ),
            parents_birthplace=ArrayAgg(
                "parent__country_of_birth__name", distinct=True
            ),
            grandparents_birthplace=ArrayAgg(
                "parent__grandparent__country_of_birth__name", distinct=True
            ),
            parent_count=Count("parent__uuid"),
            biological_parent_count=Count(
                "parent__uuid", filter=Q(parent__adopted=False), distinct=True
            ),
            biological_grandparent_count=Count(
                "parent__grandparent__uuid",
                filter=Q(parent__grandparent__adopted=False),
                distinct=True,
            ),
        )

    def eligible_for(self, country_name):
        return self.filter(
            # Direct eligibility
            Q(country_of_birth__name=country_name)
            | Q(country_of_birth_other=country_name)
            | Q(residence__name=country_name)
            | Q(residence_other=country_name)
            # Courtesy of parent place of birth
            | Q(parent__country_of_birth__name=country_name)
            | Q(parent__country_of_birth_other=country_name)
            # Courtesy of grandparent place of birth
            | Q(parent__grandparent__country_of_birth__name=country_name)
            | Q(parent__grandparent__country_of_birth_other=country_name)
        ).distinct()


class PlayerDeclarationQuerySet(QuerySet):
    def is_supersceded(self):
        return self.annotate(
            is_supersceded=Case(
                When(
                    supersceded_by__isnull=False,
                    then=Value(True, output_field=BooleanField()),
                ),
                default=Value(False, output_field=BooleanField()),
            ),
        )

    def supersceded(self):
        return self.exclude(supersceded_by__isnull=True)
