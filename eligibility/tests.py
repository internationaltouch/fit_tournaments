from datetime import date

from test_plus import TestCase

from eligibility.factory import GrandParentFactory, ParentFactory, PlayerFactory
from eligibility.models import Country, Player
from eligibility.utils import get_age


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
