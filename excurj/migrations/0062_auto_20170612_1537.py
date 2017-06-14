# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-12 12:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('excurj', '0061_auto_20170612_1433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='local_approval',
            field=models.BooleanField(default=None),
        ),
        migrations.AlterField(
            model_name='requestreference',
            name='request',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='reference_request', serialize=False, to='excurj.Request'),
        ),
    ]
