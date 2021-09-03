from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:experiment_id>/', views.experiment, name="experiment"),
    path('q/<int:question_id>', views.question, name="question"),
    path('s/', views.survey, name="survey")
]
