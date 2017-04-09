# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-07 14:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('excurj', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='city',
            options={'verbose_name_plural': 'Cities'},
        ),
        migrations.RemoveField(
            model_name='city',
            name='id',
        ),
        migrations.AddField(
            model_name='city',
            name='city_id',
            field=models.CharField(default='new', max_length=150, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='city',
            name='description',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='city',
            name='name',
            field=models.CharField(max_length=128),
        ),
    ]
