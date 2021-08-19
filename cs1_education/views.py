from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the CS1 education index!")


def consent_form(request):
    consent_question = ""

