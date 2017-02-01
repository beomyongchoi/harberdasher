from django.contrib import admin
from .models import Room, CafeRoom, Message, JoinedUser

class CafeRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'mapx', 'mapy')
    search_fields = ['name', 'label']

class JoinedUserAdmin(admin.ModelAdmin):
    list_display = ('room', 'user')
    search_fields = ['room', 'user']

admin.site.register(Room)
admin.site.register(Message)
admin.site.register(CafeRoom, CafeRoomAdmin)
admin.site.register(JoinedUser, JoinedUserAdmin)
