# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-13 22:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('excurj', '0007_auto_20170414_0117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='what_will_you_show_visitors',
            field=models.CharField(blank=True, max_length=1000),
        ),
    ]
