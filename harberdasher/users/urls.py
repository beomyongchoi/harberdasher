from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^signup/$', views.signup, name='signup'),
    # url(r'^login/$', auth_views.login, {'redirect_if_logged_in': '/', 'template_name': 'users/login.html'}, name='login'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^password/$', views.password, name='password'),
    url(r'^upload_picture/$', views.upload_picture, name='upload_picture'),
    url(r'^save_uploaded_picture/$', views.save_uploaded_picture, name='save_uploaded_picture'),
    url(r'^(?P<username>[^/]+)/$', views.profile, name='profile'),
]
