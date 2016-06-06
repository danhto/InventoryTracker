# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-06 19:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0002_auto_20160530_1656'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventory',
            name='pieces',
        ),
        migrations.AddField(
            model_name='inventory',
            name='dessicate',
            field=models.BooleanField(default='false'),
        ),
        migrations.AddField(
            model_name='inventory',
            name='label',
            field=models.CharField(choices=[(0, 'No Label'), (1, 'Has labels'), (2, 'Partially labelled')], default=0, max_length=1),
        ),
        migrations.AddField(
            model_name='inventory',
            name='standard',
            field=models.BooleanField(default='true'),
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('DEX', 'Dextrose'), ('GUM', 'Gum')], default='DEX', max_length=3),
        ),
        migrations.AddField(
            model_name='product',
            name='pieces',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='weight',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
            preserve_default=False,
        ),
    ]