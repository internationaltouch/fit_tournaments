from datetime import date

from django.test import TestCase

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

        with self.subTest("Players eligible for AUS"):
            self.assertQuerysetEqual(Player.objects.eligible_for(AUS.name), [player])

        with self.subTest("Only eligible for AUS"):
            self.assertEqual(Player.objects.get(pk=player.pk).eligible(), [AUS.name])

    def test_extreme_player(self):
        "Validate that a player with 'exotic' history has eligibility across all of them."
        country = Country.objects.iterator()
        player = PlayerFactory.create(
            country_of_birth=next(country),
            residence=next(country),
        )
        # Both biological parents were adopted, and also has two adopted parents that
        # were themselves adopted...
        for adopted in (False, True):
            for rel1 in ("father", "mother"):
                parent = ParentFactory.create(
                    child=player,
                    country_of_birth=next(country),
                    adopted=adopted,
                )
                for rel2 in ("grandfather", "grandmother"):
                    GrandParentFactory.create(
                        child=parent,
                        country_of_birth=next(country),
                    )
                    GrandParentFactory.create(
                        child=parent,
                        country_of_birth=next(country),
                        adopted=True,
                    )

        with self.subTest("Player has MANY eligibility options to choose from"):
            eligible_for = Player.objects.get(pk=player.pk).eligible()
            # Expected length is
            # 2 (birth, residence)
            # + 2 bio p + 4 bio gp + 4 adopted gp of bio p
            # + 2 adopted p + 4 bio gp of adopted p + 4 adopted gp of adopted p
            # = 2 + 2 + 4 + 4 + 2 + 4 + 4 = 22
            self.assertCountEqual(
                eligible_for,
                Country.objects.values_list("name", flat=True)[:22],
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
