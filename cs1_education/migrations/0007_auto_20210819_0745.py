# Generated by Django 3.2.5 on 2021-08-19 07:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cs1_education', '0006_auto_20210819_0647'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='consent',
            field=models.CharField(default=str, max_length=200),
        ),
        migrations.AddField(
            model_name='participant',
            name='consent_timestamp',
            field=models.TimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
