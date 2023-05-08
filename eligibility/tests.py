import random
from datetime import date

from django.contrib.auth.models import Group, Permission
from django.test import override_settings
from guardian.shortcuts import assign_perm
from test_plus import TestCase

from eligibility.factory import (
    GrandParentFactory,
    ParentFactory,
    PlayerFactory,
    SuperuserFactory,
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

    def test_player_with_unknown_parent(self):
        ENG = Country.objects.get(iso3166a3="ENG")
        player = PlayerFactory.create(
            country_of_birth=ENG, residence=ENG, min_biological_parents=1
        )
        player = Player.objects.get(pk=player.pk)

        with self.subTest(
            "Must fail before the parent is added"
        ), self.assertRaisesRegex(ValueError, "at least 1 biological"):
            player.can_declare()

        parent = ParentFactory.create(child=player, country_of_birth=ENG)
        player = Player.objects.get(pk=player.pk)

        with self.subTest(
            "Must fail before the grandparents are added"
        ), self.assertRaisesRegex(ValueError, "at least 2 biological"):
            player.can_declare()

        GrandParentFactory.create_batch(2, child=parent, country_of_birth=ENG)

        with self.subTest("Must pass after we have one parent with both parents"):
            self.assertIsNone(player.can_declare())


@override_settings(PASSWORD_HASHERS=PASSWORD_HASHERS)
class UserExceptionTest(TestCase):
    def test_player_with_unknown_parent(self):
        with self.login(self.make_user()):
            with self.subTest("Create a player entry"):
                self.post(
                    "player",
                    data={
                        "name": "Joe Bloggs",
                        "date_of_birth": "2001-12-18",
                        "country_of_birth": "ENG",
                        "residence": "ENG",
                    },
                )
                self.response_302()

            player = Player.objects.get(name="Joe Bloggs")

            with self.subTest("Create parent", player=player):
                self.post(
                    "parent",
                    player.pk,
                    data={
                        "name": "Alice Bloggs",
                        "date_of_birth": "1978-06-14",
                        "country_of_birth": "ENG",
                    },
                )
                self.response_302()

            parent = Parent.objects.get(name="Alice Bloggs")

            for name, dob, born in [
                ("Bob", "1948-03-19", "ENG"),
                ("Mary", "1949-11-02", "WAL"),
            ]:
                with self.subTest(
                    "Create grandparent", name=name, parent=parent, player=player
                ):
                    self.post(
                        "grandparent",
                        player.pk,
                        parent.pk,
                        data={
                            "name": f"{name} Bloggs",
                            "date_of_birth": dob,
                            "country_of_birth": born,
                        },
                    )
                    self.response_302()

            self.get("players")
            self.assertResponseContains(
                "<small>Must have at least 2 biological parents.</small>"
            )

            # If we now allow this player to only have one parent, does that go away?
            player.exceptions = "Does not know any details about his father."
            player.min_biological_parents = 1
            player.save()

            self.get("players")
            self.assertResponseContains(
                '<span class="badge bg-danger">Declaration required</span>'
            )

    def test_player_with_unknown_grandparent(self):
        with self.login(self.make_user()):
            with self.subTest("Create a player entry"):
                self.post(
                    "player",
                    data={
                        "name": "Joe Bloggs",
                        "date_of_birth": "2001-12-18",
                        "country_of_birth": "ENG",
                        "residence": "ENG",
                    },
                )
                self.response_302()

            player = Player.objects.get(name="Joe Bloggs")

            for name, dob, born, parents in [
                (
                    "Bob Bloggs",
                    "1948-03-19",
                    "ENG",
                    [
                        ("Sarah Bloggs", "1921-07-03", "ENG"),
                    ],
                ),
                (
                    "Mary Bloggs",
                    "1949-11-02",
                    "WAL",
                    [
                        ("Jack Smith", "1927-06-30", "WAL"),
                        ("Jane Smith", "1929-05-01", "WAL"),
                    ],
                ),
            ]:
                with self.subTest("Create parent", name=name, player=player):
                    self.post(
                        "parent",
                        player.pk,
                        data={
                            "name": name,
                            "date_of_birth": dob,
                            "country_of_birth": born,
                        },
                    )
                    self.response_302()

                    parent = Parent.objects.get(name=name)

                    for gp_name, gp_dob, gp_born in parents:
                        with self.subTest(
                            "Create grandparent",
                            name=gp_name,
                            parent=parent,
                            player=player,
                        ):
                            self.post(
                                "grandparent",
                                player.pk,
                                parent.pk,
                                data={
                                    "name": gp_name,
                                    "date_of_birth": gp_dob,
                                    "country_of_birth": gp_born,
                                },
                            )
                            self.response_302()

            res = self.get("players")
            self.assertResponseContains(
                "<small>At least one parent does not have at least 2 biological parents.</small>"
            )

            # If we now allow this parent to only have one parent, does that go away?
            parent = Parent.objects.get(name="Bob Bloggs")
            parent.exceptions = "Does not know any details about his father."
            parent.min_biological_parents = 1
            parent.save()

            self.get("players")
            self.assertResponseContains(
                '<span class="badge bg-danger">Declaration required</span>'
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
        assign_perm("eligibility.change_player", cls.power_user, cls.first_player)

        # Populate a NTO user
        cls.nto_user = UserFactory.create()

        # Populate a regular user with permission to change only the first player.
        cls.user = UserFactory.create()
        assign_perm("eligibility.change_player", cls.user, cls.first_player)

        cls.country_map = {
            name: iso3166a3
            for name, iso3166a3 in Country.objects.values_list("name", "iso3166a3")
        }

    def test_data(self):
        for i, model in enumerate([Player, Parent, GrandParent]):
            with self.subTest(model.__name__):
                self.assertEqual(model.objects.count(), self.player_count * 2**i)

    def test_query_cost(self):
        with self.assertNumQueriesLessThan(5):
            for player in Player.objects.prefetch_related(
                "parent_set", "parent_set__grandparent_set"
            ):
                # We don't care about the result, just the cost.
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

    def test_view__declaration_list__protection_anonymous(self):
        with (
            self.subTest("Queries"),
            self.assertNumQueriesLessThan(5),
            self.subTest("Anonymous"),
        ):
            self.assertLoginRequired("nations")

    def test_view__declaration_list__protection_nto_user(self):
        country = random.choice(self.first_player.eligible())
        iso3166a3 = self.country_map[country]

        with self.login(self.user):
            with self.subTest(
                "Make declaration by regular user for player",
                user=self.power_user,
                player=self.first_player,
                country=country,
                iso3166a3=iso3166a3,
            ):
                response = self.post(
                    "declaration",
                    player=self.first_player.uuid,
                    data={"elected_country": iso3166a3},
                )
                self.assertRedirects(response, self.reverse("players"))

            with self.subTest(
                "Ensure regular user can't access NTO pages",
                user=self.user,
            ):
                self.get("nations")
                self.response_403()

        # After enrolling this player, the NTO user needs to be linked to the Group
        # that was created for the country.
        self.nto_user.groups.add(Group.objects.get(name=country))

        with self.login(self.nto_user):
            with self.subTest(user=self.nto_user):
                self.assertGoodView("nations", test_query_count=50)
            with self.subTest(user=self.nto_user):
                self.assertResponseContains(
                    f'<a href="{self.first_player.get_absolute_url()}">{self.first_player}</a>'
                )


@override_settings(PASSWORD_HASHERS=PASSWORD_HASHERS)
class AdminViewTests(TestCase):
    """
    Basic set of tests to make sure the regular admin pages will not be too slow to
    provide support when we launch. These tests are not intended to be exhaustive, we
    are focussing on list views as they are the most likely to be slow because of ORM
    performance issues when making naive queries.
    """

    @classmethod
    def setUpTestData(cls):
        # Set our query count aspirations, so we can adjust them as we go.
        cls.test_query_count = 110  # FIXME: I would like to get this down!

        cls.user = SuperuserFactory.create()

        # Create 500 players, each with 2 parents, each with 2 grandparents.
        cls.player_count = 500
        for player in PlayerFactory.create_batch(cls.player_count):
            for parent in ParentFactory.create_batch(2, child=player):
                GrandParentFactory.create_batch(2, child=parent)
            assign_perm("eligibility.change_player", cls.user, player)

        cls.country_map = {
            name: iso3166a3
            for name, iso3166a3 in Country.objects.values_list("name", "iso3166a3")
        }

    def test_players(self):
        with self.login(self.user):
            for player in Player.objects.order_by("?")[:250]:
                country = random.choice(player.eligible())
                iso3166a3 = self.country_map[country]
                with self.subTest(player=player, country=country, iso3166a3=iso3166a3):
                    self.post(
                        "declaration",
                        player=player.uuid,
                        data={"elected_country": iso3166a3},
                    )
                    self.response_302()

            with self.subTest():
                self.assertGoodView(
                    "admin:eligibility_player_changelist",
                    test_query_count=self.test_query_count,
                )

            with self.subTest("DecadeBornListFilter"):
                self.assertGoodView(
                    "admin:eligibility_player_changelist",
                    test_query_count=self.test_query_count,
                    data={"decade": "1990"},
                )

            with self.subTest("EligibilityListFilter"):
                self.assertGoodView(
                    "admin:eligibility_player_changelist",
                    test_query_count=self.test_query_count,
                    data={"eligible": "Australia"},
                )

            with self.subTest("DecadeBornListFilter and EligibilityListFilter"):
                self.assertGoodView(
                    "admin:eligibility_player_changelist",
                    test_query_count=self.test_query_count,
                    data={"decade": "1990", "eligible": "Australia"},
                )

    def test_parents(self):
        with self.login(self.user):
            self.assertGoodView(
                "admin:eligibility_parent_changelist",
                test_query_count=self.test_query_count,
            )

    def test_grandparents(self):
        with self.login(self.user):
            self.assertGoodView(
                "admin:eligibility_grandparent_changelist",
                test_query_count=self.test_query_count,
            )

    def test_playerdeclaration(self):
        with self.login(self.user):
            for player in Player.objects.order_by("?")[:250]:
                country = random.choice(player.eligible())
                self.post(
                    "declaration",
                    player=player.uuid,
                    data={"elected_country": country},
                )

            with self.subTest():
                self.assertGoodView(
                    "admin:eligibility_playerdeclaration_changelist",
                    test_query_count=self.test_query_count,
                )

            with self.subTest("ElectedCountryListFilter"):
                self.assertGoodView(
                    "admin:eligibility_playerdeclaration_changelist",
                    data={"country": "England"},
                )

    def test_nationalsquad(self):
        with self.login(self.user):
            self.assertGoodView(
                "admin:eligibility_nationalsquad_changelist",
                test_query_count=self.test_query_count,
            )

    def test_nationalteam(self):
        with self.login(self.user):
            self.assertGoodView(
                "admin:eligibility_nationalteam_changelist",
                test_query_count=self.test_query_count,
            )

    def test_country(self):
        with self.login(self.user):
            self.assertGoodView(
                "admin:eligibility_country_changelist",
                test_query_count=self.test_query_count,
            )
