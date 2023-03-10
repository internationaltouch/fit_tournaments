from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("eligibility.urls")),
    path("", include("social_django.urls", namespace="social")),
    path("impersonate/", include("impersonate.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("userprofile.urls")),
]
