# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-17 09:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('excurj', '0040_auto_20170516_2105'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestReference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('traveler_desc', models.CharField(blank=True, max_length=500)),
                ('local_desc', models.CharField(blank=True, max_length=500)),
                ('traveler_fun', models.BooleanField()),
                ('local_fun', models.BooleanField()),
                ('request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='excurj.Request')),
            ],
            options={
                'get_latest_by': 'request.id',
            },
        ),
        migrations.RemoveField(
            model_name='reference',
            name='author',
        ),
        migrations.RemoveField(
            model_name='reference',
            name='referenced',
        ),
        migrations.DeleteModel(
            name='Reference',
        ),
    ]