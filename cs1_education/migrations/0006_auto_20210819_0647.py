# Generated by Django 3.2.5 on 2021-08-19 06:47

import cs1_education.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cs1_education', '0005_auto_20210819_0311'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='check_answers',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='surveyquestion',
            name='scale_label',
            field=models.JSONField(default=dict, validators=[cs1_education.models.validate_position_dict]),
        ),
        migrations.AlterField(
            model_name='surveyquestion',
            name='scale',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterUniqueTogether(
            name='experiment',
            unique_together={('question_order', 'survey_question_order', 'consent_form', 'check_answers')},
        ),
    ]
