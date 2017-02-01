# -*- coding: utf-8 -*-
import json
import urllib
import urllib2
import random
import string
import datetime

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from haikunator import Haikunator
from .models import Room, CafeRoom, JoinedUser


def about(request):
    starbucks = CafeRoom.objects.all()

    count = 0
    if request.user.is_authenticated():
        user = request.user
        rooms = JoinedUser.objects.filter(room__label__startswith='private').filter(user=user)

        for room in rooms:
            count += room.get_unread_count

    return render(request, "chat/about.html", {
        'list': starbucks,
        'count': count,
    })

# @login_required
# def get_unreads(request):
#     user = request.user
#     rooms = JoinedUser.objects.filter(room__label__startswith='private').filter(user=user)
#
#     count = 0
#     for room in rooms:
#         count += room.get_unread_count
#
#     return render(request, "chat/about.html", {
#         'list': starbucks,
#         'count': count,
#     })
#
# @login_required
# def new_room(request, username):
#     """
#     Randomly create a new room, and redirect to it.
#     """
#     new_room = None
#     while not new_room:
#         with transaction.atomic():
#             haikunator = Haikunator()
#             label = haikunator.haikunate()
#             name = label.replace('-', ' ')
#             if Room.objects.filter(label=label).exists():
#                 continue
#             new_room = Room.objects.create(name=name, label=label)
#     return redirect(chat_room, label=label)

# def _room(request, room):
#     joined_user, created = JoinedUser.objects.get_or_create(
#         user=request.user,
#         room=room,
#     )
#
#     return render(request, "chat/room.html", {
#         'room': room,
#     })
#
#
# @login_required
# def random_room(request):
#     random_id = random.randint(0,1000)
#     room = Room.objects.filter(id__lte=random_id).last()
#
#     joined_user, created = JoinedUser.objects.get_or_create(
#         user=request.user,
#         room=room,
#     )
#
#     return _room(request, room)
#
#
# @login_required
# def starbucks_room(request, label):
#     room, created = Room.objects.get_or_create(label=label)
#
#     return _room(request, room)


@login_required
def private_room(request):
    if request.method == 'POST':
        i = request.user.username
        you = request.POST.get('you')

        # if request.META.get('HTTP_REFERER'):
        #     prev = request.META.get('HTTP_REFERER')
        # else:
        #     prev = '/'

        if i == you:
            return JsonResponse({"error": "impossible"})

        # if not any(user == request.user.username for user in users) or users[0] == users[1]:
        #     return render(request, "chat/this-is-private.html", {
        #         'room':label,
        #         'prev':prev,
        #     })

        private = sorted([i, you])
        name = " ".join(str(x) for x in private).title()
        label = 'private-' + name.replace(' ','-').lower()

        room, created = Room.objects.get_or_create(
            name=name,
            label=label,
        )

        opposite_user = User.objects.get(username=you)
        if opposite_user is None:
            return JsonResponse({"error": "impossible"})

        now = timezone.now()
        yesterday = now - datetime.timedelta(days=1)

        try:
            obj = JoinedUser.objects.get(room=room, user=opposite_user)
        except JoinedUser.DoesNotExist:
            new_values = {
                'room': room,
                'user': opposite_user,
                'enter_time': yesterday,
                'exit_time': now
            }
            obj = Person(**new_values)
            obj.save()

        # messages = room.messages.order_by('timestamp')
        # message_list = list(messages)
        # for index, value in enumerate(message_list):
        #     message_list[index] = str(message_list[index]).strip('<').split(',')

        result = {
            "title": you.title(),
            "room": room.id,
            # "message": message_list,
        }
        return JsonResponse(result)
    else:
        return JsonResponse({"nothing to see": "this isn't happening"})


@login_required
def private_room_list(request):
    if request.method == 'POST':
        user = request.user
        rooms = JoinedUser.objects.filter(room__label__startswith='private').filter(user=user)

        room_list = []
        for x in rooms:
            room_list.append({
                'id': x.room.id,
                'name': x.room.label.replace(user.username,'').replace('private','').strip('-'),
                'unread_count': x.get_unread_count
            })

        # room = list(Room.objects.filter(label__startswith='nameless').values())
        # if len(room) is 0:
            # return JsonResponse({"room":None})

        return JsonResponse({
            "room":room_list,
        })
    else:
        return JsonResponse({"nothing to see": "this isn't happening"})


def save_starbucks(request):
    client_id = "pOK1vfqW3iwmGmewUghS"
    client_secret = "kBsI_gIGhC"
    text = u"스타벅스"
    encode_text = text.encode('utf-8')
    base_url = "https://openapi.naver.com/v1/search/local.json"

    start = 1
    count = 0
    result_list = []

    while True:
    	try:
    		url = base_url + '?' + urllib.urlencode({
    			'query': encode_text,
    			'display': 99,
    			'start': start,
    		})
    		request = urllib2.Request(url)
    		request.add_header('Content-Type', 'application/json')
    		request.add_header("X-Naver-Client-Id",client_id)
    		request.add_header("X-Naver-Client-Secret",client_secret)
    		response = urllib2.urlopen(request).read()
    	except Exception as e:
    		raise Exception(e)
    	else:
    		result = json.loads(response)
    		result_list += (result['items'])
    		start += 99
    		count += 99
    		if result['total'] <= count or start > 1000:
    			break

    haikunator = Haikunator(nouns=['starbucks'])
    for result in result_list:
    	if result['title'].startswith(u'<b>스타벅스</b> '):
            name = result['title'].replace(u'<b>스타벅스</b>', u'스타벅스')
            new_room = None
            if CafeRoom.objects.filter(name=name).exists():
                continue
            while not new_room:
                with transaction.atomic():
                    label = haikunator.haikunate()
                    if CafeRoom.objects.filter(label=label).exists():
                        continue
                    new_room, created = CafeRoom.objects.get_or_create(
                        name=name,
                        label=label,
                        mapx=result['mapx'],
                        mapy=result['mapy'])

    return redirect(about)
