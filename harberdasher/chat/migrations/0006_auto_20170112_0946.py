# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-12 00:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_auto_20170111_1834'),
    ]

    operations = [
        migrations.AddField(
            model_name='joineduser',
            name='entry_time',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='joineduser',
            name='exit_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
