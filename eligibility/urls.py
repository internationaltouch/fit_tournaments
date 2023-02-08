from django.urls import path

from eligibility import views

urlpatterns = [
    path("", views.index, name="index"),
    path("players", views.PlayerList.as_view(), name="players"),
    path("players/create", views.player_create, name="player"),
    path("players/<uuid:pk>", views.player_edit, name="player"),
    path("players/<uuid:player>/declarations/create", views.PlayerDeclarationCreate.as_view(), name="declaration"),
    path("players/<uuid:player>/declarations/<uuid:pk>", views.PlayerDeclarationView.as_view(), name="declaration"),
    path("players/<uuid:player>/parents/create", views.parent_edit, name="parent"),
    path("players/<uuid:player>/parents/<uuid:pk>", views.parent_edit, name="parent"),
    path("players/<uuid:player>/parents/<uuid:parent>/grandparent/create", views.GrandParentCreate.as_view(), name="grandparent"),
    path("players/<uuid:player>/parents/<uuid:parent>/grandparent/<uuid:pk>", views.GrandParentEdit.as_view(), name="grandparent"),
]
