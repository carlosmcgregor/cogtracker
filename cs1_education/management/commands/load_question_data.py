from csv import DictReader
from datetime import datetime

from django.core.management import BaseCommand
from django.db.utils import IntegrityError

from cs1_education.models import Question, SurveyQuestion, Experiment
from pytz import UTC

import json


DATETIME_FORMAT = '%m/%d/%Y %H:%M'

VACCINES_NAMES = [
    'Canine Parvo',
    'Canine Distemper',
    'Canine Rabies',
    'Canine Leptospira',
    'Feline Herpes Virus 1',
    'Feline Rabies',
    'Feline Leukemia'
]

ALREADY_LOADED_ERROR_MESSAGE = """
If you need to reload the question data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables."""


def UnicodeDictReader(utf8_data, **kwargs):
    csv_reader = DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        yield {key.encode('utf-8').decode('utf-8-sig'): value.encode('utf-8').decode('utf-8-sig')
               for key, value in row.items()}


class Command(BaseCommand):
    # Show this when the user types help
    help = "Loads data from question_data.csv into our Question model"

    def handle(self, *args, **options):
        # if Question.objects.exists() or SurveyQuestion.objects.exists() or Experiment.objects.exists():
        #     print('Some data already loaded... exiting.')
        #     print(ALREADY_LOADED_ERROR_MESSAGE)
        #     return
        print("Loading question data")
        for row in UnicodeDictReader(open('./question_data.csv')):
            if not row['ID']:
                continue
            if Question.objects.filter(
                    pre_text=row['Pre-Text'], post_text=row['Post-Text'], code=row['Code']
            ).count() != 0:
                continue
            question = Question()
            question.pre_text = row['Pre-Text']
            question.post_text = row['Post-Text']
            question.code = row['Code']
            question.blooms_taxonomy = row['Blooms Taxonomy']
            question.hints = json.loads(row['Hints'])
            question.answer = row['Answer']
            question.source = row['Source']
            # raw_submission_date = row['submission date']
            # submission_date = UTC.localize(
            #     datetime.strptime(raw_submission_date, DATETIME_FORMAT))
            try:
                question.save()
            except IntegrityError:
                continue

        print("Loading survey question data")
        for row in UnicodeDictReader(open('./survey_question_data.csv')):
            if not row['ID']:
                continue
            if SurveyQuestion.objects.filter(text=row['Text']).count() != 0:
                continue
            survey_question = SurveyQuestion()
            survey_question.text = row['Text']
            survey_question.scale = json.loads(row['Scale'])
            survey_question.scale_label = json.loads(row['Scale Label'])
            try:
                survey_question.save()
            except IntegrityError:
                continue

        print("Loading experiment data")
        for row in UnicodeDictReader(open('./experiment_data.csv')):
            if not row['ID']:
                continue
            question_order = json.loads(row['Question Order'])
            survey_question_order = json.loads(row['Survey Question Order'])
            check_answers = False
            if row['Check Answers'].startswith('T'):
                check_answers = True
            if Experiment.objects.filter(question_order=question_order, survey_question_order=survey_question_order,
                                         consent_form=row['Consent Form'], check_answers=check_answers).count() != 0:
                continue

            experiment = Experiment()
            experiment.question_order = question_order
            experiment.survey_question_order = survey_question_order
            experiment.consent_form = row['Consent Form']
            try:
                experiment.save()
            except IntegrityError:
                continue

            # raw_vaccination_names = row['vaccinations']
            # vaccination_names = [name for name in raw_vaccination_names.split('| ') if name]
            # for vac_name in vaccination_names:
            #     vac = Vaccine.objects.get(name=vac_name)
            #     pet.vaccinations.add(vac)
            # pet.save()
