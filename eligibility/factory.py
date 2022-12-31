import factory
from factory.django import DjangoModelFactory

from eligibility.models import Country, GrandParent, Parent, Player


class PlayerFactory(DjangoModelFactory):
    class Meta:
        model = Player

    name = factory.Faker("name")
    date_of_birth = factory.Faker("date_between", end_date="-15y")
    country_of_birth = factory.Iterator(Country.objects.all())
    residence = factory.Iterator(Country.objects.all())


class ParentFactory(DjangoModelFactory):
    class Meta:
        model = Parent

    name = factory.Faker("name")
    date_of_birth = factory.Faker("date_between", start_date="-55y", end_date="-45y")
    country_of_birth = factory.Iterator(Country.objects.all())
    adopted = False


class GrandParentFactory(DjangoModelFactory):
    class Meta:
        model = GrandParent

    name = factory.Faker("name")
    date_of_birth = factory.Faker("date_between", start_date="-90y", end_date="-75y")
    country_of_birth = factory.Iterator(Country.objects.all())
    adopted = False
