from django.contrib import admin

from .models import Profile, Tag


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'sex', 'location')
    search_fields = ['location']

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Tag)
