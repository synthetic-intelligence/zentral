# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-29 17:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monolith', '0022_auto_20170410_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pkginfo',
            name='update_for',
            field=models.ManyToManyField(related_name='updated_by', to='monolith.PkgInfoName'),
        ),
    ]
