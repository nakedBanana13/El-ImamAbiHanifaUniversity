from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import Question, Choice, Exam


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['module', 'question_text']

    def __init__(self, *args, question_bank=None, **kwargs):
        super().__init__(*args, **kwargs)
        if question_bank:
            self.fields['module'].queryset = question_bank.course.modules.all()


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text', 'is_correct']


class BaseChoiceFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        num_correct_choices = 0
        for form in self.forms:
            if form.cleaned_data.get('is_correct'):
                num_correct_choices += 1
        if num_correct_choices != 1:
            raise ValidationError("Exactly one choice must be marked as correct.")


ChoiceFormSet = inlineformset_factory(
    Question,
    Choice,
    form=ChoiceForm,
    fields=('choice_text', 'is_correct'),
    min_num=4,
    max_num=4,
    validate_min=True,
    validate_max=True,
    formset=BaseChoiceFormSet)


class ExamForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        question_bank = kwargs.pop('question_bank', None)
        super().__init__(*args, **kwargs)
        if question_bank:
            # Filter modules based on the question bank
            self.fields['modules'].queryset = question_bank.course.modules.all()

    class Meta:
        model = Exam
        fields = ['modules', 'number_of_questions', 'duration_minutes', 'scheduled_datetime', 'total_marks', 'lock_course_during_exam']
        widgets = {
            'modules': forms.CheckboxSelectMultiple(),
            'scheduled_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }


class ExamSubmissionForm(forms.Form):
    def __init__(self, exam_questions, *args, **kwargs):
        super(ExamSubmissionForm, self).__init__(*args, **kwargs)

        # Populate form fields dynamically based on exam questions
        for exam_question in exam_questions:
            # Get all choices for the current question
            choices = [(choice.id, choice.choice_text) for choice in exam_question.exam_choices.all()]
            question_text = exam_question.question.question_text
            self.fields[f'question_{exam_question.id}'] = forms.ChoiceField(label=question_text,
                                                                            choices=choices,
                                                                            widget=forms.RadioSelect)
