# Generated by Django 3.2.13 on 2022-05-25 07:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('probes', '0012_auto_20220329_0643'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feed',
            name='url',
        ),
    ]
