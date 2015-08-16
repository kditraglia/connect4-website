from django.conf.urls import patterns, include, url

from .views import AllGamesList

urlpatterns = patterns('game.views',
    url(r'^invite$', 'new_invitation', name='connect4_invite'),
    url(r'^invitation/(?P<pk>\d+)/$', 'accept_invitation', name='connect4_accept_invitation'),
    url(r'^game/(?P<pk>\d+)/$', 'game_detail', name='connect4_game_detail'),
    url(r'^game/(?P<pk>\d+)/do_move$', 'game_do_move', name='connect4_game_do_move'),
    url(r'^game/all', AllGamesList.as_view()),
    url(r'^get_game/(?P<pk>\d+)/$', 'get_game_detail'),
    url(r'^game/(?P<pk>\d+)/game_do_movejson/(?P<y>\d+)/(?P<x>\d+)/$', 'game_do_movejson'),
)