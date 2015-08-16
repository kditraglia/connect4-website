from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.views.generic import ListView

from .models import Invitation, Game, Move
from .forms import InvitationForm, MoveForm

import json
from django.http import HttpResponse
from django.core import serializers

def home(request):
    if request.user.is_authenticated():
        return redirect('user/home')
    return render(request, "game/home.html")

class AllGamesList(ListView):
    model = Game

@login_required
def new_invitation(request):
    if request.method == 'POST':
        invitation = Invitation(from_user=request.user)
        form = InvitationForm(data=request.POST, instance=invitation)
        if form.is_valid():
            form.save()
            return redirect('user_home')
    else:
        form = InvitationForm()
    return render(request, "game/new_invitation.html", {'form': form})



@login_required
def accept_invitation(request, pk):
    invitation = get_object_or_404(Invitation, pk=pk)
    if not request.user == invitation.to_user:
        raise PermissionDenied
    if request.method == 'POST':
        if "accept" in request.POST:
            game = Game.objects.new_game(invitation)
            game.save()
            invitation.delete()
            return redirect(game)
        else:
            invitation.delete()
            return redirect('user_home')
    else:
        return render(request, "game/accept_invitation.html", {'invitation': invitation})

@login_required
def get_game_detail(request, pk):
    game = get_object_or_404(Game, pk=pk)
    response_data = {'game': serializers.serialize("json", [game]),
                     'board' : game.as_board()}
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@login_required
def game_detail(request, pk):
    game = get_object_or_404(Game, pk=pk)
    if game.is_users_move(request.user):
        return redirect('connect4_game_do_move', pk=pk)
    return render(request, "game/game_detail.html", {'game': game})

@login_required
def game_do_movejson(request, pk, x, y):
    game = get_object_or_404(Game, pk=pk)
    if not game.is_users_move(request.user):
        raise PermissionDenied

    move = Move()
    move.x = int(x)
    move.y = int(y)
    move.game = game
    move.by_first_player = True
    move.save()
    game.update_after_move(move)
    game.save()
  
    response_data = {'game': serializers.serialize("json", [game])}
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@login_required
def game_do_move(request, pk):
    game = get_object_or_404(Game, pk=pk)
    if not game.is_users_move(request.user):
        raise PermissionDenied
    context = {'game': game}
    if request.method == 'POST':
        form = MoveForm(data=request.POST, instance=game.create_move())
        context['form'] = form
        if form.is_valid():
            move = form.save()
            game.update_after_move(move)
            game.save()
            return redirect('connect4_game_detail', pk=pk)
    else:
        context['form'] = MoveForm()
    return render(request, "game/game_do_move.html", context )
