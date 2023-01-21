from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse


@login_required
def profile(request):
    return TemplateResponse(request, "profile.html")
