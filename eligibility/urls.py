from django.urls import path

from eligibility import views

urlpatterns = [
    path("", views.index, name="index"),
    path("players", views.PlayerList.as_view(), name="players"),
    path("players/create", views.PlayerCreate.as_view(), name="player"),
    path("players/<uuid:pk>", views.PlayerDetail.as_view(), name="player"),
    path("players/declarations/<uuid:pk>", views.PlayerDeclarationView.as_view(), name="declaration"),
]
