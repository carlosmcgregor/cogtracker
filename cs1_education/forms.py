from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML


class ParticipantForm(forms.Form):
    name = forms.CharField(max_length=200, label="Your name", required=True)
    participant_id = forms.IntegerField(required=True, label="Your participant ID")
    helper = FormHelper()
    helper.layout = Layout(
            Fieldset(
                "",
                HTML(
                    """<h6>Please fill the following and press "Next" to accept:</h6>"""
                ),
                'name',
                'participant_id',
                HTML(
                    """</br>"""
                )
            ),
            ButtonHolder(
                Submit('submit', 'Next', css_class='button white')
            )
    )


class QuestionForm(forms.Form):
    answer =  forms.CharField(widget=forms.Textarea(attrs={"rows": 3, "cols": 60}), label="")
                              # label='Please write your answer below and click "Next" when done:')
    helper = FormHelper()
    helper.layout = Layout(
        Fieldset(
            "",
            HTML(
                """<h6>Please write your answer below (in multiple lines if the answer includes multiple lines of code):</h6>"""
            ),
            'answer',
            HTML(
                """</br>"""
            )
        ),
        ButtonHolder(
            Submit('submit', 'Submit', css_class='button white')
        )
    )
