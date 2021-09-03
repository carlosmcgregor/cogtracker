from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib import messages


import re


import markdown2

from .models import Experiment, Question, SurveyQuestion, Participant
from .forms import ParticipantForm, QuestionForm


def replace_linebreaks(text, double=True):
    linebreaks = '\n\n' if double else '\n'

    return text.replace('\\n', linebreaks)


def markdown(text, *args, **kwargs):
    return markdown2.markdown(replace_linebreaks(text), *args, **kwargs)


def index(request):
    return HttpResponse("You're at the CS1 education index! Please use the provided experiment link.")


@csrf_exempt
def experiment(request, experiment_id):
    try:
        experiment = Experiment.objects.get(id=experiment_id)
    except Experiment.DoesNotExist:
        raise Http404(_("Experiment %d not found." % experiment_id))

    questions = experiment.question_order
    next_question = 0
    consent_form_display = 'block'
    instructions_display = 'none'

    if request.method == 'POST':
        form = ParticipantForm(request.POST)
        consent_form_display = 'none'
        instructions_display = 'block'
        try:
            next_question = questions.pop(0)
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
    request.session['question_count'] = 0
    request.session['hint_timeout'] = experiment.hint_timeout
    request.session['experiment_id'] = experiment_id
    instructions = experiment.instructions

    if experiment.check_answers:
        instructions += '\n\n_Your answers will be automatically compared against the correct answer._'

    return render(request, 'experiment.html',
                  {"form": form,
                   "consent_form": markdown(experiment.consent_form),
                   "instructions": markdown(experiment.instructions),
                   "consent_form_display": consent_form_display,
                   "instructions_display": instructions_display,
                   "next_question": next_question})


def question(request, question_id):
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

    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        raise Http404(_("Question %d not found." % question_id))

    question_count = request.session["question_count"] + 1
    hint_timeout = request.session.get('hint_timeout') or 60000

    print(request)

    if request.method == 'POST':
        form = QuestionForm(request.POST)

        if request.session['check_answers']:
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
                    messages.info(request, 'Wrong answer!')
                else:
                    return redirect('../s/')
            else:
                print("Form is invalid!")
    else:
        try:
            request.session['next_question'] = request.session['questions'].pop(0)
        except IndexError:
            request.session['next_question'] = 0

        form = QuestionForm()

    return render(request, 'question.html',
                  {"form": form,
                   "pre_text": markdown(question.pre_text),
                   "code": replace_linebreaks(question.code, double=False),
                   "post_text": markdown(question.post_text),
                   "next_question": request.session['next_question'],
                   "question_id": question_id,
                   "question_count": question_count,
                   "hints": question.hints,
                   "hint_timeout": hint_timeout})


@csrf_exempt
def survey(request):
    surveys = list()

    if request.method == 'POST':
        # TODO: Add survey data recording
        print(request.POST)
        # return redirect('../q/' + str(request.session['next_question']))
        return HttpResponse(status=204)

    for i, page in enumerate(request.session['survey_questions']):
        surveys.append(list())
        for survey_id in page:
            surveys[i].append(SurveyQuestion.objects.get(id=survey_id))

    return render(request, 'survey.html',
                  {"surveys": surveys,
                   "next_question": request.session['next_question']})

