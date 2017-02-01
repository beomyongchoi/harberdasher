import re
import json
import logging

from django.utils import timezone

from channels import Channel, Group
from channels.sessions import channel_session
from channels.auth import channel_session_user, channel_session_user_from_http

from .models import Room, JoinedUser, Message


log = logging.getLogger(__name__)

### WebSocket handling ###


# This decorator copies the user from the HTTP session (only available in
# websocket.connect or http.request messages) to the channel session (available
# in all consumers with the same reply_channel, so all three here)
@channel_session_user_from_http
def ws_connect(message):
    # message.reply_channel.send({'accept': True})
    log.debug('ws_connect=%s', message['path'])
    # Initialise their session
    Group("user-%s" % message.user.username).add(message.reply_channel)
    # message.channel_session['rooms'] = []


# Unpacks the JSON in the received WebSocket frame and puts it onto a channel
# of its own with a few attributes extra so we can route it
# This doesn't need @channel_session_user as the next consumer will have that,
# and we preserve message.reply_channel (which that's based on)
def ws_receive(message):
    # All WebSocket frames have either a text or binary payload; we decode the
    # text part here assuming it's JSON.
    # You could easily build up a basic framework that did this encoding/decoding
    # for you as well as handling common errors.
    payload = json.loads(message['text'])
    payload['reply_channel'] = message.content['reply_channel']
    Channel("chat.receive").send(payload)


@channel_session_user
def ws_disconnect(message):
    log.debug("disconnect user=%s", message.user)
    try:
        Group("room-%s" % message.channel_session['rooms']).send({
            "text": json.dumps({
                "leave": message.channel_session['rooms'],
                "user": message.user.username,
            }),
        })
        Group("user-%s" % message.user.id).discard(message.reply_channel)
        Group("room-%s" % message.channel_session['rooms']).discard(message.reply_channel)
    except:
        pass
    # Unsubscribe from any connected rooms
    # for session_id in message.channel_session.get("rooms", set()):
    #     try:
    #         room = Room.objects.get(id=session_id)
    #         # Removes us from the room's send group. If this doesn't get run,
    #         # we'll get removed once our first reply message expires.
    #         Group("room-%s" % room.id).discard(message.reply_channel)
    #     except Room.DoesNotExist:
    #         pass

### Chat channel handling ###


# Channel_session_user loads the user out from the channel session and presents
# it as message.user. There's also a http_session_user if you want to do this on
# a low-level HTTP handler, or just channel_session if all you want is the
# message.channel_session object without the auth fetching overhead.
@channel_session_user
def chat_join(message):
    # Find the room they requested (by ID) and add ourselves to the send group
    # Note that, because of channel_session_user, we have a message.user
    # object that works just like request.user would. Security!
    try:
        room = Room.objects.filter(id__lte=message["room"]).last()
        message["room"] = room.id
    except Room.DoesNotExist:
        log.debug('ws room does not exist id=%s', id)
        return
    else:
        # OK, add them in. The websocket_group is what we'll send messages
        # to so that everyone in the chat room gets them.
        Group("room-%s" % room.id).add(message.reply_channel)
        # message.channel_session['rooms'] = list(set(message.channel_session['rooms']).union([room.id]))
        message.channel_session['rooms'] = room.id

        private, first, last = room.label.split('-')
        if private == 'private':
            if not (message.user.username == first or message.user.username == last):
                log.debug('get out')
                return

            joined_user, created = room.users.get_or_create(user=message.user)
            joined_user.entry_time = timezone.now()
            joined_user.save()

            user_list = []
            for joined in room.users.all():
                if joined.is_active():
                    user_list.append({'user':joined.user.username, 'status':'active'})
                else:
                    user_list.append({'user':joined.user.username, 'status':'inactive'})

            messages = Message.objects.filter(room=room).order_by('-timestamp')[0:50]
            messages_list = []
            for m in reversed(messages):
                messages_list.append(m.as_dict())

            Group("room-%s" % room.id).send({
                "text": json.dumps({
                    "join": room.id,
                    "title": room.name,
                    "list": user_list,
                    "user": message.user.username,
                    "private": messages_list,
                }),
            })
        else:
            joined_user, created = room.users.get_or_create(user=message.user)
            joined_user.entry_time = timezone.now()
            joined_user.save()

            user_list = []
            for joined in room.users.all():
                if joined.is_active():
                    user_list.append({'user':joined.user.username, 'status':'active'})
                else:
                    user_list.append({'user':joined.user.username, 'status':'inactive'})

            Group("room-%s" % room.id).send({
                "text": json.dumps({
                    "join": room.id,
                    "title": room.name,
                    "list": user_list,
                }),
            })


@channel_session_user
def chat_leave(message):
    try:
        room = Room.objects.get(id=message["room"])
    except Room.DoesNotExist:
        log.debug('ws room does not exist id=%s', id)
        return
    else:
        Group("room-%s" % room.id).discard(message.reply_channel)
        # message.channel_session['rooms'] = list(set(message.channel_session['rooms']).difference([room.id]))

        joined_user, created = room.users.get_or_create(user=message.user)
        if joined_user:
            joined_user.exit_time = timezone.now()
            joined_user.save()

        # Send a message back that will prompt them to close the room
        Group("room-%s" % room.id).send({
            "text": json.dumps({
                "leave": room.id,
                "user": message.user.username,
            }),
        })




@channel_session_user
def chat_send(message):
    # Check that the user in the room
    if int(message["room"]) != message.channel_session['rooms']:
        log.debug(message['room'])
        log.debug(message.channel_session['rooms'])
        return
    # Find the room they're sending to, check perms
    try:
        room = Room.objects.get(id=message["room"])
    except Room.DoesNotExist:
        log.debug('ws room does not exist id=%s', id)
        return
    else:
        # Send the message along
        # room.send_message(message["message"], message.user)
        m = room.messages.create(
            user=message.user,
            message=message["message"]
        )
        Group("room-%s" % room.id).send({"text": json.dumps(m.as_dict())})
                # 'user': message.user.username,
                # 'message': message["message"],
                # 'timestamp': timezone.now().astimezone(timezone.get_current_timezone()).strftime('%b %-d %-I:%M %p')

        private, first, last = room.label.split('-')
        if private == 'private':
            if first == message.user.username:
                Group("user-%s" % last).send({
                    "text": json.dumps({
                        'count': room.id
                    })
                })
            else:
                Group("user-%s" % first).send({
                    "text": json.dumps({
                        'count': room.id
                    })
                })
