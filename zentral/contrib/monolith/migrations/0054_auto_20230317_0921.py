# Generated by Django 3.2.14 on 2023-03-17 09:21

from django.db import migrations, models
import django.db.models.deletion
import zentral.contrib.monolith.models


class Migration(migrations.Migration):

    dependencies = [
        ('monolith', '0053_delete_submanifestattachment'),
    ]

    operations = [
        migrations.AddField(
            model_name='pkginfo',
            name='file',
            field=models.FileField(blank=True, upload_to=zentral.contrib.monolith.models.pkg_info_path),
        ),
        migrations.AddField(
            model_name='pkginfo',
            name='local',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='pkginfo',
            name='name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='monolith.pkginfoname'),
        ),
        migrations.AlterField(
            model_name='pkginfo',
            name='requires',
            field=models.ManyToManyField(blank=True, related_name='required_by', to='monolith.PkgInfoName'),
        ),
        migrations.AlterField(
            model_name='pkginfo',
            name='update_for',
            field=models.ManyToManyField(blank=True, related_name='updated_by', to='monolith.PkgInfoName'),
        ),
    ]
