from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

import markdown2

from .models import Experiment, Question, SurveyQuestion, Participant
from .forms import ParticipantForm, QuestionForm


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
        print(str(form))
        try:
            next_question = questions.pop(0)
        except IndexError:
            next_question = 0
    else:
        form = ParticipantForm()

    # questions = [Question.objects.get(id=question_id) for question_id in experiment.question_order]
    #
    # survey_questions = list()
    # for page in experiment.survey_question_order:
    #     survey_questions.append(
    #         [survey_questions.append(SurveyQuestion.objects.get(id=survey_question_id)) for survey_question_id in page]
    #     )
    print(str(form))

    if form.is_valid():
        request.session['name'] = form.cleaned_data['name']
        request.session['participant_id'] = form.cleaned_data['participant_id']

    request.session['questions'] = questions
    request.session['survey_questions'] = experiment.survey_question_order
    request.session['check_answers'] = experiment.check_answers

    return render(request, 'experiment.html',
                  {"form": form,
                   "consent_form": markdown2.markdown(experiment.consent_form),
                   "instructions": markdown2.markdown(experiment.instructions),
                   "consent_form_display": consent_form_display,
                   "instructions_display": instructions_display,
                   "next_question": next_question})
                  # {"questions": questions,
                  #  "survey_questions": survey_questions,
                  #  "consent_form": experiment.consent_form,
                  #  "check_answers": experiment.check_answers})


def question(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        raise Http404(_("Question %d not found." % question_id))

    try:
        next_question = request.session['questions'].pop(0)
    except IndexError:
        next_question = 0

    # consent_form_display = 'block'
    # instructions_display = 'none'
    #
    # if request.method == 'POST':
    #     form = ParticipantForm(request.POST)
    #     consent_form_display = 'none'
    #     instructions_display = 'block'
    #     print(str(form))
    #     try:
    #         next_question = questions.pop(0)
    #     except IndexError:
    #         next_question = 0
    # else:
    #     form = ParticipantForm()
    #
    # # questions = [Question.objects.get(id=question_id) for question_id in experiment.question_order]
    # #
    # # survey_questions = list()
    # # for page in experiment.survey_question_order:
    # #     survey_questions.append(
    # #         [survey_questions.append(SurveyQuestion.objects.get(id=survey_question_id)) for survey_question_id in page]
    # #     )
    # print(str(form))

    # if form.is_valid():
    #     request.session['name'] = form.cleaned_data['name']
    #     request.session['participant_id'] = form.cleaned_data['participant_id']

    form = QuestionForm()

    # request.session['survey_questions'] = experiment.survey_question_order
    # request.session['check_answers'] = experiment.check_answers

    return render(request, 'question.html',
                  {"form": form,
                   "pre_text": markdown2.markdown(question.pre_text),
                   "code": markdown2.markdown(question.code),
                   "post_text": markdown2.markdown(question.post_text),
                   "next_question": next_question})
    # {"questions": questions,
    #  "survey_questions": survey_questions,
    #  "consent_form": experiment.consent_form,
    #  "check_answers": experiment.check_answers})


