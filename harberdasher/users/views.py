from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import Profile, Tag
from harberdasher.chat.models import Room, CafeRoom, JoinedUser

from harberdasher.users.forms import SignUpForm, ProfileForm


@login_required
def profile(request, username):
    user = request.user
    rooms = JoinedUser.objects.filter(room__label__startswith='private').filter(user=user)

    count = 0
    for room in rooms:
        count += room.get_unread_count

    page_user = get_object_or_404(User, username=username)
    tags = Tag.objects.filter(user=page_user)
    return render(request, 'users/profile.html', {
        'tags': tags,
        'page_user': page_user,
        'count': count
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
            # messages.add_message(request,
            #                      messages.SUCCESS,
            #                      'Your profile was successfully edited.')
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

@login_required
def tag(request, tag_name):
    tags = Tag.objects.filter(tag=tag_name)
    users = []
    for tag in tags:
        users.append(tag.user)
    return render(request, 'users/tag.html',
        {
            'tag': tag_name,
            'users': users,
        })

def custom_login(request):
    if request.method == 'POST':
        if request.user.is_authenticated():
            redirect('home')
        form = SignUpForm(request.POST)
        if not form.is_valid():
            return render(request, 'users/login.html',
                {'form': form})

        else:
            username = form.cleaned_data.get('username')
            # email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            # User.objects.create_user(username=username, password=password,
                                    #  email=email)
            user = authenticate(username=username, password=password)
            login(request, user)

            return redirect('/')

    else:
        return render(request, 'users/login.html',
            {'form': SignUpForm()})

    # if request.user.is_authenticated():
    #     redirect('home')
    # else:
    #     template_name = "users/login.html"
