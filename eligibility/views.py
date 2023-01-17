from django.template.response import TemplateResponse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from eligibility.forms import PlayerForm
from eligibility.models import Player, PlayerDeclaration


def index(request):
    return TemplateResponse(request, "eligibility/index.html")


class PlayerList(ListView):
    model = Player


class PlayerCreate(CreateView):
    model = Player
    form_class = PlayerForm


class PlayerEdit(UpdateView):
    model = Player


class PlayerDetail(DetailView):
    model = Player


class PlayerDeclarationView(DetailView):
    model = PlayerDeclaration
