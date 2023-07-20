from django.urls import path

from accreditation import views

urlpatterns = [
    path(
        "accreditation",
        views.PlayerDeclarationSearchList.as_view(),
        name="accreditation",
    ),
    path(
        "accreditation/<uuid:pk>", views.PlayerDeclarationView.as_view(), name="verify"
    ),
]
