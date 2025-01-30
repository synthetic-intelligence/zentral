# Generated by Django 4.2.8 on 2024-02-06 22:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mdm', '0072_softwareupdateenforcement_platforms_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='softwareupdate',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='softwareupdate',
            name='build',
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AlterUniqueTogether(
            name='softwareupdate',
            unique_together={('platform',
                              'major', 'minor', 'patch', 'extra', 'build',
                              'prerequisite_build', 'public', 'availability')},
        ),
    ]
