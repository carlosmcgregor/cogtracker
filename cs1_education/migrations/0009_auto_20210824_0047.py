# Generated by Django 3.2.5 on 2021-08-24 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cs1_education', '0008_experiment_instructions'),
    ]

    operations = [
        migrations.RenameField(
            model_name='participant',
            old_name='participant_code',
            new_name='code',
        ),
        migrations.AddField(
            model_name='participant',
            name='name',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
