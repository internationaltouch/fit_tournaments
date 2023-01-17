from django.template.response import TemplateResponse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from eligibility.models import Player, PlayerDeclaration


def index(request):
    return TemplateResponse(request, "eligibility/index.html")


class PlayerList(ListView):
    model = Player


class PlayerDetail(DetailView):
    model = Player


class PlayerDeclarationView(DetailView):
    model = PlayerDeclaration
