# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-15 03:31
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('satsound', '0006_auto_20161230_0403'),
    ]

    operations = [
        migrations.AlterField(
            model_name='satelliteaudio',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]