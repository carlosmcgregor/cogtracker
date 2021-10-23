from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.db.utils import IntegrityError
from django.shortcuts import redirect
from django.contrib import messages


import re
import random
import json
import time


import markdown2

from .models import Experiment, Question, SurveyQuestion, Participant, ParticipantActivity
from .forms import ParticipantForm, QuestionForm


def replace_linebreaks(text, double=True):
    linebreaks = '\n\n' if double else '\n'

    return text.replace('\\n', linebreaks)


def markdown(text, double=None, *args, **kwargs):
    # print("Original text:")
    # print(text)
    if double is None:
        double = False
        if text.find("```") != -1:
            # print("Using double lines")
            double = True

    change_code_tags = '<code>' not in text

    # print("Text without linebreaks:")
    text = replace_linebreaks(text, double=double)
    # print(text)

    markdown_text = markdown2.markdown(text,
                                       extras=['fenced-code-blocks'],
                                       *args,
                                       **kwargs)

    if change_code_tags:
        markdown_text = markdown_text.replace("code>", "pre>")

    return markdown_text


def randomize_list(l):
    randomized_l = list()

    while l:
        i = random.SystemRandom().randint(0, len(l) - 1)
        randomized_l.append(l.pop(i))

    return randomized_l


def index(request):
    return HttpResponse("You're at the CS1 education index! Please use the provided experiment link.")


@csrf_exempt
def experiment(request, experiment_id):
    try:
        experiment = Experiment.objects.get(id=experiment_id)
    except Experiment.DoesNotExist:
        raise Http404(_("Experiment %d not found." % experiment_id))

    # Create session if it does not exist
    if not request.session.exists(request.session.session_key):
        request.session.create()

    print(request.session.session_key)
    request.session["experiment_id"] = experiment_id

    questions = experiment.question_order
    if experiment.random_questions:
        questions = randomize_list(questions)

    next_question = 0
    consent_form_display = 'block'
    instructions_display = 'none'

    if request.method == 'POST':
        participant = Participant()
        form = ParticipantForm(request.POST)
        consent_form_display = 'none'
        instructions_display = 'block'

        try:
            next_question = questions[0]
        except IndexError:
            next_question = 0
    else:
        form = ParticipantForm()

    if form.is_valid():
        request.session['name'] = form.cleaned_data['name']
        request.session['participant_id'] = form.cleaned_data['participant_id']

        participant.name = form.cleaned_data['name']
        participant.code = form.cleaned_data['participant_id']
        participant.experiment_id = experiment
        participant.session_key = request.session.session_key
        participant.consent = experiment.consent_form
        try:
            participant.save()
        except IntegrityError:
            pass

    request.session['questions'] = questions
    request.session['survey_questions'] = experiment.survey_question_order
    request.session['preliminary_survey_questions'] = experiment.preliminary_survey_question_order
    request.session['check_answers'] = experiment.check_answers
    request.session['hint_timeout'] = experiment.hint_timeout
    request.session['experiment_id'] = experiment_id
    request.session['on_question'] = False
    request.session['next_question'] = next_question
    instructions = experiment.instructions

    if experiment.check_answers:
        instructions += '\n\n_Your answers will be automatically compared against the correct answer._'

    return render(request, 'experiment.html',
                  {"form": form,
                   "consent_form": markdown(experiment.consent_form, double=True),
                   "instructions": markdown(experiment.instructions, double=True),
                   "consent_form_display": consent_form_display,
                   "instructions_display": instructions_display,
                   "next_question": next_question,
                   "session_key": request.session.session_key})


@csrf_exempt
def preliminary_survey(request):
    surveys = list()
    request.session['on_question'] = False
    print(request.session.get("preliminary_survey_questions"))

    if request.method == 'POST':
        print("Getting survey data")
        cur_survey_answers = dict()
        cur_survey_answers["question_id"] = -1
        cur_survey_answers["timestamp"] = time.time()
        cur_survey_answers["survey_answers"] = json.loads(request.body)

        update_participant(request, survey_data=cur_survey_answers)

        # return redirect('../q/' + str(request.session['next_question']))
        return HttpResponse(status=202)

    for i, page in enumerate(request.session.get('preliminary_survey_questions') or [[1, 2, 3, 4, 5]]):
        surveys.append(list())
        for survey_id in page:
            surveys[i].append(SurveyQuestion.objects.get(id=survey_id))

    return render(request, 'preliminary_survey.html',
                  {"surveys": surveys,
                   "next_question": request.session.get('next_question') or 0,
                   "session_key": request.session.session_key})


def question(request, question_id):
    # Check if question ID is 0, which is the farewell screen
    if question_id == 0:
        experiment_id = request.session.get("experiment_id") or -1
        # print("Experiment ID: {}".format(experiment_id))

        try:
            experiment = Experiment.objects.get(id=experiment_id)
            farewell_message = experiment.farewell_message
        except Experiment.DoesNotExist:
            farewell_message = markdown("Thank you for participating in this experiment!")

        return render(request, 'thanks.html',
                      {"farewell_message": farewell_message})

    # Retrieve question
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        raise Http404(_("Question %d not found." % question_id))

    request.session["question_id"] = question_id
    questions = request.session.get("questions") or [str(question_id)]
    # print(questions)
    question_index = questions.index(str(question_id))
    # print("Question count: {}".format(question_index + 1))
    questions_remaining = len(questions[question_index:]) - 1
    hint_timeout = request.session.get('hint_timeout') or 5000
    check_answers = request.session.get('check_answers') if request.session.get('check_answers') is not None else True

    try:
        request.session['next_question'] = questions[question_index + 1]
    except IndexError:
        request.session['next_question'] = 0

    if request.method == 'POST':
        form = QuestionForm(request.POST)

        if check_answers:
            # print("Checking answer...")
            if form.is_valid():
                # print("Form validation successful!")
                given_answer = form.cleaned_data['answer']
                cur_answer = dict()
                cur_answer["question_id"] = request.session.get("question_id")
                cur_answer["timestamp"] = time.time()
                cur_answer["answer"] = given_answer

                update_participant(request, question_data=cur_answer)
                # print("Given answer: %s" % given_answer)

                matches = re.findall(question.answer, given_answer)
                # print(str(matches))
                # print(question.answer)
                if not matches:
                    # print("Adding message to request")
                    # messages.info(request, 'Wrong answer!')
                    return HttpResponse(json.dumps({'message': "Please try again.", 'success': False}))
                else:
                    return HttpResponse(json.dumps({'message': "Correct!", 'success': True}))
                    # return redirect('../s/')
            else:
                print("Form is invalid!")
    else:
        form = QuestionForm()

    hints = [markdown(hint) for hint in question.hints]
    # print(hints)

    return render(request, 'question.html',
                  {"form": form,
                   "pre_text": markdown(question.pre_text),
                   "code": replace_linebreaks(question.code, double=False),
                   "post_text": markdown(question.post_text),
                   "next_question": request.session['next_question'],
                   "question_id": question_id,
                   "question_count": question_index + 1,
                   "questions_remaining": questions_remaining,
                   "hints": hints,
                   "hint_timeout": hint_timeout,
                   "session_key": request.session.session_key})


def update_participant(request, survey_data=None, question_data=None):
    experiment_id = request.session["experiment_id"]
    experiment = Experiment.objects.get(id=request.session["experiment_id"])

    session_key = request.session.session_key
    participant_name = request.session['name']
    participant_id = request.session['participant_id']

    print("Looking for name={}, code={}, session key={}, experiment id={}".format(
        participant_name, participant_id, session_key, experiment_id
    ))
    participant = Participant.objects.get(code=participant_id, name=participant_name, session_key=session_key,
                                          experiment_id=experiment)
    survey_question_answers = participant.survey_question_answers
    question_answers = participant.question_answers

    Participant.objects.update_or_create(
        name=participant_name, code=participant_id, session_key=session_key, experiment_id=experiment,
        defaults={"survey_question_answers": (survey_question_answers + [survey_data])
                                             if survey_data is not None else survey_question_answers,
                  "question_answers": (question_answers + [question_data])
                                      if question_data is not None else question_answers})


@csrf_exempt
def survey(request):
    surveys = list()
    request.session['on_question'] = False

    if request.method == 'POST':
        print("Getting survey data")
        cur_survey_answers = dict()
        cur_survey_answers["question_id"] = request.session.get("question_id")
        cur_survey_answers["timestamp"] = time.time()
        cur_survey_answers["survey_answers"] = json.loads(request.body)

        update_participant(request, survey_data=cur_survey_answers)

        # return redirect('../q/' + str(request.session['next_question']))
        return HttpResponse(status=202)

    for i, page in enumerate(request.session.get('survey_questions') or [[1, 2, 3, 4, 5]]):
        surveys.append(list())
        for survey_id in page:
            surveys[i].append(SurveyQuestion.objects.get(id=survey_id))

    return render(request, 'survey.html',
                  {"surveys": surveys,
                   "next_question": request.session['next_question'],
                   "session_key": request.session.session_key})


@csrf_exempt
def activity(request):
    if request.method == 'POST':
        print("Getting Activity Data:")
        payload = json.loads(request.body)
        participant_activity = ParticipantActivity()
        participant_activity.session_key = payload["session_key"]
        participant_activity.url = payload["url"]
        participant_activity.activity = payload["activity"]
        participant_activity.save()
        return HttpResponse(status=202)
