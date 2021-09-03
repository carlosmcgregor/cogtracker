# Generated by Django 3.2.5 on 2021-08-18 23:01

import cs1_education.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cs1_education', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SurveyQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=200, unique=True)),
                ('scale', models.JSONField(default=list, validators=[cs1_education.models.validate_string_list])),
            ],
        ),
        migrations.RemoveField(
            model_name='experiment',
            name='questions',
        ),
        migrations.RemoveField(
            model_name='question',
            name='exam',
        ),
        migrations.RemoveField(
            model_name='question',
            name='number',
        ),
        migrations.RemoveField(
            model_name='question',
            name='subsection',
        ),
        migrations.AddField(
            model_name='experiment',
            name='survey_question_order',
            field=models.JSONField(default=list, validators=[cs1_education.models.validate_survey_question_order]),
        ),
        migrations.AddField(
            model_name='participant',
            name='interaction',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='participant',
            name='question_answers',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='participant',
            name='survey_question_answers',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='question',
            name='answer',
            field=models.TextField(default='.*'),
        ),
        migrations.AddField(
            model_name='question',
            name='hints',
            field=models.JSONField(default=list, validators=[cs1_education.models.validate_string_list]),
        ),
        migrations.AddField(
            model_name='question',
            name='source',
            field=models.TextField(default=str),
        ),
        migrations.AlterField(
            model_name='experiment',
            name='question_order',
            field=models.JSONField(default=list, validators=[cs1_education.models.validate_question_order]),
        ),
        migrations.AlterField(
            model_name='participant',
            name='experiment_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='cs1_education.experiment'),
        ),
        migrations.AlterField(
            model_name='question',
            name='text',
            field=models.TextField(unique=True),
        ),
        migrations.DeleteModel(
            name='Exam',
        ),
        migrations.DeleteModel(
            name='Instructor',
        ),
    ]