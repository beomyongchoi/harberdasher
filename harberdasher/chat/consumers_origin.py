import re
import json
import logging

from django.utils import timezone

from channels import Group
from channels.sessions import channel_session
from channels.auth import channel_session_user, channel_session_user_from_http

from .models import Room, JoinedUser


log = logging.getLogger(__name__)


@channel_session_user_from_http
def ws_connect(message):
    # Extract the room from the message. This expects message.path to be of the
    # form /chat/{label}/, and finds a Room if the message path is applicable,
    # and if the Room exists. Otherwise, bails (meaning this is a some othersort
    # of websocket). So, this is effectively a version of _get_object_or_404.
    try:
        log.debug('=-=-=-=%s=-=-=-=', message['path'])
        prefix, room_type, label = message['path'].decode('ascii').strip('/').split('/')
        if prefix == 'chat':
            log.debug('chat')
        elif prefix == 'alert':
            log.debug('alert')
            return
        else:
            log.debug('invalid ws path=%s', message['path'])
            return
        room = Room.objects.get(label=label)
    except ValueError:
        log.debug('invalid ws path=%s', message['path'])
        return
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return
    else:
        log.debug('chat connect room=%s client=%s:%s currentuser=%s',
            room.label, message['client'][0], message['client'][1], message.user)
        Group('chat-'+label, channel_layer=message.channel_layer).add(message.reply_channel)
        message.channel_session['room'] = room.label

        joined_user, created = room.users.get_or_create(user=message.user)
        if joined_user:
            joined_user.entry_time = timezone.now()
            joined_user.save()

        message['text'] = '{"flag":"enter"}'
        return ws_receive(message)


def ws_receive(message):
    # Look up the room from the channel session, bailing if it doesn't exist
    try:
        label = message.channel_session['room']
        room = Room.objects.get(label=label)
    except KeyError:
        log.debug('no room in channel_session')
        return ws_receive
    except Room.DoesNotExist:
        log.debug('recieved message, buy room does not exist label=%s', label)
        return

    # Parse out a chat message from the content text, bailing if it doesn't
    # conform to the expected message format.
    try:
        data = json.loads(message['text'])
    except ValueError:
        log.debug("ws message isn't json text=%s", text)
        return

    if data.has_key('flag'):
        if data['flag'] =='enter':
            log.debug("enter=%s", message.user)

            user_list = []
            for joined in room.users.all():
                if joined.is_active():
                    user_list.append({'user':joined.user.username, 'status':'active'})
                else:
                    user_list.append({'user':joined.user.username, 'status':'inactive'})
            data['list'] = user_list

            Group('chat-'+label, channel_layer=message.channel_layer).send({'text': json.dumps(data)})

        else:
            log.debug("exit=%s", message.user)
            data['exit_user'] = message.user.username
            Group('chat-'+label, channel_layer=message.channel_layer).send({'text': json.dumps(data)})

    else:
        data['user'] = message.user
        log.debug('chat message room=%s username=%s message=%s currentuser=%s',
            room.label, data['user'].username, data['message'], message.user)
        m = room.messages.create(**data)

        # See above for the note about Group
        Group('chat-'+label, channel_layer=message.channel_layer).send({'text': json.dumps(m.as_dict())})


@channel_session_user
def ws_disconnect(message):
    try:
        label = message.channel_session['room']
        room = Room.objects.get(label=label)
        Group('chat-'+label, channel_layer=message.channel_layer).discard(message.reply_channel)
    except (KeyError, Room.DoesNotExist):
        pass
    else:
        joined_user, created = room.users.get_or_create(user=message.user)
        if joined_user:
            joined_user.exit_time = timezone.now()
            joined_user.save()

        message['text'] = '{"flag":"exit"}'
        return ws_receive(message)
