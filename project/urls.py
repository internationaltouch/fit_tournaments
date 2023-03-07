from django.contrib import admin
from django.urls import path, include

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path("", include("eligibility.urls")),
    path("", include("social_django.urls", namespace="social")),
    path("impersonate/", include("impersonate.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("userprofile.urls")),
    path("sentry-debug", trigger_error),
    path("__debug__/", include("debug_toolbar.urls")),
]
