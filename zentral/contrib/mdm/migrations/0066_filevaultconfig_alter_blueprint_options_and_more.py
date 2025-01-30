# Generated by Django 4.1.9 on 2023-07-29 10:08

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mdm', '0065_depvirtualserver_default_enrollment'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileVaultConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
                ('escrow_location_display_name', models.CharField(max_length=256, verbose_name='PRK escrow location display name')),
                ('at_login_only', models.BooleanField(default=False, help_text='Do not ask for FileVault to be enabled at logout.', verbose_name='Defer enablement at login only')),
                ('bypass_attempts', models.IntegerField(default=-1, help_text='After this number, FileVault will have to be enabled at login.', validators=[django.core.validators.MinValueValidator(-1), django.core.validators.MaxValueValidator(9999)], verbose_name='Max bypass attempts at login')),
                ('show_recovery_key', models.BooleanField(default=False, help_text='Display the PRK to the user after FileVault is enabled.', verbose_name='Show recovery key')),
                ('destroy_key_on_standby', models.BooleanField(default=False, help_text='Force FileVault unlock after hibernation.', verbose_name='Destroy key on standby')),
                ('prk_rotation_interval_days', models.IntegerField(default=0, help_text='Interval in days after which the PRK will be automatically rotated and escrowed to Zentral.', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(366)], verbose_name='PRK rotation interval (days)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'filevault config',
            },
        ),
        migrations.AlterModelOptions(
            name='blueprint',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='enrolleddevice',
            options={'permissions': [('view_filevault_prk', 'Can view FileVault PRK')]},
        ),
        migrations.AddField(
            model_name='enrolleddevice',
            name='filevault_config_uuid',
            field=models.UUIDField(null=True),
        ),
        migrations.AddField(
            model_name='enrolleddevice',
            name='filevault_escrow_key',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='enrolleddevice',
            name='filevault_prk',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='enrolleddevice',
            name='filevault_prk_updated_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='blueprint',
            name='filevault_config',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mdm.filevaultconfig'),
        ),
    ]
