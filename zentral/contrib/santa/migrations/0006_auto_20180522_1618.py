# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-05-22 16:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('santa', '0005_enrollment_santa_version'),
    ]

    operations = [
        migrations.RenameField(
            model_name='enrollment',
            old_name='santa_version',
            new_name='santa_release',
        ),
        migrations.AddField(
            model_name='enrollment',
            name='distributor_content_type',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='distributor_pk',
            field=models.PositiveIntegerField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='version',
            field=models.PositiveSmallIntegerField(default=1, editable=False),
        ),
        migrations.AlterField(
            model_name='enrollment',
            name='secret',
            field=models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE,
                                       related_name='%(app_label)s_%(class)s',
                                       to='inventory.enrollmentsecret'),
        ),
    ]
