from django.conf.urls import include, url
from django.contrib import admin
from . import views


urlpatterns = [
    url(r'^$',  views.about, name='home'),
    url(r'^supers3cret4dm1n/', include(admin.site.urls)),
    url(r'^save-starbucks/$', views.save_starbucks, name='save_starbucks'),
    # url(r'^get-unreads/$', views.get_unreads, name='get_unreads'),
    # url(r'^starbucks/random/$', views.random_room, name='random_room'),
    # url(r'^starbucks/(?P<label>[\w-]{,50})/$', views.starbucks_room, name='starbucks_room'),
    url(r'^private/$', views.private_room, name='private_room'),
    url(r'^private-room-list/$', views.private_room_list, name='private_room_list'),

]
