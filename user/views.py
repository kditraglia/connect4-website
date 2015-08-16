from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse_lazy

from game.models import Game

import json
from django.http import HttpResponse
from django.core import serializers

@login_required
def get_user_news(request):
    my_games = Game.objects.games_for_user(request.user)
    active_games = my_games.filter(status="A")
    finished_games = serializers.serialize("json", my_games.exclude(status="A"))
    waiting_games = serializers.serialize("json", active_games.filter(next_to_move=request.user))
    other_games = serializers.serialize("json", active_games.exclude(next_to_move=request.user))
    invitations = serializers.serialize("json", request.user.invitations_received.all())
    
    response_data = {'other_games': other_games,
                'waiting_games': waiting_games,
                'finished_games': finished_games,
                'invitations': invitations}
    
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@login_required
def home(request):
    my_games = Game.objects.games_for_user(request.user)
    active_games = my_games.filter(status="A")
    finished_games = my_games.exclude(status="A")
    waiting_games = active_games.filter(next_to_move=request.user)
    other_games = active_games.exclude(next_to_move=request.user)
    invitations = request.user.invitations_received.all()
    context = {'other_games': other_games,
                'waiting_games': waiting_games,
                'finished_games': finished_games,
                'invitations': invitations}
    return render(request, "user/home.html", context)

class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = "user/signup.html"
    success_url = reverse_lazy('user_home')
