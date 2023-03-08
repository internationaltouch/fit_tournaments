import unittest
from datetime import date

from django.contrib.auth.models import Permission
from django.test import override_settings
from guardian.shortcuts import assign_perm
from test_plus import TestCase

from eligibility.factory import (
    GrandParentFactory,
    ParentFactory,
    PlayerFactory,
    UserFactory,
)
from eligibility.models import Country, GrandParent, Parent, Player
from eligibility.utils import get_age

PASSWORD_HASHERS = ("django.contrib.auth.hashers.CryptPasswordHasher",)


class EligibilityTest(TestCase):
    def test_boring_player(self):
        "Ensure that a 'boring' player whose entire history is with one country ONLY has that country."
        AUS = Country.objects.get(iso3166a3="AUS")
        player = PlayerFactory.create(country_of_birth=AUS, residence=AUS)
        for parent in ParentFactory.create_batch(2, child=player, country_of_birth=AUS):
            GrandParentFactory.create_batch(2, child=parent, country_of_birth=AUS)
        self.assertEqual(Player.objects.get(pk=player.pk).eligible(), [AUS.name])

    def test_boring_player_living_overseas(self):
        "Ensure that a 'boring' player only has eligibility for their ancestry country and their residence country."
        AUS = Country.objects.get(iso3166a3="AUS")
        ENG = Country.objects.get(iso3166a3="ENG")
        player = PlayerFactory.create(country_of_birth=AUS, residence=ENG)
        for parent in ParentFactory.create_batch(2, child=player, country_of_birth=AUS):
            GrandParentFactory.create_batch(2, child=parent, country_of_birth=AUS)
        self.assertEqual(
            Player.objects.get(pk=player.pk).eligible(), [AUS.name, ENG.name]
        )

    def test_player_with_parent_born_overseas(self):
        AUS = Country.objects.get(iso3166a3="AUS")
        NZL = Country.objects.get(iso3166a3="NZL")
        player = PlayerFactory.create(country_of_birth=AUS, residence=AUS)
        parent1 = ParentFactory.create(child=player, country_of_birth=AUS)
        parent2 = ParentFactory.create(child=player, country_of_birth=NZL)
        for parent in [parent1, parent2]:
            GrandParentFactory.create_batch(2, child=parent, country_of_birth=AUS)
        with self.subTest("Players eligible for both"):
            self.assertEqual(
                Player.objects.get(pk=player.pk).eligible(), [AUS.name, NZL.name]
            )

    def test_player_with_grandparents_born_overseas(self):
        AUS = Country.objects.get(iso3166a3="AUS")
        ENG = Country.objects.get(iso3166a3="ENG")
        player = PlayerFactory.create(country_of_birth=AUS, residence=AUS)
        for parent in ParentFactory.create_batch(2, child=player, country_of_birth=AUS):
            GrandParentFactory.create_batch(2, child=parent, country_of_birth=ENG)
        self.assertEqual(
            Player.objects.get(pk=player.pk).eligible(), [AUS.name, ENG.name]
        )


class UtilityTests(TestCase):
    def test_get_age_edge_cases(self):
        "Ensure that get_age() handles edge cases correctly."
        player = PlayerFactory.create(date_of_birth=date(2014, 2, 8))
        for census_date, expected_age in [
            (date(2022, 2, 7), 7),
            (date(2022, 2, 8), 8),
            (date(2022, 2, 9), 8),
        ]:
            with self.subTest(census_date=census_date):
                self.assertEqual(get_age(player, census_date), expected_age)


@override_settings(PASSWORD_HASHERS=PASSWORD_HASHERS)
class ViewPerformanceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Get some countries that we will use to populate the players and their ancestors.
        AUS = Country.objects.get(iso3166a3="AUS")
        NZL = Country.objects.get(iso3166a3="NZL")
        ENG = Country.objects.get(iso3166a3="ENG")

        # Create 500 players, each with 2 parents, each with 2 grandparents.
        cls.player_count = 500
        players = PlayerFactory.create_batch(cls.player_count)
        for player in players:
            for parent in ParentFactory.create_batch(2, child=player):
                GrandParentFactory.create_batch(2, child=parent)

        # Save the first player for later.
        cls.first_player = Player.objects.order_by("name").first()

        # Populate a power user
        cls.power_user = UserFactory.create()
        # Grant permission to the user to change ALL players.
        perm = Permission.objects.get(codename="change_player")
        cls.power_user.user_permissions.set([perm])

        # Populate a regular user with permission to change only the first player.
        cls.user = UserFactory.create()
        assign_perm("eligibility.change_player", cls.user, cls.first_player)

    def test_data(self):
        for i, model in enumerate([Player, Parent, GrandParent]):
            with self.subTest(model.__name__):
                self.assertEqual(model.objects.count(), self.player_count * 2**i)

    def test_query_cost(self):
        with self.assertNumQueriesLessThan(5):
            for player in Player.objects.prefetch_related(
                "parent_set", "parent_set__grandparent_set"
            ):
                player.can_declare_bool

    def test_view__player_list__protection_anonymous(self):
        with (
            self.subTest("Queries"),
            self.assertNumQueriesLessThan(5),
            self.subTest("Anonymous"),
        ):
            self.assertLoginRequired("players")

    def test_view__player_list__protection_user(self):
        with self.login(self.user):
            # XXX: try to go lower if we drive the other numbers down
            self.assertGoodView("players", test_query_count=20)
            self.assertResponseContains(
                f'<a href="{self.first_player.get_absolute_url()}">{self.first_player}</a>'
            )

    def test_view__player_list__protection_power_user(self):
        # FIXME: we don't really want this failure!
        with self.login(self.power_user):
            self.assertGoodView("players", test_query_count=110)
            self.assertResponseContains(
                f'<a href="{self.first_player.get_absolute_url()}">{self.first_player}</a>'
            )
