from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib import messages


import re
import random
import json


import markdown2

from .models import Experiment, Question, SurveyQuestion, Participant
from .forms import ParticipantForm, QuestionForm


def replace_linebreaks(text, double=True):
    linebreaks = '\n\n' if double else '\n'

    return text.replace('\\n', linebreaks)


def markdown(text, double=None, *args, **kwargs):
    if double is None:
        double = False
        if text.find("```") != -1:
            print("Using double lines")
            double = True

    return markdown2.markdown(replace_linebreaks(text, double=double),
                              extras=['fenced-code-blocks'],
                              *args,
                              **kwargs).replace("code>", "pre>")


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

    questions = experiment.question_order
    if experiment.random_questions:
        questions = randomize_list(questions)

    next_question = 0
    consent_form_display = 'block'
    instructions_display = 'none'

    if request.method == 'POST':
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

    request.session['questions'] = questions
    request.session['survey_questions'] = experiment.survey_question_order
    request.session['check_answers'] = experiment.check_answers
    request.session['hint_timeout'] = experiment.hint_timeout
    request.session['experiment_id'] = experiment_id
    request.session['on_question'] = False
    instructions = experiment.instructions

    if experiment.check_answers:
        instructions += '\n\n_Your answers will be automatically compared against the correct answer._'

    return render(request, 'experiment.html',
                  {"form": form,
                   "consent_form": markdown(experiment.consent_form, double=True),
                   "instructions": markdown(experiment.instructions, double=True),
                   "consent_form_display": consent_form_display,
                   "instructions_display": instructions_display,
                   "next_question": next_question})


def question(request, question_id):
    # Check if question ID is 0, which is the farewell screen
    if question_id == 0:
        experiment_id = request.session.get("experiment_id") or -1
        print("Experiment ID: {}".format(experiment_id))

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

    questions = request.session.get("questions") or [str(question_id)]
    print(questions)
    question_index = questions.index(str(question_id))
    print("Question count: {}".format(question_index + 1))
    questions_remaining = len(questions[question_index:]) - 1
    hint_timeout = request.session.get('hint_timeout') or 60000
    check_answers = request.session.get('check_answers') if request.session.get('check_answers') is not None else True

    try:
        request.session['next_question'] = questions[question_index + 1]
    except IndexError:
        request.session['next_question'] = 0

    if request.method == 'POST':
        form = QuestionForm(request.POST)

        if check_answers:
            print("Checking answer...")
            if form.is_valid():
                print("Form validation successful!")
                given_answer = form.cleaned_data['answer']
                print("Given answer: %s" % given_answer)

                matches = re.findall(question.answer, given_answer)
                print(str(matches))
                print(question.answer)
                if not matches:
                    print("Adding message to request")
                    # messages.info(request, 'Wrong answer!')
                    message = "Wrong answer!"
                    return HttpResponse(json.dumps({'message': message}))
                else:
                    return redirect('../s/')
            else:
                print("Form is invalid!")
    else:
        form = QuestionForm()

    hints = [markdown(hint) for hint in question.hints]
    print(hints)

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
                   "hint_timeout": hint_timeout})


@csrf_exempt
def survey(request):
    surveys = list()
    request.session['on_question'] = False

    if request.method == 'POST':
        # TODO: Add survey data recording
        print(request.POST)
        # return redirect('../q/' + str(request.session['next_question']))
        return HttpResponse(status=204)

    for i, page in enumerate(request.session.get('survey_questions') or [[1, 2, 3, 4, 5]]):
        surveys.append(list())
        for survey_id in page:
            surveys[i].append(SurveyQuestion.objects.get(id=survey_id))

    return render(request, 'survey.html',
                  {"surveys": surveys,
                   "next_question": request.session['next_question']})

