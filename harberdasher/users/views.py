import os
from PIL import Image
from random import shuffle

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings as django_settings

from .models import Profile, Tag
from harberdasher.chat.models import Room, CafeRoom, JoinedUser

from .forms import SignUpForm, LoginForm, ProfileForm, ChangePasswordForm

ACTIVE = 'A'

@login_required
def profile(request, username):
    uploaded_picture = False
    try:
        if request.GET.get('upload_picture') == 'uploaded':
            uploaded_picture = True

    except Exception, e:
        pass

    user = request.user
    rooms = JoinedUser.objects.filter(room__label__startswith='private').filter(user=user)

    count = 0
    for room in rooms:
        count += room.get_unread_count

    page_user = get_object_or_404(User, username=username)
    tags = Tag.objects.filter(user=page_user).filter(status=ACTIVE)
    return render(request, 'users/profile.html', {
        'tags': tags,
        'page_user': page_user,
        'count': count,
        'uploaded_picture': uploaded_picture
        })


@login_required
def settings(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            user.profile.sex = form.cleaned_data.get('sex')
            user.profile.birthdate = form.cleaned_data.get('birthdate')
            user.profile.location = form.cleaned_data.get('location')
            user.save()
            interests = form.cleaned_data.get('interests')
            user.create_or_update_tags(interests)
            messages.add_message(request, messages.SUCCESS,
                                 'Your profile was successfully edited.')

            return redirect('profile', user)
    else:
        tags = ''
        for tag in user.get_tags():
            tags = u'{0} {1}'.format(tags, tag.tag)
        tags = tags.strip()
        form = ProfileForm(instance=user, initial={
            'sex': user.profile.sex,
            'birthdate': user.profile.birthdate,
            'location': user.profile.location,
            'interests': tags,
            })
    return render(request, 'users/settings.html', {'form': form})


@login_required
def password(request):
    user = request.user
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            user.set_password(new_password)
            user.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Your password was successfully changed.')

    else:
        form = ChangePasswordForm(instance=user)

    return render(request, 'users/password.html', {'form': form})


@login_required
def upload_picture(request):
    try:
        profile_pictures = django_settings.MEDIA_ROOT + '/profile_pictures/'
        if not os.path.exists(profile_pictures):
            os.makedirs(profile_pictures)
        f = request.FILES['picture']
        filename = profile_pictures + request.user.username + '_tmp.png'
        with open(filename, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        im = Image.open(filename)
        width, height = im.size
        if width > 350:
            new_width = 350
            new_height = (height * 350) / width
            new_size = new_width, new_height
            im.thumbnail(new_size, Image.ANTIALIAS)
            im.save(filename)

        return redirect('/users/' + request.user.username + '/?upload_picture=uploaded')

    except Exception, e:
        print e
        return redirect('/users/' + request.user.username)


@login_required
def save_uploaded_picture(request):
    try:
        x = int(request.POST.get('x'))
        y = int(request.POST.get('y'))
        w = int(request.POST.get('w'))
        h = int(request.POST.get('h'))
        tmp_filename = django_settings.MEDIA_ROOT + '/profile_pictures/' + request.user.username + '_tmp.png'
        filename = django_settings.MEDIA_ROOT + '/profile_pictures/' + request.user.username + '.png'
        im = Image.open(tmp_filename)
        cropped_im = im.crop((x, y, w+x, h+y))
        cropped_im.thumbnail((200, 200), Image.ANTIALIAS)
        cropped_im.save(filename)
        os.remove(tmp_filename)
        messages.add_message(request, messages.SUCCESS,
                             'Your picture was successfully edited.')

    except Exception, e:
        pass

    return redirect('/users/' + request.user.username)

    # return redirect('home')


@login_required
def tag(request, tag_name):
    tags = Tag.objects.filter(tag=tag_name).filter(status=ACTIVE)
    users = []
    for tag in tags:
        users.append(tag.user)
    popular_tags = Tag.get_popular_tags()
    return render(request, 'users/tag.html',
        {
            'tag_name': tag_name,
            'users': users,
            'popular_tags': popular_tags
        })


@login_required
def tags(request):
    tags = Tag.objects.filter(status=ACTIVE)
    count = {}

    for tag in tags:
        if tag.tag in count:
            count[tag.tag] = count[tag.tag] + 1
        else:
            count[tag.tag] = 1

    max_count = sorted(count.items(), key=lambda t: t[1], reverse=True)[0][1]

    for key, value in count.iteritems():
        new_value = value * 128 / max_count
        count.update({key: new_value})

    shuffled_tags = count.items()
    shuffle(shuffled_tags)

    return render(request, 'users/tags.html',
        {
            'shuffled_tags': shuffled_tags,
        })


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if not form.is_valid():
            return render(request, 'users/signup.html',
                {'form': form})

        else:
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            User.objects.create_user(username=username, password=password,
                                     email=email)
            user = authenticate(username=username, password=password)
            login(request, user)

            return redirect('/')

    else:
        return render(request, 'users/signup.html',
            {'form': SignUpForm()})


def user_login(request):
    if request.user.is_authenticated():
        return redirect('home')

    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            next = request.POST.get('next')

            user = authenticate(username=username, password=password)

            if user is not None and user.is_active:
                login(request, user)
                return redirect(next)
            else:
                next = request.POST.get('next')
                form.errors.setdefault("username","cannot login")
                return render(request, 'users/login.html',
                    {'form': form, 'next': next,})
        else:
            next = request.POST.get('next')
            return render(request, 'users/login.html',
                {'form': form, 'next': next,})

    else:
        next = request.GET.get('next', '/')
        return render(request, 'users/login.html',
            {'form': LoginForm(),
            'next': next,})
