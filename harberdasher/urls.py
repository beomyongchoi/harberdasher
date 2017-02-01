from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import include, url
from harberdasher.users import views as harberdasher_users_views

urlpatterns = [
    url(r'', include('harberdasher.chat.urls')),
    url(r'^users/', include('harberdasher.users.urls')),
    url(r'^tag/(?P<tag_name>.+)/$', harberdasher_users_views.tag, name='tag'),
    url(r'^tags/$', harberdasher_users_views.tags, name='tags'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
