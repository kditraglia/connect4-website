from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from user.views import SignUpView

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'game.views.home', name='connect4_home'),
    url(r'^connect4/', include('game.urls')),
)

urlpatterns += patterns(
    'django.contrib.auth.views',
    
    url(r'^login/$', 'login',
        {'template_name': 'login.html'},
        name='connect4_login'),
    
    url(r'^logout/$', 'logout',
        {'next_page': r'/'},
        name='connect4_logout'),
)

urlpatterns += patterns('user.views',
                            url(r'^user/home$', 'home', name='user_home'),
                            url(r'^user/signup$', SignUpView.as_view(), name='user_signup'),
                            url(r'^user/get_info$', 'get_user_news'),
                        )
