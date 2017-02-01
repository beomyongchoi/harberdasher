from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible


# def join_room(self, tags):
#     tags = tags.strip()
#     tag_list = tags.split(' ')
#     existing_tags = Tag.objects.filter(user=self)
#     for existing_tag in existing_tags:
#         if existing_tag.tag not in tag_list:
#             existing_tag.delete()
#     for tag in tag_list:
#         if tag:
#             t, created = Tag.objects.get_or_create(tag=tag.lower(),
#                                                    user=self)
#
def get_my_rooms(self):
    return JoinedUser.objects.filter(user=self).filter(room__label__icontains='starbucks')
    # return self.rooms.all()

# def get_my_private_rooms(self):
#     return Room.objects.filter(label__startswith='private').filter(label__icontains=self.username)

# User.add_to_class('join_room', join_room)
User.add_to_class('get_my_rooms', get_my_rooms)
# User.add_to_class('get_my_private_rooms', get_my_private_rooms)

@python_2_unicode_compatible
class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    label = models.SlugField(unique=True)

    def __str__(self):
        return self.label


class CafeRoom(Room):
    mapx = models.IntegerField()
    mapy = models.IntegerField()


@python_2_unicode_compatible
class Message(models.Model):
    user = models.ForeignKey(User, related_name='messages')
    room = models.ForeignKey(Room, related_name='messages')
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)


    def __str__(self):
        # return '{0},{1},{2},{3}'.format(self.message, self.user.username, self.formatted_timestamp, self.room)
        return '[{timestamp}] {user}: {message}'.format(**self.as_dict())

    @property
    def formatted_timestamp(self):
        return self.timestamp.astimezone(timezone.get_current_timezone()).strftime('%b %-d %-I:%M %p')

    def as_dict(self):
        return {'user': self.user.username, 'message': self.message, 'timestamp': self.formatted_timestamp}


@python_2_unicode_compatible
class JoinedUser(models.Model):
    user = models.ForeignKey(User, related_name='rooms')
    room = models.ForeignKey(Room, related_name='users')
    entry_time = models.DateTimeField(default=timezone.now, db_index=True)
    exit_time = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (('user', 'room'),)

    def is_active(self):
        if self.entry_time >= self.exit_time:
            return True

    def is_cafe(self):
        if self.room.caferoom:
            return True

    @property
    def get_unread_count(self):
        if not self.is_active():
            unread = Message.objects.filter(room=self.room).filter(timestamp__gt=self.exit_time)
            return len(unread)
        else:
            return 0

    def as_dict(self):
        return {'name': self.user.username, 'unread_count': self.get_unread_count, 'id': self.room.id}

    def __str__(self):
        return self.room.name
