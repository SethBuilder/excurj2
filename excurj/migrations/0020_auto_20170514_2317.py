# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-14 20:17
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('excurj', '0019_auto_20170514_2304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reference',
            name='date',
            field=models.DateField(default=datetime.datetime(2017, 5, 14, 23, 17, 37, 507081)),
        ),
    ]