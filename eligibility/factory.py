import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from eligibility.models import Country, GrandParent, Parent, Player


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    username = factory.Sequence(lambda n: "user%04d" % (n + 1))
    email = factory.Sequence(lambda n: "user%03d@example.com" % (n + 1))

    password = "crypt$$azoV33FJ2h3AA"  # pre-crypted "password"
    is_active = True


class SuperuserFactory(UserFactory):
    is_superuser = True
    is_staff = True


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
