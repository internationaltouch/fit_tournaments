from django.urls import include, path

from eligibility import views
from eligibility.views import nations, players

player_urls = [
    path("create", players.player_create, name="player"),
    path("<uuid:pk>", players.player_edit, name="player"),
    path("<uuid:player>/declarations/create", players.declaration_create, name="declaration"),
    path("<uuid:player>/declarations/<uuid:pk>", players.PlayerDeclarationView.as_view(), name="declaration"),
    path("<uuid:player>/parents/create", players.parent_edit, name="parent"),
    path("<uuid:player>/parents/<uuid:pk>", players.parent_edit, name="parent"),
    path("<uuid:player>/parents/<uuid:parent>/grandparent/create", players.grandparent_edit, name="grandparent"),
    path("<uuid:player>/parents/<uuid:parent>/grandparent/<uuid:pk>", players.grandparent_edit, name="grandparent"),
]

urlpatterns = [
    path("", views.index, name="index"),
    path("players", players.PlayerList.as_view(), name="players"),
    path("players/", include(player_urls)),
    path("nation", nations.declaration_list, name="nations"),
]
