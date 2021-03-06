# Generated by Django 3.2.5 on 2021-10-21 15:35

import cs1_education.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cs1_education', '0014_alter_participant_unique_together'),
    ]

    operations = [
        migrations.RenameField(
            model_name='surveyquestion',
            old_name='scale',
            new_name='customization_number',
        ),
        migrations.RenameField(
            model_name='surveyquestion',
            old_name='scale_label',
            new_name='scale_labels',
        ),
        migrations.AddField(
            model_name='experiment',
            name='preliminary_survey_question_order',
            field=models.JSONField(default=list, validators=[cs1_education.models.validate_survey_question_order]),
        ),
        migrations.AddField(
            model_name='surveyquestion',
            name='survey_type',
            field=models.CharField(default='rating', max_length=30),
            preserve_default=False,
        ),
    ]
