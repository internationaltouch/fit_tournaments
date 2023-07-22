from django.urls import include, path

from eligibility import views
from eligibility.views import nations, players

player_urls = [
    path("create", players.player_create, name="player"),
    path("<uuid:pk>", players.player_edit, name="player"),
    path("<uuid:pk>/exception", players.player_exception_request, name="exception"),
    path("<uuid:player>/declarations/create", players.declaration_create, name="declaration"),
    path("<uuid:player>/declarations/<uuid:pk>", players.PlayerDeclarationView.as_view(), name="declaration"),
    path("<uuid:player>/parents/create", players.parent_edit, name="parent"),
    path("<uuid:player>/parents/<uuid:pk>", players.parent_edit, name="parent"),
    path("<uuid:player>/parents/<uuid:parent>/grandparent/create", players.grandparent_edit, name="grandparent"),
    path("<uuid:player>/parents/<uuid:parent>/grandparent/<uuid:pk>", players.grandparent_edit, name="grandparent"),
]

nation_urls = [
    path("<uuid:uuid>", nations.declaration_verify, name="declaration"),
    path("events", nations.event_list, name="events"),
    path("events/<uuid:event>/squad", nations.event_notify_squad, name="squad"),
    path("events/<uuid:event>/team", nations.event_notify_team, name="team"),
]

urlpatterns = [
    path("", views.index, name="index"),
    path("players", players.player_list, name="players"),
    path("players/", include(player_urls)),
    path("nations", nations.declaration_list, name="nations"),
    path("nations/", include(nation_urls)),
]
