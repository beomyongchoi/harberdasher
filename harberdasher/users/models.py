#-*- coding: utf-8 -*-

from __future__ import unicode_literals

import urllib
import hashlib
import os.path

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db import models
from django.conf import settings


def create_or_update_tags(self, tags):
    tag_list = tags.strip().split(' ')
    existing_tags = Tag.objects.filter(user=self).filter(status='A')
    for existing_tag in existing_tags:
        if existing_tag.tag not in tag_list:
            existing_tag.status = 'I'
            existing_tag.save()
    for tag in tag_list:
        t, created = Tag.objects.get_or_create(tag=tag.lower(),
                                               user=self)
        if not created and t.status == 'I':
            t.status = 'A'
            t.save()

def get_tags(self):
    return Tag.objects.filter(user=self)

User.add_to_class('create_or_update_tags', create_or_update_tags)
User.add_to_class('get_tags', get_tags)

class Profile(models.Model):
    MALE = 'M'
    FEMALE = 'F'
    SEX_TYPES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        )

    GYEONGGI = 'G'
    GANGWON = 'A'
    CHUNGBUK = 'Q'
    CHUNGNAM = 'R'
    GYEONGBUK = 'Y'
    GYEONGNAM = 'Z'
    JEONBUK = 'K'
    JEONNAM = 'H'
    SEOUL = 'S'
    INCHEON = 'I'
    DAEJEON = 'D'
    SEJONG = 'O'
    DAEGU = 'P'
    BUSAN = 'B'
    GWANGJU = 'W'
    JEJU = 'J'
    LOCATION_TYPES = (
        (GYEONGGI, '경기도'),
        (GANGWON, '강원도'),
        (CHUNGBUK, '충청북도'),
        (CHUNGNAM, '충청남도'),
        (GYEONGBUK, '경상북도'),
        (GYEONGNAM, '경상남도'),
        (JEONBUK, '전라북도'),
        (JEONNAM, '전라남도'),
        (SEOUL, '서울'),
        (INCHEON, '인천'),
        (DAEJEON, '대전'),
        (SEJONG, '세종'),
        (DAEGU, '대구'),
        (BUSAN, '부산'),
        (GWANGJU, '광주'),
        (JEJU, '제주'),
    )

    user = models.OneToOneField(User)
    sex = models.CharField(max_length=1, choices=SEX_TYPES, null=True, blank=True)
    location = models.CharField(max_length=1, choices=LOCATION_TYPES, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    greeting_message = models.TextField(max_length=2000, null=True, blank=True)


    class Meta:
        db_table = 'auth_profile'

    def get_picture(self):
        no_picture = settings.MEDIA_URL + 'starbucks.png'
        try:
            filename = settings.MEDIA_ROOT + '/profile_pictures/' + self.user.username + '.png'
            picture_url = settings.MEDIA_URL + 'profile_pictures/' + self.user.username + '.png'
            if os.path.isfile(filename):
                return picture_url
            # else:
            #     gravatar_url = u'http://www.gravatar.com/avatar/{0}?{1}'.format(
            #         hashlib.md5(self.user.email.lower()).hexdigest(),
            #         urllib.urlencode({'d': no_picture, 's': '256'})
            #         )
            #     return gravatar_url

        except Exception, e:
            pass
        return no_picture

    def get_age(self):
        import datetime
        return int(datetime.date.today().year - self.birthdate.year + 1)

    def __str__(self):
        return self.user.username

    def get_location(self):
        return {
            'G': '경기도',
            'A': '강원도',
            'Q': '충청북도',
            'R': '충청남도',
            'Y': '경상북도',
            'Z': '경상남도',
            'K': '전라북도',
            'H': '전라남도',
            'S': '서울',
            'I': '인천',
            'D': '대전',
            'O': '세종',
            'P': '대구',
            'B': '부산',
            'W': '광주',
            'J': '제주',
        }[self.location]


class Tag(models.Model):
    ACTIVE = 'A'
    INACTIVE = 'I'
    TAG_STATUS = (
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
        )

    tag = models.CharField(max_length=50)
    user = models.ForeignKey(User)
    status = models.CharField(max_length=1, choices=TAG_STATUS, default=ACTIVE)

    class Meta:
        unique_together = (('tag', 'user'),)
        index_together = [['tag', 'user'], ]

    # def __str__(self):
    #     return self.tag

    @staticmethod
    def get_popular_tags():
        tags = Tag.objects.filter(status='A')
        count = {}
        for tag in tags:
            if tag.tag in count:
                count[tag.tag] = count[tag.tag] + 1
            else:
                count[tag.tag] = 1
        sorted_count = sorted(count.items(), key=lambda t: t[1], reverse=True)
        return sorted_count[:20]


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
