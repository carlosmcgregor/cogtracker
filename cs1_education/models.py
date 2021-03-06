from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

import re

from six import string_types


def validate_question_order(value):
    if not isinstance(value, list):
        raise ValidationError(_("Expected a list. Got %(type) instead."), params={'type': str(type(value))})

    for item in value:
        if not isinstance(item, string_types):
            raise ValidationError(_("Expected a string. Got %(type) instead."), params={'type': str(type(item))})

        if Question.objects.filter(id=item).count() == 0:
            raise ValidationError(_("Invalid question: question %(question) does not exist"),
                                  params={'question': item})


def validate_survey_question_order(value):
    if not isinstance(value, list):
        raise ValidationError(_("Expected a list. Got %(type) instead."), params={'type': str(type(value))})

    for item in value:
        if not isinstance(item, list):
            raise ValidationError(_("Expected a list. Got %(type) instead."), params={'type': str(type(item))})

        for text in item:
            if not isinstance(text, string_types):
                raise ValidationError(_("Expected a string. Got %(type) instead."), params={'type': str(type(text))})

            if SurveyQuestion.objects.filter(id=text).count() == 0:
                raise ValidationError(_("Invalid question: question %(question) does not exist"),
                                      params={'question': text})


def validate_string_list(value):
    if not isinstance(value, list):
        raise ValidationError(_("Expected a list. Got %(type) instead."), params={'type': str(type(value))})

    for item in value:
        if not isinstance(item, string_types):
            raise ValidationError(_("Expected a string. Got %(type) instead."), params={'type': str(type(item))})


def validate_position_dict(value):
    if not isinstance(value, dict):
        raise ValidationError(_("Expected a dict. Got %(type) instead."), params={'type': str(type(value))})

    for key, value in value.items():
        if not key.isdigit():
            raise ValidationError(_("Expected a position number. Got %(key) instead."), params={'key': key})

        if not isinstance(value, string_types):
            raise ValidationError(_("Expected a string. Got %(type) instead."), params={'type': str(type(value))})


# def validate_question_order(value):
#     if not isinstance(value, list):
#         raise ValidationError(_("Expected a list. Got %(type) instead."), params={'type': str(type(value))})
#
#     KEYS = sorted(["school", "year", "semester", "number", "subsection"])
#
#     for item in value:
#         if not isinstance(item, dict):
#             raise ValidationError(_("Expected a dict. Got %(type) instead."), params={'type': str(type(item))})
#
#         sorted_keys = sorted(item.keys())
#         if not sorted_keys == KEYS:
#             raise ValidationError(
#                 _("Key errors. Expected %(expected_keys), got %(sorted_keys)."),
#                 params={"expected_keys": str(KEYS), "sorted_keys": str(sorted_keys)}
#             )


# class Instructor(models.Model):
#     last_name = models.CharField(max_length=100)
#     first_name = models.CharField(max_length=100)


# class Exam(models.Model):
#     SEMESTERS = (
#         ("F", "Fall"),
#         ("W", "Winter"),
#         ("S", "Summer")
#     )
#     SCHOOL = (
#         ("SG", "St. George"),
#         ("M", "Mississauga"),
#         ("SC", "Scarborough")
#     )
#     instructor = models.ForeignKey(Instructor, blank=False, on_delete=models.CASCADE)
#     semester = models.CharField(
#         max_length=max(len(cur_semester) for cur_semester in SEMESTERS), blank=False, choices=SEMESTERS
#     )
#     school =  models.CharField(max_length=max(len(cur_school[1]) for cur_school in SCHOOL), choices=SCHOOL)
#     year = models.IntegerField()


class Question(models.Model):
    BLOOMS = (
        ("K", "Knowledge"),
        ("C", "Comprehension"),
        ("A", "Application"),
        ("An", "Analysis"),
        ("S", "Synthesis"),
        ("E", "Evaluation")
    )
    # exam = models.ForeignKey(Exam, blank=False, on_delete=models.CASCADE)
    # number = models.IntegerField()
    # subsection = models.CharField(max_length=3)
    pre_text = models.TextField(blank=False, default=str)
    post_text = models.CharField(max_length=300, blank=False)
    code = models.TextField(blank=False, default=str)
    blooms_taxonomy = models.CharField(max_length=13, blank=False, choices=BLOOMS)
    hints = models.JSONField(validators=[validate_string_list], default=list)
    answer = models.TextField(blank=False, default=r".*")
    source = models.TextField(default=str)

    class Meta:
        unique_together = ('pre_text', 'post_text', 'code')


class SurveyQuestion(models.Model):
    text = models.CharField(max_length=200, blank=False, unique=True)
    customization_number = models.IntegerField(default=0)
    scale_labels = models.JSONField(validators=[validate_position_dict], default=dict)
    survey_type = models.CharField(max_length=30)

    @property
    def label_text(self):
        return self.create_label(self.text)

    @staticmethod
    def create_label(text):
        pattern = re.compile('[\W_]+')
        text = pattern.sub(' ', text)
        split_text = text.lower().split(' ')
        return '_'.join(split_text)

    @property
    def scale_keys(self):
        return sorted(list(self.scale_labels.keys()))

    @property
    def scale_values(self):
        return [self.scale_labels[key] for key in self.scale_keys if key != "Other"]

    @property
    def first_element_key(self):
        return self.scale_keys[0]

    @property
    def first_element_key_as_int(self):
        try:
            return int(self.first_element_key)
        except ValueError:
            return self.first_element_key

    @property
    def first_element(self):
        return self.scale_labels[self.first_element_key]

    @property
    def last_element_key(self):
        return self.scale_keys[-1]

    @property
    def last_element_key_as_int(self):
        try:
            return int(self.last_element_key)
        except ValueError:
            return self.last_element_key

    @property
    def last_element(self):
        return self.scale_labels[self.last_element_key]


    @property
    def matrix_columns(self):
        if self.survey_type != "matrix":
            return [{}]

        return [{"value": int(key), "text": value} for key, value in self.scale_labels["columns"].items()]

    @property
    def matrix_rows(self):
        if self.survey_type != "matrix":
            return [{}]

        sorted_keys = sorted(self.scale_labels.keys())
        sorted_keys.remove("columns")

        return [
            {"value": self.create_label(self.scale_labels[key]), "text": self.scale_labels[key]}
            for key in sorted_keys
        ]

    @property
    def has_other(self):
        return self.scale_labels.get("Other") is not None

    @property
    def other_label(self):
        return self.scale_labels.get("Other") or "Other"


class Experiment(models.Model):
    # questions = models.ManyToManyField(Question)
    question_order = models.JSONField(validators=[validate_question_order], default=list)
    survey_question_order = models.JSONField(validators=[validate_survey_question_order], default=list)
    preliminary_survey_question_order = models.JSONField(validators=[validate_survey_question_order], default=list)
    consent_form = models.TextField(blank=False)
    instructions = models.TextField(blank=False)
    farewell_message = models.TextField(default="Thank you for participating in this experiment.")
    check_answers = models.BooleanField(default=True)
    random_questions = models.BooleanField(default=True)
    hint_timeout = models.IntegerField(default=60000)

    class Meta:
        unique_together = ('question_order', 'survey_question_order', 'consent_form', 'check_answers')


class Participant(models.Model):
    code = models.IntegerField()
    name = models.CharField(max_length=200, blank=False)
    experiment_id = models.ForeignKey(Experiment, on_delete=models.SET_NULL, null=True)
    # Answers come in the form of a list of dicts
    # e.g. [{"question": "1", "answer": "25", "timestamp": "2021-04-01 15:00"}]
    question_answers = models.JSONField(default=list)

    # Answers come in the form of a list of dicts
    # e.g. [{"survey_question": "1", "answer": "5", "timestamp": "2021-04-01 15:00"}]
    survey_question_answers = models.JSONField(default=list)

    # Interactions come in the form of a list of dicts
    # e.g. [{"page": "question1", "timestamp": "2021-04-01 15:00", "mouse_x": "25", "mouse_y": "400", "key_press": "k"}]
    # interaction = models.JSONField(default=list)

    session_key = models.CharField(max_length=200, blank=False)
    consent = models.CharField(max_length=1000, blank=False, default=str)
    consent_timestamp = models.TimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    class Meta:
        unique_together = ('code', 'name', 'session_key', 'experiment_id')


class ParticipantActivity(models.Model):
    session_key = models.CharField(max_length=200, blank=False)
    url = models.CharField(max_length=200, blank=False)
    activity = models.JSONField(default=list)
