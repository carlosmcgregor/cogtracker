# Generated by Django 3.2.5 on 2021-08-04 20:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.CharField(choices=[('F', 'Fall'), ('W', 'Winter'), ('S', 'Summer')], max_length=2)),
                ('school', models.CharField(choices=[('SG', 'St. George'), ('M', 'Mississauga'), ('SC', 'Scarborough')], max_length=11)),
                ('year', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Instructor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_name', models.CharField(max_length=100)),
                ('first_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('participant_code', models.IntegerField()),
                ('experiment_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('subsection', models.CharField(max_length=3)),
                ('text', models.TextField()),
                ('blooms_taxonomy', models.CharField(choices=[('K', 'Knowledge'), ('C', 'Comprehension'), ('A', 'Application'), ('An', 'Analysis'), ('S', 'Synthesis'), ('E', 'Evaluation')], max_length=13)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cs1_education.exam')),
            ],
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_order', models.JSONField()),
                ('consent_form', models.TextField()),
                ('questions', models.ManyToManyField(to='cs1_education.Question')),
            ],
        ),
        migrations.AddField(
            model_name='exam',
            name='instructor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cs1_education.instructor'),
        ),
    ]
