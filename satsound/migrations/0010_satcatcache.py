# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-18 22:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('satsound', '0009_auto_20170409_0229'),
    ]

    operations = [
        migrations.CreateModel(
            name='SatCatCache',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('norad_id',
                 models.IntegerField(primary_key=True, serialize=False, verbose_name='NORAD catalog number')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
