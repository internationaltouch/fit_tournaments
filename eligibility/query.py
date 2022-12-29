from django.db.models import Case, F, When
from django.db.models.query import QuerySet


class PersonQuerySet(QuerySet):
    def eligibility_by_birth(self):
        return self.annotate(
            birthplace=Case(
                When(country_of_birth__isnull=True, then=F("country_of_birth_other")),
                default=F("country_of_birth__name"),
            )
        )


class PlayerQueryset(PersonQuerySet):
    def eligibility_by_residence(self):
        return self.annotate(
            residency=Case(
                When(residence__isnull=True, then=F("residence_other")),
                default=F("residence__name"),
            )
        )
