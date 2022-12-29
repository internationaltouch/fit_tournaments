from django.db import models

from eligibility.query import PersonQuerySet, PlayerQueryset


class PersonManager(models.Manager.from_queryset(PersonQuerySet)):
    def get_queryset(self):
        return super().get_queryset().eligibility_by_birth()


class PlayerManager(models.Manager.from_queryset(PlayerQueryset)):
    def get_queryset(self):
        return super().get_queryset().eligibility_by_birth().eligibility_by_residence()
