# Generated by Django 4.1.9 on 2023-09-04 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realms', '0008_realmgroupmapping_separator'),
    ]

    operations = [
        migrations.AddField(
            model_name='realm',
            name='custom_attr_1_claim',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='realm',
            name='custom_attr_2_claim',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='realmuser',
            name='custom_attr_1',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='realmuser',
            name='custom_attr_2',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
