from django.test import TestCase

from eligibility.factory import GrandParentFactory, ParentFactory, PlayerFactory
from eligibility.models import Country, Player


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
